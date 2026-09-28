"""Controles op de gebouwde site in public/. Faalt (exitcode 1) als één controle faalt.

Gebruik:
    python build.py
    python tools/check.py

Controles (zie CLAUDE.md):
1. Geen externe resources en geen inline script, style of style="".
2. Geen interne dode links; elke oude URL geeft 200, 301 of 410.
3. Privacyfilter en verplichte velden over gepubliceerde uitrukken.
4. Aantal uitrukken per jaar 2008 t/m 2022 gelijk aan de legacy-telling.
5. Budgetten en maximale bestandsgrootte.
6. Alt-teksten, title en description, goed geneste HTML.
"""

import csv
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"
DATA = ROOT / "data"

# Zet op True zodra fase 3 (migratie) klaar is. Tot die tijd zijn de migratiecontroles
# (oude URL's die 200 moeten geven, en tellingen per jaar) alleen waarschuwingen.
MIGRATIE_KLAAR = True

# Telling uit legacy/content/JJJJ.md (fase 1, MIGRATIE.md).
LEGACY_TELLING = {2008: 95, 2009: 113, 2010: 119, 2011: 127, 2012: 112, 2013: 116, 2014: 104,
                  2015: 91, 2016: 106, 2017: 126, 2018: 124, 2019: 76, 2020: 98, 2021: 69, 2022: 52}
# Oude regels die bewust niet zijn overgenomen (oefening 2012, besluit Sven 28-09-2026),
# gelijk aan LEGACY_WEG in tools/migrate_hugo.py.
LEGACY_WEG = {2012: 1}

BUDGET_PAGINA = 100 * 1024   # HTML + CSS + JS per pagina
BUDGET_EERSTE_AFB = 150 * 1024
MAX_BESTAND = 300 * 1024     # afbeeldingen

VOID = {"area", "base", "br", "col", "embed", "hr", "img", "input", "link", "meta", "source", "track", "wbr"}
OPTIONEEL_SLUITEN = {"p", "li", "dt", "dd", "tr", "td", "th", "thead", "tbody", "option"}

fouten = []
waarschuwingen = []


def fout(tekst):
    fouten.append(tekst)


def extern(url):
    u = url.strip().lower()
    return u.startswith(("http:", "https:", "//"))


class Pagina(HTMLParser):
    def __init__(self, naam):
        super().__init__(convert_charrefs=True)
        self.naam = naam
        self.stapel = []
        self.links = []
        self.bronnen = []
        self.stylesheets = []
        self.scripts = []
        self.afbeeldingen = []
        self.titel = None
        self.in_titel = False
        self.beschrijving = None
        self.ids = set()

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if "style" in a:
            fout(f"{self.naam}: inline style=\"\" op <{tag}> (breekt de CSP)")
        if any(k.startswith("on") for k in a):
            fout(f"{self.naam}: inline event-handler op <{tag}>")
        if "id" in a:
            if a["id"] in self.ids:
                fout(f"{self.naam}: dubbele id '{a['id']}'")
            self.ids.add(a["id"])
        if tag in ("iframe", "object", "embed"):
            fout(f"{self.naam}: <{tag}> is niet toegestaan")
        if tag == "style":
            fout(f"{self.naam}: inline <style>")
        if tag == "script":
            if not a.get("src"):
                fout(f"{self.naam}: inline <script>")
            else:
                self.scripts.append(a["src"])
        rel = (a.get("rel") or "").split()
        if tag == "link" and "stylesheet" in rel:
            self.stylesheets.append(a.get("href", ""))
        elif tag == "link" and ("canonical" in rel or "alternate" in rel):
            # Verwijzingen, geen resources die de browser laadt.
            if not extern(a.get("href", "")):
                self.links.append(a.get("href", ""))
        elif tag == "link" and a.get("href"):
            self.bronnen.append(a["href"])
        if tag == "a" and a.get("href"):
            self.links.append(a["href"])
        for attr in ("src", "srcset", "poster"):
            if a.get(attr):
                for deel in a[attr].split(","):
                    self.bronnen.append(deel.strip().split(" ")[0])
        if tag == "img":
            if a.get("alt") is None:
                fout(f"{self.naam}: <img src=\"{a.get('src')}\"> zonder alt")
            if not (a.get("width") and a.get("height")):
                fout(f"{self.naam}: <img src=\"{a.get('src')}\"> zonder width/height")
            self.afbeeldingen.append(a.get("src", ""))
        if tag == "meta" and a.get("name") == "description":
            self.beschrijving = a.get("content")
        if tag == "title":
            self.in_titel = True
            self.titel = ""
        if tag not in VOID:
            self.stapel.append(tag)

    def handle_startendtag(self, tag, attrs):
        # <svg .../> en dergelijke: openen en direct sluiten.
        self.handle_starttag(tag, attrs)
        if tag not in VOID and self.stapel and self.stapel[-1] == tag:
            self.stapel.pop()

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_titel = False
        if tag in VOID:
            return
        while self.stapel and self.stapel[-1] != tag and self.stapel[-1] in OPTIONEEL_SLUITEN:
            self.stapel.pop()
        if not self.stapel or self.stapel[-1] != tag:
            fout(f"{self.naam}: onverwachte </{tag}> (open: {'/'.join(self.stapel[-3:])})")
            return
        self.stapel.pop()

    def handle_data(self, data):
        if self.in_titel:
            self.titel += data


def pad_voor(url):
    """Bestand in public/ voor een interne URL, of None."""
    pad = unquote(urlsplit(url).path)
    doel = PUBLIC / pad.lstrip("/")
    if pad.endswith("/"):
        doel = doel / "index.html"
    if doel.is_file():
        return doel
    if (doel / "index.html").is_file():
        return doel / "index.html"
    return None


def lees_htaccess():
    regels = {}
    tekst = (PUBLIC / ".htaccess").read_text(encoding="utf-8")
    for m in re.finditer(r'^RedirectMatch (301|410) "([^"]+)"(?: "([^"]+)")?$', tekst, re.M):
        regels[m.group(2)] = (m.group(1), m.group(3))
    return regels


def redirect_voor(regels, url):
    for patroon, (code, doel) in regels.items():
        if re.match(patroon, url):
            return code, doel
    return None


def controle_html():
    paginas = sorted(PUBLIC.rglob("*.html"))
    css_bestanden = {}
    for p in PUBLIC.rglob("*.css"):
        tekst = p.read_text(encoding="utf-8")
        css_bestanden["/" + p.relative_to(PUBLIC).as_posix()] = p.stat().st_size
        for m in re.finditer(r"url\(\s*['\"]?([^'\")]+)|@import\s+['\"]?([^'\";\s]+)", tekst):
            u = m.group(1) or m.group(2)
            if extern(u):
                fout(f"{p.relative_to(PUBLIC)}: externe resource in CSS: {u}")
    htaccess = lees_htaccess()
    for pad in paginas:
        naam = pad.relative_to(PUBLIC).as_posix()
        p = Pagina(naam)
        p.feed(pad.read_text(encoding="utf-8"))
        p.close()
        if p.stapel:
            fout(f"{naam}: niet gesloten elementen: {'/'.join(p.stapel)}")
        # 1. Externe resources
        for u in p.bronnen + p.stylesheets + p.scripts:
            if extern(u):
                fout(f"{naam}: externe resource: {u}")
        # 2. Interne links
        for u in p.links + p.bronnen + p.stylesheets + p.scripts:
            if extern(u) or u.startswith(("mailto:", "tel:", "data:")):
                continue
            if u.startswith("#"):
                if u[1:] and u[1:] not in p.ids:
                    fout(f"{naam}: anker {u} bestaat niet op de pagina")
                continue
            if not u.startswith("/"):
                fout(f"{naam}: relatieve link {u}, gebruik een pad vanaf /")
                continue
            doel = pad_voor(u)
            frag = urlsplit(u).fragment
            if doel is None and not redirect_voor(htaccess, urlsplit(u).path):
                fout(f"{naam}: dode interne link {u}")
            elif doel is not None and frag and doel.suffix == ".html":
                if f'id="{frag}"' not in doel.read_text(encoding="utf-8"):
                    fout(f"{naam}: anker #{frag} bestaat niet in {u}")
        # 5. Budget
        totaal = pad.stat().st_size
        for u in p.stylesheets + p.scripts:
            d = pad_voor(u)
            if d:
                totaal += d.stat().st_size
        if totaal > BUDGET_PAGINA:
            fout(f"{naam}: HTML+CSS+JS is {totaal // 1024} kB, budget {BUDGET_PAGINA // 1024} kB")
        if p.afbeeldingen:
            eerste = pad_voor(p.afbeeldingen[0])
            if eerste and eerste.stat().st_size > BUDGET_EERSTE_AFB:
                fout(f"{naam}: eerste afbeelding {p.afbeeldingen[0]} is groter dan {BUDGET_EERSTE_AFB // 1024} kB")
        # 6. Title en description
        if not (p.titel or "").strip():
            fout(f"{naam}: geen <title>")
        if not (p.beschrijving or "").strip():
            fout(f"{naam}: geen meta description")
    return len(paginas)


def controle_bestanden():
    for p in PUBLIC.rglob("*"):
        if p.suffix.lower() in {".jpg", ".jpeg", ".png", ".gif", ".webp", ".avif", ".svg", ".ico"}:
            if p.stat().st_size > MAX_BESTAND:
                fout(f"{p.relative_to(PUBLIC)}: {p.stat().st_size // 1024} kB, maximum {MAX_BESTAND // 1024} kB")


def controle_legacy_urls():
    htaccess = lees_htaccess()
    with (DATA / "legacy-urls.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            url, actie = r["url"], r["actie"]
            r_ = redirect_voor(htaccess, url)
            if actie == "410":
                if not r_ or r_[0] != "410":
                    fout(f"oude URL {url}: 410 ontbreekt in .htaccess")
                continue
            if pad_voor(url) is not None and not r_:
                continue
            if r_ and r_[0] == "301":
                if pad_voor(r_[1]) is None:
                    melding = f"oude URL {url}: 301 naar {r_[1]}, maar dat bestaat niet"
                    (fouten if MIGRATIE_KLAAR else waarschuwingen).append(melding)
                continue
            melding = f"oude URL {url} geeft een 404 (verwacht {actie})"
            (fouten if MIGRATIE_KLAAR else waarschuwingen).append(melding)


HUISNUMMER = re.compile(r"[A-Za-zé.]\s+\d{1,4}\s?[a-zA-Z]?(\s?-\s?\d+)?\b(?![,.]\d)")
WEG = re.compile(r"\b[AN]\s?\d{1,3}\b")
MEDISCH = re.compile(r"reanim|ambu|pati|afhijs|tillen|letsel|onwel|persoon|zelfdod|suic", re.I)
POSTCODE = re.compile(r"\b\d{4}\s?[A-Za-z]{2}\b")
TELEFOON = re.compile(r"(\+31|\b0)[\s-]?\d(?:[\s-]?\d){8}\b")
KENTEKEN = re.compile(r"\b(?=[A-Z0-9-]{8}\b)[A-Z0-9]{1,3}-[A-Z0-9]{1,3}-[A-Z0-9]{1,3}\b")


def controle_uitrukken():
    for pad in sorted((DATA / "uitrukken").glob("*.csv")):
        jaar = int(pad.stem)
        with pad.open(encoding="utf-8", newline="") as f:
            regels = list(csv.DictReader(f))
        for i, r in enumerate(regels, start=2):
            if r["publiceren"] != "ja":
                continue
            plek = f"{pad.relative_to(ROOT).as_posix()}:{i}"
            if r["bron"] not in ("legacy", "eigen", "p2000"):
                fout(f"{plek}: bron moet legacy, eigen of p2000 zijn")
            if r["prio"] and r["prio"] not in ("1", "2", "3"):
                fout(f"{plek}: prio '{r['prio']}' is geen 1, 2 of 3 (oefeningen horen niet in de uitrukken)")
            if not r["melding"].strip():
                fout(f"{plek}: melding ontbreekt")
            if r["bron"] in ("eigen", "p2000"):
                for veld in ("prio", "adres", "plaats"):
                    if not r[veld].strip():
                        fout(f"{plek}: {veld} ontbreekt (verplicht bij bron={r['bron']})")
            elif not (r["adres"].strip() or r["plaats"].strip()):
                fout(f"{plek}: adres en plaats zijn allebei leeg")
            tekst = " ".join((r["melding"], r["adres"], r["plaats"]))
            for naam, patroon in (("postcode", POSTCODE), ("telefoonnummer", TELEFOON), ("kenteken", KENTEKEN)):
                if patroon.search(tekst):
                    fout(f"{plek}: mogelijk {naam} in '{tekst}'")
            # Huisnummers zijn toegestaan in historische regels (besluit 27-09-2026),
            # behalve bij medische meldingen (besluit 28-09-2026, AVG).
            if r["bron"] == "legacy" and MEDISCH.search(r["melding"]) and HUISNUMMER.search(r["adres"]) \
                    and not WEG.search(r["adres"]):
                fout(f"{plek}: huisnummer bij medische melding '{r['melding']}' in '{r['adres']}'")
            # Huisnummers zijn toegestaan in historische regels (besluit 27-09-2026).
            if r["bron"] in ("eigen", "p2000") and HUISNUMMER.search(r["adres"]) and not WEG.search(r["adres"]):
                fout(f"{plek}: mogelijk huisnummer in '{r['adres']}'")
        if jaar in LEGACY_TELLING:
            legacy = [r for r in regels if r["bron"] == "legacy"]
            verwacht = LEGACY_TELLING[jaar] - LEGACY_WEG.get(jaar, 0)
            if len(legacy) != verwacht:
                fout(f"{pad.name}: {len(legacy)} legacy-regels, verwacht {verwacht}")
    for jaar in LEGACY_TELLING:
        if not (DATA / "uitrukken" / f"{jaar}.csv").exists():
            melding = f"data/uitrukken/{jaar}.csv ontbreekt"
            (fouten if MIGRATIE_KLAAR else waarschuwingen).append(melding)


def main():
    if not PUBLIC.is_dir():
        sys.exit("public/ bestaat niet. Draai eerst: python build.py")
    n = controle_html()
    controle_bestanden()
    controle_legacy_urls()
    controle_uitrukken()
    if waarschuwingen:
        print(f"{len(waarschuwingen)} waarschuwing(en), fout zodra MIGRATIE_KLAAR = True:")
        for w in waarschuwingen[:15]:
            print(f"  - {w}")
        if len(waarschuwingen) > 15:
            print(f"  ... en nog {len(waarschuwingen) - 15}")
    if fouten:
        print(f"{len(fouten)} fout(en):")
        for f in fouten:
            print(f"  - {f}")
        sys.exit(1)
    print(f"Alle controles geslaagd ({n} HTML-bestanden).")


if __name__ == "__main__":
    main()

"""Eenmalige migratie van de oude Hugo-site (legacy/) naar content/, data/ en afbeeldingen/.

Gebruik:
    python tools/migrate_hugo.py            # alleen rapport, schrijft niets
    python tools/migrate_hugo.py --apply    # schrijft de bestanden

Wat het doet (zie CLAUDE.md fase 3 en de besluiten in VOORTGANG.md):
- Uitrukken 2008 t/m 2022 naar data/uitrukken/JJJJ.csv. Regels uit andere bronnen
  (eigen, p2000) in die jaren blijven staan. Per jaar moet het aantal regels gelijk zijn
  aan het aantal <tr> in de oude tabel, anders stopt het script.
- Nieuwsartikelen naar content/nieuws/ met YAML front matter (title, date, author,
  description, banner, fotos). Tags en categorieën vervallen.
- Shortcodes: gallery/figure worden een fotolijst in de front matter, youtube (en de
  YouTube-iframe) wordt een link, incident-location een link naar OpenStreetMap,
  tweet en facebook-post vervallen.
- Afbeeldingen naar afbeeldingen/ met genormaliseerde namen. Oude paden komen in
  data/afbeeldingen-oud.csv; build.py maakt daar 301's van.
- Posten Kennemerland: de kaart wordt een lijst met links naar OpenStreetMap.
- Over ons en Betekenis P2000: tekst overgenomen, met de vastgelegde aanpassingen.

Voertuigpagina's, disclaimer, privacy en home zijn al met de hand gemaakt en worden
niet overschreven. Alleen standaardbibliotheek plus pyyaml.
"""

import argparse
import csv
import datetime as dt
import html
import re
import shutil
import sys
import tomllib
from collections import Counter, defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
LEGACY = ROOT / "legacy"
LCONTENT = LEGACY / "content"
LSTATIC = LEGACY / "static"
AFBEELDINGEN = ROOT / "afbeeldingen"
KOLOMMEN = ["nr", "datum", "tijd", "prio", "melding", "adres", "plaats", "bron", "publiceren"]

MAANDEN = {"jan": 1, "feb": 2, "mrt": 3, "mar": 3, "maa": 3, "apr": 4, "mei": 5, "jun": 6,
           "jul": 7, "aug": 8, "sep": 9, "okt": 10, "nov": 11, "dec": 12}

# Plaatsnamen die in de oude uitrukken voorkomen. Staat het deel na de laatste komma
# of tussen haakjes hierin, dan is het de plaats.
PLAATSEN = {
    "Akersloot", "Alkmaar", "Amsterdam", "Amsterdam Zuidoost", "Assendelft", "Badhoevedorp",
    "Bakkum", "Bennebroek", "Bergen", "Beverwijk", "Bloemendaal", "Callantsoog", "Castricum",
    "Driehuis", "Egmond aan Zee", "Haarlem", "Halfweg", "Heemskerk", "Heemstede", "Heiloo",
    "Hoofddorp", "IJmuiden", "Ijmuiden", "Krommenie", "Limmen", "Marken", "Nieuw-Vennep",
    "Overveen", "Purmerend", "Santpoort-Noord", "Santpoort-Zuid", "Schoorl", "Uitgeest",
    "Velsen-Noord", "Velsen-Zuid", "Velserbroek", "Volendam", "Weteringbrug", "Wijk aan Zee",
    "Wormer", "Wormerveer", "Zaandam", "Zaandijk", "Zandvoort", "Zwaanshoek",
}
WEG = re.compile(r"\b[AN]\s?\d{1,3}\b")
# Besluit Sven 28-09-2026 (AVG): bij medische meldingen geen huisnummer, want adres plus
# medische melding is een gezondheidsgegeven van een herkenbaar persoon.
MEDISCH = re.compile(r"reanim|ambu|pati|afhijs|tillen|letsel|onwel|persoon|zelfdod|suic", re.I)
HUISNUMMER = re.compile(r"^(?P<straat>.*?[A-Za-zé.])\s+\d{1,5}(?![.,]\d)[a-zA-Z]{0,3}\b.*$")  # geen hectometer (53.7)
PRIO = re.compile(r"^\s*prio\s*(\d+)\s+", re.I)

# Kapotte tekens in een paar oude regels (besluit 27-09-2026: alleen de codering herstellen).
CODERING = {"PatiÃ«nt": "Patiënt", "Pati�nt": "Patiënt", "Ã«": "ë", "Ã©": "é"}

LEGACY_TELLING = {2008: 95, 2009: 113, 2010: 119, 2011: 127, 2012: 112, 2013: 116, 2014: 104,
                  2015: 91, 2016: 106, 2017: 126, 2018: 124, 2019: 76, 2020: 98, 2021: 69, 2022: 52}

# Oude regels die bewust niet worden overgenomen: (datum, melding). Oefeningen zijn geen
# uitrukken (besluit Sven 28-09-2026). check.py verwacht per jaar de telling min deze regels.
LEGACY_WEG = {("2012-12-11", "Brand oefening")}

rapport = defaultdict(list)


# Uitrukken

def lees_tabel(jaar):
    tekst = (LCONTENT / f"{jaar}.md").read_text(encoding="utf-8")
    body = tekst.split("<tbody>", 1)[1].split("</tbody>", 1)[0]
    aantal_tr = len(re.findall(r"<tr\b", body))
    rijen = []
    for tr in re.findall(r"<tr[^>]*>(.*?)</tr>", body, re.S):
        cellen = [html.unescape(re.sub(r"<[^>]+>", "", c)).strip()
                  for c in re.findall(r"<td[^>]*>(.*?)</td>", tr, re.S)]
        rijen.append(cellen)
    return aantal_tr, rijen


def herstel_codering(s):
    for fout_, goed in CODERING.items():
        s = s.replace(fout_, goed)
    return s


def is_plaats(s):
    """Plaatsnaam, ook als het streepje anders geschreven is ("Velsen – Noord")."""
    sleutel = re.sub(r"\s*[-–]\s*", "-", s.strip()).lower()
    return any(sleutel == re.sub(r"\s*[-–]\s*", "-", p).lower() for p in PLAATSEN)


def splits_adres(adres, jaar):
    """Geeft (adres, plaats) volgens de besluiten van 27-09-2026."""
    a = adres.strip()
    if is_plaats(a):
        return "", a
    m = re.fullmatch(r"(.*?)\s*\(([^()]+)\)", a)
    if m and is_plaats(m.group(2)):
        return m.group(1).strip(), m.group(2).strip()
    if ", " in a:
        voor, na = a.rsplit(", ", 1)
        if is_plaats(na):
            return voor.strip(), na.strip()
    # Plaatsnaam aan het eind zonder komma, bijv. "Corus Beverwijk" of "Oprit 10 A9 Castricum".
    # Niet na woorden die bij een naam horen ("Haven van Uitgeest", "Station Uitgeest", "Oprit Heemskerk").
    # Bij wegen alleen direct na het hectometergetal ("A9 L 61.0 Uitgeest").
    for p in sorted(PLAATSEN, key=len, reverse=True):
        if a.endswith(" " + p) and len(a) > len(p) + 1:
            voor = a[: -len(p)].strip()
            laatste = voor.split()[-1].lower()
            if laatste in {"van", "station", "afrit", "oprit", "thv", "ns"}:
                break
            if WEG.search(voor) and (not re.search(r"\d", laatste) or re.search(r"afrit|oprit", voor, re.I)):
                break
            rapport["plaats aan het eind zonder komma"].append(f"{jaar}: {a}")
            return voor, p
    if WEG.search(a):
        return a, ""
    if m and re.fullmatch(r"[A-Z]{2,4}", m.group(2).strip()):
        # Afkorting zoals (HMS): mogelijk een plaats, niet raden.
        rapport["afkorting tussen haakjes (plaats leeg gelaten)"].append(f"{jaar}: {a}")
        return a, ""
    return a, "Uitgeest"


def migreer_uitrukken(apply):
    uit = {}
    for jaar in range(2008, 2023):
        aantal_tr, rijen = lees_tabel(jaar)
        if aantal_tr != LEGACY_TELLING[jaar] or len(rijen) != aantal_tr:
            sys.exit(f"FOUT: {jaar}: {len(rijen)} regels gelezen, {aantal_tr} <tr>, verwacht {LEGACY_TELLING[jaar]}")
        nieuw = []
        for volgorde, (nr, datum, melding, adres) in enumerate(rijen):
            dag, mnd = datum.split("-")
            if mnd.lower() not in MAANDEN:
                sys.exit(f"FOUT: {jaar}: onbekende maand in '{datum}'")
            iso = f"{jaar}-{MAANDEN[mnd.lower()]:02d}-{int(dag):02d}"
            melding = herstel_codering(melding)
            prio = ""
            m = PRIO.match(melding)
            if m:
                if m.group(1) in ("1", "2", "3"):
                    prio = m.group(1)
                else:
                    rapport["prio buiten 1-3 (prio leeg, prefix weg)"].append(f"{jaar}: {melding}")
                melding = melding[m.end():]
            if (iso, melding.strip()) in LEGACY_WEG:
                rapport["oude regel bewust weggelaten (oefening)"].append(f"{jaar}: {iso} {melding}")
                continue
            adres, plaats = splits_adres(herstel_codering(adres), jaar)
            if MEDISCH.search(melding) and not WEG.search(adres):
                h = HUISNUMMER.match(adres)
                if h:
                    rapport["huisnummer weggehaald bij medische melding (AVG)"].append(f"{jaar}: {melding}")
                    adres = h.group("straat").strip()
            try:
                oud_nr = int(nr)
            except ValueError:
                oud_nr = 0
            nieuw.append(({"nr": "", "datum": iso, "tijd": "", "prio": prio, "melding": melding.strip(),
                           "adres": adres, "plaats": plaats, "bron": "legacy", "publiceren": "ja"},
                          (iso, oud_nr, volgorde)))
        # Regels uit andere bronnen (eigen, p2000) in dit jaar behouden.
        pad = ROOT / "data" / "uitrukken" / f"{jaar}.csv"
        anders = []
        if pad.exists():
            with pad.open(encoding="utf-8", newline="") as f:
                anders = [r for r in csv.DictReader(f) if r["bron"] != "legacy"]
        regels = [r for r, _ in sorted(nieuw, key=lambda x: x[1])]
        alle = sorted(regels + anders, key=lambda r: (r["datum"], r["tijd"] or ""))
        for i, r in enumerate(alle, start=1):
            r["nr"] = str(i)
        uit[jaar] = alle
        rapport["uitrukken per jaar (legacy + andere bronnen)"].append(
            f"{jaar}: {len(regels)} + {len(anders)}, zonder prio {sum(1 for r in regels if not r['prio'])}, "
            f"zonder plaats {sum(1 for r in regels if not r['plaats'])}")
        if apply:
            pad.parent.mkdir(parents=True, exist_ok=True)
            with pad.open("w", encoding="utf-8", newline="") as f:
                w = csv.DictWriter(f, fieldnames=KOLOMMEN, lineterminator="\n")
                w.writeheader()
                w.writerows(alle)
    return uit


# Afbeeldingen

afbeeldingen_oud = {}  # oud pad (/img/...) -> nieuw pad (relatief aan afbeeldingen/)


def normaliseer_naam(naam):
    stam, _, ext = naam.rpartition(".")
    ext = {"jpeg": "jpg"}.get(ext.lower(), ext.lower())
    stam = re.sub(r"\(medium\)", "", stam, flags=re.I)
    stam = re.sub(r"[^A-Za-z0-9]+", "-", stam).strip("-").lower()
    return f"{stam}.{ext}"


def neem_afbeelding(oud, map_, apply):
    """Kopieert /img/... naar afbeeldingen/<map_>/<genormaliseerd> en onthoudt het oude pad."""
    oud = "/" + oud.lstrip("/")
    if oud in afbeeldingen_oud:
        return afbeeldingen_oud[oud]
    bron = LSTATIC / oud.lstrip("/")
    if not bron.is_file():
        rapport["afbeelding niet gevonden"].append(oud)
        return None
    nieuw = f"{map_}/{normaliseer_naam(bron.name)}"
    afbeeldingen_oud[oud] = nieuw
    if apply:
        doel = AFBEELDINGEN / nieuw
        doel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(bron, doel)
    return nieuw


# Nieuws

def lees_toml(pad):
    tekst = pad.read_text(encoding="utf-8")
    _, kop, body = tekst.split("+++", 2)
    return tomllib.loads(kop), body


def interne_links(body):
    """Absolute links naar de eigen site worden paden; oude paden gaan direct naar hun nieuwe doel."""
    doelen = {}
    with (ROOT / "data" / "legacy-urls.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            if r["actie"] == "301" and r["doel"].startswith("/"):
                doelen[r["url"]] = r["doel"]

    def vervang(m):
        pad = m.group(1) or "/"
        return "(" + doelen.get(pad, pad)

    return re.sub(r"\(https?://(?:www\.)?brandweeruitgeest\.nl(/[^)\s\"]*)?", vervang, body)


def migreer_nieuws(apply):
    uitvoer = ROOT / "content" / "nieuws"
    for pad in sorted((LCONTENT / "nieuws").glob("*.md")):
        meta, body = lees_toml(pad)
        slug = pad.stem
        titel = meta["title"].strip()
        body = body.replace("​", "").strip("\n")

        fotos = [m for m in re.findall(r'\{\{<\s*figure\s+src="([^"]+)"[^>]*>\}\}', body)]
        body = re.sub(r"\{\{<\s*/?(gallery|load-photoswipe)\s*>\}\}\s*", "", body)
        body = re.sub(r'\{\{<\s*figure[^>]*>\}\}\s*', "", body)
        body = re.sub(r"\{\{<\s*youtube\s+([\w-]+)\s*>\}\}",
                      r"[Bekijk de video op YouTube](https://www.youtube.com/watch?v=\1)", body)
        body = re.sub(r'<iframe[^>]*youtube(?:-nocookie)?\.com/embed/([\w-]+)[^>]*>\s*</iframe>',
                      r"[Bekijk de video op YouTube](https://www.youtube.com/watch?v=\1)", body)
        if re.search(r"\{\{<\s*(tweet|facebook-post)", body):
            rapport["tweets en Facebook-posts weggehaald"].append(slug)
        body = re.sub(r"\{\{<\s*(tweet|facebook-post)[^>]*>\}\}\s*", "", body)

        def osm(m):
            lat = f"{m.group(1)}.{m.group(2)}"
            lon = f"{m.group(3)}.{m.group(4)}"
            return (f"[Bekijk de locatie op OpenStreetMap](https://www.openstreetmap.org/"
                    f"?mlat={lat}&mlon={lon}#map=16/{lat}/{lon})")
        body = re.sub(r"\{\{<\s*incident-location\s+(\d+)\s+(\d+)\s+(\d+)\s+(\d+)\s*>\}\}", osm, body)
        if "{{<" in body or "{{%" in body:
            sys.exit(f"FOUT: onbekende shortcode over in {pad.name}")
        body = interne_links(body)
        if re.search(r"^# ", body, re.M):  # de titel is al de h1; koppen één niveau lager
            body = re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", body, flags=re.M)
        body = re.sub(r"[ \t]+\n", "\n", body)          # spaties aan regeleinden (Markdown-regelbreuk)
        body = re.sub(r"\n{3,}", "\n\n", body).strip() + "\n"

        map_ = f"nieuws/{slug}"
        nieuwe_fotos = []
        for i, src in enumerate(fotos, start=1):
            nieuw = neem_afbeelding(src, map_, apply)
            if nieuw:
                nieuwe_fotos.append({"src": nieuw, "alt": f"Foto {i} van {len(fotos)} bij: {titel}"})
        datum = meta["date"]
        if isinstance(datum, str):
            datum = dt.datetime.fromisoformat(datum)
        datum = datum.replace(tzinfo=None)  # lokale tijd, zodat de dag in de URL gelijk blijft
        fm = {"title": titel, "date": datum, "author": meta.get("author", ""),
              "description": " ".join(meta.get("description", "").split())}
        if meta.get("banner"):
            b = neem_afbeelding(meta["banner"], map_, apply)
            if b:
                fm["banner"] = {"src": b, "alt": f"Foto bij: {titel}"}
        for extra in meta.get("images") or []:
            neem_afbeelding(extra, map_, apply)
        if nieuwe_fotos:
            fm["fotos"] = nieuwe_fotos
        if not fm["author"]:
            del fm["author"]
        rapport["nieuwsartikelen"].append(f"{slug}: {len(nieuwe_fotos)} foto's")
        if apply:
            uitvoer.mkdir(parents=True, exist_ok=True)
            tekst = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False, width=1000) + "---\n\n" + body
            (uitvoer / f"{slug}.md").write_text(tekst, encoding="utf-8", newline="\n")


# Losse pagina's

def migreer_posten(apply):
    js = (LSTATIC / "js" / "leaflet_brw_posten_kennemerland.js").read_text(encoding="utf-8")
    posten = re.findall(r'L\.marker\(\[([\d.]+),\s*([\d.]+)\].*?bindTooltip\("([^"]+)"\).*?href=\\"([^\\]+)\\"',
                        js, re.S)
    regels = ["Dit zijn de brandweerposten van Veiligheidsregio Kennemerland. "
              "Klik op een post voor de ligging op OpenStreetMap.", "",
              "| Post | Kaart | Website |", "|---|---|---|"]
    for lat, lon, naam, website in posten:
        naam = naam.replace("Post ", "")
        kaart = f"https://www.openstreetmap.org/?mlat={lat}&mlon={lon}#map=17/{lat}/{lon}"
        site = "/" if "brandweeruitgeest.nl" in website else website
        regels.append(f"| {naam} | [Kaart]({kaart}) | [Website]({site}) |")
    rapport["posten Kennemerland"].append(f"{len(posten)} posten")
    fm = {"title": "Posten Kennemerland", "description": "Alle brandweerposten van Veiligheidsregio Kennemerland."}
    if apply:
        tekst = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + "\n".join(regels) + "\n"
        (ROOT / "content" / "posten-kennemerland.md").write_text(tekst, encoding="utf-8", newline="\n")


VACATURE = "https://www.werkenbijdevrk.nl/vacatures/brandweervrijwilliger/8fa2ec35-00b3-4844-be28-4cba4928301b"


def migreer_over_ons(apply):
    _, body = lees_toml(LCONTENT / "over-ons.md")
    body = body.replace("​", "").strip()
    # Het oude thema zette hier een contactformulier onder (besluit: vervalt, wordt werving en mail).
    body += ("\n\n## Aanmelden\n\n"
             f"Interesse? Bekijk de [vacature brandweervrijwilliger]({VACATURE}) bij Veiligheidsregio "
             "Kennemerland. Vragen kun je mailen naar [info@brandweeruitgeest.nl](mailto:info@brandweeruitgeest.nl).\n")
    # De pagina-titel is al een h1; koppen in de tekst schuiven één niveau op.
    body = re.sub(r"^(#{1,5}) ", lambda m: "#" + m.group(1) + " ", body, flags=re.M)
    fm = {"title": "Over ons", "description": "Over brandweer Uitgeest, de post aan de Molenwerf en werken als brandweervrijwilliger."}
    if apply:
        tekst = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + body + "\n"
        (ROOT / "content" / "over-ons.md").write_text(tekst, encoding="utf-8", newline="\n")


def migreer_p2000(apply):
    meta, body = lees_toml(LCONTENT / "betekenis-p2000-meldingen.md")
    body = re.sub(r'<a name="([A-Z])"></a>', r'<a id="\1"></a>', body.replace("​", "")).strip()
    fm = {"title": "Betekenis P2000-meldingen",
          "description": "Uitleg van afkortingen in P2000-meldingen van brandweer en ambulance."}
    if apply:
        tekst = "---\n" + yaml.safe_dump(fm, allow_unicode=True, sort_keys=False) + "---\n\n" + body + "\n"
        (ROOT / "content" / "betekenis-p2000-meldingen.md").write_text(tekst, encoding="utf-8", newline="\n")


def overige_afbeeldingen(apply):
    """Afbeeldingen die niet meer op een pagina staan maar wel een 301 krijgen (besluit 27-09-2026)."""
    for p in sorted((LSTATIC / "img" / "voertuigen").rglob("*")):
        v = p.parent.name
        # 12-2001 (oude dienstauto) en de binnenkant van 12-2030 staan niet meer op de site (28-09-2026).
        if p.is_file() and v not in ("12-2003", "12-2031", "12-2061", "12-2001") \
                and p.name not in ("DSC06422.jpg", "DSC06430.jpg"):
            neem_afbeelding(f"/img/voertuigen/{v}/{p.name}", f"voertuigen/{v}", apply)
    for p in sorted((LSTATIC / "img" / "clients").glob("12*")):
        if "122031" not in p.name and "122061" not in p.name:
            neem_afbeelding(f"/img/clients/{p.name}", "archief/voertuigtegels", apply)
    for p in sorted((LSTATIC / "img" / "carousel").glob("*")):
        neem_afbeelding(f"/img/carousel/{p.name}", "archief/veiligheidstips", apply)


def main():
    ap = argparse.ArgumentParser(description="Migreer legacy/ naar de nieuwe structuur.")
    ap.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    migreer_uitrukken(args.apply)
    migreer_nieuws(args.apply)
    migreer_posten(args.apply)
    # Over ons is op 28-09-2026 op verzoek van Sven herschreven; niet meer overschrijven.
    migreer_p2000(args.apply)
    overige_afbeeldingen(args.apply)

    if args.apply:
        with (ROOT / "data" / "afbeeldingen-oud.csv").open("w", encoding="utf-8", newline="") as f:
            w = csv.writer(f, lineterminator="\n")
            w.writerow(["oud", "nieuw"])
            for oud, nieuw in sorted(afbeeldingen_oud.items()):
                w.writerow([oud, nieuw])
    rapport["afbeeldingen"].append(f"{len(afbeeldingen_oud)} oude paden met een nieuw adres")
    for kop, regels in rapport.items():
        print(f"{kop}:")
        for r in regels:
            print(f"  {r}")
    if not args.apply:
        print("Niets geschreven. Draai opnieuw met --apply.")


if __name__ == "__main__":
    main()

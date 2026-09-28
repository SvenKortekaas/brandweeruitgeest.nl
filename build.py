"""Bouwt brandweeruitgeest.nl van content/, data/, templates/, static/ en afbeeldingen/ naar public/.

Gebruik:
    python build.py

Alleen jinja2, markdown, pyyaml en Pillow. Werkt op Windows, macOS en Linux.
"""

import csv
import datetime as dt
import hashlib
import html
import re
import shutil
import sys
from collections import Counter, OrderedDict
from pathlib import Path

import markdown
import yaml
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from markupsafe import Markup
from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parent
CONTENT = ROOT / "content"
DATA = ROOT / "data"
TEMPLATES = ROOT / "templates"
STATIC = ROOT / "static"
AFBEELDINGEN = ROOT / "afbeeldingen"
PUBLIC = ROOT / "public"
CACHE = ROOT / ".cache" / "img"

NIEUWS_PER_PAGINA = 10
FOTO_BREEDTES = (480, 960, 1600)
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli",
           "augustus", "september", "oktober", "november", "december"]
UITRUK_KOLOMMEN = ["nr", "datum", "tijd", "prio", "melding", "adres", "plaats", "bron", "publiceren"]


def fout(bericht):
    sys.exit(f"FOUT: {bericht}")


# Inhoud lezen

def lees_markdown(pad):
    """Geeft (front matter, html) van een Markdown-bestand met YAML front matter."""
    tekst = pad.read_text(encoding="utf-8")
    meta = {}
    if tekst.startswith("---"):
        try:
            _, kop, tekst = tekst.split("---", 2)
        except ValueError:
            fout(f"{pad}: front matter niet afgesloten met ---")
        meta = yaml.safe_load(kop) or {}
    for veld in ("title", "description"):
        if not meta.get(veld):
            fout(f"{pad}: veld '{veld}' ontbreekt in de front matter")
    body = markdown.markdown(tekst, extensions=["extra", "sane_lists"], output_format="html")
    return meta, Markup(body)


# Groepen om op te filteren (jaarpagina, via ankers zonder JS). De eerste passende regel
# wint. De slugs staan ook in static/css/site.css (filterregels); houd die gelijk.
SOORTGROEPEN = [
    ("automatisch", "Automatische melding", re.compile(
        r"\babm\b|\boms\b|\bpac\b|automatisch|brandmeld|rookmeld|co[ -]?meld|rook ?/ ?co|basis alarm", re.I)),
    ("ambulance", "Ambulance en reanimatie", re.compile(
        r"reanim|ambu|afhijs|tillen|\btil\b|\baed\b|gezondheid|onwel|pati|huisarts|eerste hulp", re.I)),
    ("dieren", "Dieren", re.compile(r"\bdier|\bkoe\b|schaap|paard|\bkat\b|hert\b", re.I)),
    ("water", "Water", re.compile(r"te water|water in|watersport|\bschip|vaartuig|ongeval water|zinkend|door ijs|vuurpijl", re.I)),
    ("brand", "Brand", re.compile(
        r"brand(?!stof)|nacontrole|nablussen|\bwts\b|middel wo", re.I)),
    ("hulpverlening", "Ongeval en hulpverlening", re.compile(
        r"ongeval|\bvko\b|beknel|hulpverlening|\bhv\b|letsel|lift|storm|sneeuw|wateroverlast|gas|"
        r"lekkage|stank|meting|wegdek|instorting|explosie|gevaarlijke|buitensluiting|openen deur|"
        r"verdachte|treinongeval|stromschade|boom|op hoogte|vreemde lucht|luchtverontr", re.I)),
]
OVERIG = ("overig", "Overig")


def soortgroep(melding):
    for slug, naam, patroon in SOORTGROEPEN:
        if patroon.search(melding):
            return slug, naam
    return OVERIG


def is_oefening(r):
    """Oefeningen tellen apart, niet als uitruk (besluit 28-09-2026)."""
    return r["prio"] == "5" or r["melding"].strip().lower() == "oefening"


def lees_uitrukken():
    """Alle uitrukken per jaar, gecontroleerd op kolommen en waarden."""
    jaren = {}
    for pad in sorted((DATA / "uitrukken").glob("*.csv")):
        jaar = int(pad.stem)
        with pad.open(encoding="utf-8", newline="") as f:
            lezer = csv.DictReader(f)
            if lezer.fieldnames != UITRUK_KOLOMMEN:
                fout(f"{pad}: kolommen moeten zijn {','.join(UITRUK_KOLOMMEN)}")
            regels = []
            for i, r in enumerate(lezer, start=2):
                try:
                    r["datum"] = dt.date.fromisoformat(r["datum"])
                except ValueError:
                    fout(f"{pad}:{i}: ongeldige datum '{r['datum']}'")
                if r["datum"].year != jaar:
                    fout(f"{pad}:{i}: datum valt niet in {jaar}")
                if r["publiceren"] not in ("ja", "nee"):
                    fout(f"{pad}:{i}: publiceren moet ja of nee zijn")
                r["nr"] = int(r["nr"])
                regels.append(r)
        jaren[jaar] = regels
    return jaren


# Afbeeldingen

class Fotos:
    """Zet bronafbeeldingen om naar WebP en AVIF in meerdere breedtes, zonder metadata."""

    def __init__(self):
        self.gemaakt = {}

    def varianten(self, pad):
        if pad in self.gemaakt:
            return self.gemaakt[pad]
        bron = AFBEELDINGEN / pad
        if not bron.is_file():
            fout(f"afbeelding niet gevonden: afbeeldingen/{pad}")
        data = bron.read_bytes()
        kort = hashlib.sha256(data).hexdigest()[:8]
        with Image.open(bron) as im:
            im = ImageOps.exif_transpose(im)
            im = im.convert("RGB")
            breedte, hoogte = im.size
            breedtes = sorted({min(b, breedte) for b in FOTO_BREEDTES})
            stam = Path(pad).with_suffix("").as_posix()
            uit = []
            for b in breedtes:
                h = round(hoogte * b / breedte)
                bestanden = {}
                for fmt, kwaliteit in (("avif", 55), ("webp", 78)):
                    naam = f"img/{stam}-{b}.{kort}.{fmt}"
                    cache = CACHE / naam
                    if not cache.exists():
                        cache.parent.mkdir(parents=True, exist_ok=True)
                        klein = im.resize((b, h), Image.LANCZOS) if b != breedte else im
                        klein.save(cache, fmt.upper(), quality=kwaliteit)
                    doel = PUBLIC / naam
                    doel.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(cache, doel)
                    bestanden[fmt] = "/" + naam
                uit.append({"breedte": b, "hoogte": h, **bestanden})
        self.gemaakt[pad] = uit
        return uit

    def html(self, pad, alt, sizes="(min-width: 60rem) 60rem, 100vw", lui=True):
        v = self.varianten(pad)
        grootste = v[-1]
        # Standaardafbeelding: de middelste breedte is een goede balans voor browsers zonder srcset.
        standaard = v[min(1, len(v) - 1)]
        srcset = lambda fmt: ", ".join(f"{x[fmt]} {x['breedte']}w" for x in v)
        laden = ' loading="lazy"' if lui else ' fetchpriority="high"'
        return Markup(
            "<picture>"
            f'<source type="image/avif" srcset="{srcset("avif")}" sizes="{sizes}">'
            f'<img src="{standaard["webp"]}" srcset="{srcset("webp")}" sizes="{sizes}" '
            f'width="{grootste["breedte"]}" height="{grootste["hoogte"]}" '
            f'alt="{html.escape(alt)}" decoding="async"{laden}>'
            "</picture>"
        )

    def groot(self, pad):
        return self.varianten(pad)[-1]["webp"]


# Hulpfuncties voor templates

def datum_nl(d, jaar=True):
    tekst = f"{d.day} {MAANDEN[d.month - 1]}"
    return f"{tekst} {d.year}" if jaar else tekst


def schrijf(url, inhoud):
    """Schrijft inhoud naar public/ voor een URL als /pad/ of /bestand.xml."""
    pad = PUBLIC / url.lstrip("/")
    if url.endswith("/"):
        pad = pad / "index.html"
    pad.parent.mkdir(parents=True, exist_ok=True)
    pad.write_text(inhoud, encoding="utf-8", newline="\n")


def asset(env_assets, bron):
    """Kopieert een bestand uit static/ met een hash in de naam en geeft het pad terug."""
    if bron not in env_assets:
        pad = STATIC / bron
        kort = hashlib.sha256(pad.read_bytes()).hexdigest()[:8]
        naam = f"{Path(bron).with_suffix('').as_posix()}.{kort}{pad.suffix}"
        doel = PUBLIC / naam
        doel.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(pad, doel)
        env_assets[bron] = "/" + naam
    return env_assets[bron]


def slug(tekst):
    return re.sub(r"[^a-z0-9]+", "-", tekst.lower()).strip("-")


# .htaccess

def regex_pad(url):
    kern = re.escape(url.rstrip("/")) if url != "/" else ""
    return f"^{kern}/?$" if url.endswith("/") else f"^{kern}$"


def htaccess(site, gegenereerd, fotos):
    regels = []
    redirects = OrderedDict()
    with (DATA / "legacy-urls.csv").open(encoding="utf-8", newline="") as f:
        for r in csv.DictReader(f):
            url, actie, doel = r["url"], r["actie"], r["doel"]
            if actie == "301" and doel.startswith("/"):
                redirects[url] = ("301", doel)
            elif actie == "410":
                redirects[url] = ("410", "")
            elif actie == "200" and url not in gegenereerd:
                # Een oude pagina die (nog) niet bestaat. Paginering valt terug op het overzicht.
                if re.fullmatch(r"/nieuws/page/\d+/", url):
                    redirects[url] = ("301", "/nieuws/")
    # Doorverwijzing naar een nieuwspagina die er niet (meer) is: naar het overzicht.
    for url, (code, doel) in redirects.items():
        if code == "301" and re.fullmatch(r"/nieuws/page/\d+/", doel) and doel not in gegenereerd:
            redirects[url] = ("301", "/nieuws/")
    # Oude afbeeldingspaden (tools/migrate_hugo.py) naar de grootste nieuwe versie.
    oud = DATA / "afbeeldingen-oud.csv"
    if oud.exists():
        with oud.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                redirects[r["oud"]] = ("301", fotos.groot(r["nieuw"]))
    redirects["/img/logo.png"] = ("301", "/logo.png")
    extra = DATA / "redirects.csv"
    if extra.exists():
        with extra.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                redirects[r["oud"]] = ("301", r["nieuw"])

    regels += [
        "# Gegenereerd door build.py. Niet met de hand wijzigen.",
        "Options -Indexes",
        "AddDefaultCharset utf-8",
        "AddType image/avif .avif",
        "AddType image/webp .webp",
        "ErrorDocument 404 /404.html",
        "ErrorDocument 410 /404.html",
        "",
        "# HTTPS en host zonder www. Werkt op elke host (ook het testsubdomein v2.).",
        "RewriteEngine On",
        "RewriteCond %{HTTP_HOST} ^www\\.(.+)$ [NC]",
        "RewriteRule ^ https://%1%{REQUEST_URI} [R=301,L]",
        "RewriteCond %{HTTPS} !=on",
        "RewriteRule ^ https://%{HTTP_HOST}%{REQUEST_URI} [R=301,L]",
        "",
        "# Geen toegang tot dotfiles, behalve .well-known",
        'RedirectMatch 404 "/\\.(?!well-known/)"',
        "",
        "<IfModule mod_headers.c>",
        '  Header always set Strict-Transport-Security "max-age=31536000; includeSubDomains"',
        "  Header always set Content-Security-Policy \"default-src 'self'; img-src 'self' data:; "
        "style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self'; "
        "frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests\"",
        '  Header always set X-Content-Type-Options "nosniff"',
        '  Header always set Referrer-Policy "strict-origin-when-cross-origin"',
        '  Header always set Cross-Origin-Opener-Policy "same-origin"',
        '  Header always set Permissions-Policy "geolocation=(), camera=(), microphone=(), browsing-topics=()"',
        "  # Testomgeving (v2.brandweeruitgeest.nl) niet in zoekmachines.",
        '  <If "%{HTTP_HOST} =~ /^v2\\./">',
        '    Header always set X-Robots-Tag "noindex, nofollow"',
        "  </If>",
        '  <FilesMatch "\\.[0-9a-f]{8}\\.(css|js|webp|avif)$">',
        '    Header set Cache-Control "public, max-age=31536000, immutable"',
        "  </FilesMatch>",
        '  <FilesMatch "\\.(html|xml|txt|json)$">',
        '    Header set Cache-Control "public, max-age=300"',
        "  </FilesMatch>",
        "</IfModule>",
        "",
        "# Oude URL's (data/legacy-urls.csv en data/redirects.csv)",
    ]
    for url, (code, doel) in redirects.items():
        if code == "301":
            regels.append(f'RedirectMatch 301 "{regex_pad(url)}" "{doel}"')
        else:
            regels.append(f'RedirectMatch 410 "{regex_pad(url)}"')
    return "\n".join(regels) + "\n"


# Bouwen

def bouw():
    if PUBLIC.exists():
        shutil.rmtree(PUBLIC)
    PUBLIC.mkdir()
    site = yaml.safe_load((DATA / "site.yaml").read_text(encoding="utf-8"))
    fotos = Fotos()
    assets = {}

    env = Environment(loader=FileSystemLoader(TEMPLATES), autoescape=True,
                      undefined=StrictUndefined, trim_blocks=True, lstrip_blocks=True)
    env.globals.update(site=site, foto=fotos.html, foto_groot=fotos.groot,
                       asset=lambda b: asset(assets, b), maanden=MAANDEN,
                       jaar_nu=dt.date.today().year)
    env.filters.update(datum=datum_nl, slug=slug)

    paginas = []  # (url, titel) voor sitemap

    def render(url, template, **ctx):
        schrijf(url, env.get_template(template).render(url=url, **ctx))
        paginas.append(url)

    # Uitrukken
    jaren = lees_uitrukken()
    gepubliceerd = {j: [r for r in rs if r["publiceren"] == "ja"] for j, rs in jaren.items()}
    for jaar, regels in gepubliceerd.items():
        per_maand = OrderedDict()
        for r in sorted(regels, key=lambda r: r["nr"]):
            per_maand.setdefault(r["datum"].month, []).append(r)
        soorten = Counter(r["melding"] for r in regels).most_common()
        for r in regels:
            r["groep"] = soortgroep(r["melding"])[0]
        groepen = [(slug, naam, n) for (slug, naam), n in
                   Counter(soortgroep(r["melding"]) for r in regels).most_common()]
        groepen_per_maand = {m: {r["groep"] for r in rs} for m, rs in per_maand.items()}
        lijst = sorted(gepubliceerd)
        i = lijst.index(jaar)
        oefeningen = sum(1 for r in regels if is_oefening(r))
        aantal = len(regels) - oefeningen
        render(f"/uitrukken/{jaar}/", "uitrukken-jaar.html", jaar=jaar, aantal=aantal,
               oefeningen=oefeningen, lopend=(jaar == dt.date.today().year),
               per_maand=per_maand, soorten=soorten, groepen=groepen,
               groepen_per_maand=groepen_per_maand,
               vorige=lijst[i - 1] if i > 0 else None,
               volgende=lijst[i + 1] if i + 1 < len(lijst) else None,
               titel=f"Uitrukken {jaar}",
               beschrijving=f"Alle {aantal} uitrukken van brandweer Uitgeest in {jaar}.")
    totalen = [(j, sum(1 for x in r if not is_oefening(x)), sum(1 for x in r if is_oefening(x)))
               for j, r in sorted(gepubliceerd.items())]
    render("/uitrukken/", "uitrukken-overzicht.html", totalen=totalen,
           hoogste=max((a for _, a, _ in totalen), default=1),
           met_oefeningen=any(o for _, _, o in totalen),
           titel="Uitrukken", beschrijving="Alle uitrukken van brandweer Uitgeest per jaar.")
    alle = [r for rs in gepubliceerd.values() for r in rs]
    laatste = sorted(alle, key=lambda r: (r["datum"], r["nr"]), reverse=True)[:5]

    # Voertuigen
    voertuigen = []
    for pad in sorted((CONTENT / "voertuigen").glob("*.md")):
        meta, body = lees_markdown(pad)
        voertuigen.append({"url": f"/voertuigen/{pad.stem}/", "meta": meta, "body": body})
    voertuigen.sort(key=lambda v: v["meta"].get("volgorde", 99))
    for v in voertuigen:
        render(v["url"], "voertuig.html", meta=v["meta"], body=v["body"],
               titel=v["meta"]["title"], beschrijving=v["meta"]["description"])

    # Nieuws
    artikelen = []
    for pad in sorted((CONTENT / "nieuws").glob("*.md")):
        meta, body = lees_markdown(pad)
        d = meta.get("date")
        if not isinstance(d, (dt.date, dt.datetime)):
            fout(f"{pad}: veld 'date' ontbreekt of is geen datum")
        d = d if isinstance(d, dt.datetime) else dt.datetime.combine(d, dt.time(12))
        meta["date"] = d
        url = f"/nieuws/{d:%Y/%m/%d}/{pad.stem}/"
        artikelen.append({"url": url, "meta": meta, "body": body})
    artikelen.sort(key=lambda a: a["meta"]["date"], reverse=True)
    for a in artikelen:
        render(a["url"], "nieuwsartikel.html", meta=a["meta"], body=a["body"],
               titel=a["meta"]["title"], beschrijving=a["meta"]["description"])
    aantal_paginas = max(1, -(-len(artikelen) // NIEUWS_PER_PAGINA))
    for n in range(1, aantal_paginas + 1):
        url = "/nieuws/" if n == 1 else f"/nieuws/page/{n}/"
        stuk = artikelen[(n - 1) * NIEUWS_PER_PAGINA:n * NIEUWS_PER_PAGINA]
        render(url, "nieuwsoverzicht.html", artikelen=stuk, pagina=n, aantal_paginas=aantal_paginas,
               titel="Nieuwsarchief" if n == 1 else f"Nieuwsarchief, pagina {n}",
               beschrijving="Archief van nieuwsberichten van brandweer Uitgeest uit 2016 tot en met 2020.")
    schrijf("/nieuws/index.xml", env.get_template("feed.xml").render(artikelen=artikelen))

    # Losse pagina's
    for pad in sorted(CONTENT.glob("*.md")):
        meta, body = lees_markdown(pad)
        url = "/" if pad.stem == "index" else f"/{pad.stem}/"
        template = meta.get("template", "pagina") + ".html"
        render(url, template, meta=meta, body=body, titel=meta["title"],
               beschrijving=meta["description"], voertuigen=voertuigen, laatste=laatste)

    # 404, statische bestanden, sitemap, robots, .htaccess
    schrijf("/404.html", env.get_template("404.html").render(
        url="/404.html", titel="Pagina niet gevonden",
        beschrijving="Deze pagina bestaat niet (meer) op brandweeruitgeest.nl."))
    for pad in STATIC.rglob("*"):
        if pad.is_file() and not pad.relative_to(STATIC).as_posix().startswith("css/"):
            doel = PUBLIC / pad.relative_to(STATIC)
            doel.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(pad, doel)
    schrijf("/sitemap.xml", env.get_template("sitemap.xml").render(paginas=sorted(paginas)))
    schrijf("/robots.txt", f"User-agent: *\nDisallow:\nSitemap: {site['url']}/sitemap.xml\n")
    gegenereerd = set(paginas) | {"/nieuws/index.xml", "/sitemap.xml", "/robots.txt", "/404.html"}
    schrijf("/.htaccess", htaccess(site, gegenereerd, fotos))

    print(f"Klaar: {len(paginas)} pagina's, {len(alle)} uitrukken, "
          f"{len(fotos.gemaakt)} afbeeldingen in {PUBLIC.relative_to(ROOT)}/")


if __name__ == "__main__":
    bouw()

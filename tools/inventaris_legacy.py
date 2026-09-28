"""URL-inventaris van de oude Hugo-site (fase 1).

Leest de build-output van legacy/ en schrijft per URL een voorstel:
200 (blijft bestaan), 301 (doorverwijzing) of 410 (bewust weg, besluit Sven 27-09-2026).

Gebruik:
    hugo -s legacy -d <map>
    python tools/inventaris_legacy.py <map> > data/legacy-urls.csv

Alleen standaardbibliotheek, werkt op Windows, macOS en Linux.
"""

import csv
import re
import sys
from pathlib import Path

LEGACY = Path(__file__).resolve().parent.parent / "legacy"

PAGINAS = {
    "/",
    "/betekenis-p2000-meldingen/",
    "/disclaimer/",
    "/nieuws/",
    "/over-ons/",
    "/posten-kennemerland/",
    "/voertuigen/",
}

# Voertuigen die niet meer in gebruik zijn: geen eigen pagina meer.
VOERTUIGEN_WEG = {"12-2031", "12-2061"}

# Foto's die bewust niet meer op de site staan (besluit Sven 28-09-2026): de oude 12-2001
# (voorganger van de huidige dienstbus) en de binnenkant van 12-2030.
FOTOS_WEG = {"/img/voertuigen/12-2001/IMG_4955.jpg", "/img/voertuigen/12-2001/IMG_4956.jpg", "/img/voertuigen/12-2001/IMG_4957.jpg", "/img/voertuigen/12-2001/IMG_4958.jpg", "/img/voertuigen/12-2030/DSC06422.jpg", "/img/voertuigen/12-2030/DSC06430.jpg"}

# Favicons en manifest die op hetzelfde pad blijven; overige icoonformaten gaan via 301.
ICONEN_BLIJVEN = {
    "/favicon.ico",
    "/favicon-16x16.png",
    "/favicon-32x32.png",
    "/apple-touch-icon.png",
    "/apple-touch-icon-precomposed.png",
    "/safari-pinned-tab.svg",
    "/mstile-150x150.png",
    "/manifest.json",
    "/browserconfig.xml",
}


def gebruikte_afbeeldingen():
    """Namen van afbeeldingen waarnaar content, data of config verwijzen."""
    tekst = []
    for map_ in ("content", "data"):
        for p in (LEGACY / map_).rglob("*"):
            # Features en testimonials stonden uit op de oude site.
            if p.is_file() and not {"features", "testimonials"} & set(p.parts):
                tekst.append(p.read_text(encoding="utf-8", errors="replace"))
    tekst.append((LEGACY / "config.toml").read_text(encoding="utf-8", errors="replace"))
    return "\n".join(tekst)


def urls(build):
    for p in sorted(build.rglob("*")):
        if not p.is_file():
            continue
        rel = "/" + p.relative_to(build).as_posix()
        if rel.endswith("/index.html"):
            rel = rel[: -len("index.html")]
        yield rel


def is_alias(build, url):
    if not url.endswith("/"):
        return False
    html = (build / url.lstrip("/") / "index.html").read_text(encoding="utf-8", errors="replace")
    return 'http-equiv="refresh"' in html


def classificeer(url, build, bronnen):
    m = re.fullmatch(r"/(12-20\d\d)/", url)
    if m:
        if m.group(1) in VOERTUIGEN_WEG:
            return "voertuig", "301", "/voertuigen/"
        return "voertuig", "301", f"/voertuigen/{m.group(1)}/"
    m = re.fullmatch(r"/(20\d\d)/", url)
    if m:
        return "uitrukken", "301", f"/uitrukken/{m.group(1)}/"
    if url.startswith("/nieuws/20"):
        return "nieuwsartikel", "200", url
    if url == "/nieuws/index.xml":
        return "feed", "200", url
    if url == "/index.xml":
        return "feed", "301", "/nieuws/index.xml"
    if url == "/nieuws/page/1/":
        return "paginering", "301", "/nieuws/"
    if re.fullmatch(r"/nieuws/page/\d+/", url):
        return "paginering", "200", url
    if url == "/page/1/":
        return "paginering", "301", "/"
    m = re.fullmatch(r"/page/(\d+)/", url)
    if m:
        return "paginering", "301", f"/nieuws/page/{m.group(1)}/"
    if url.startswith(("/tags/", "/categories/")):
        return "taxonomie", "301", "/nieuws/"
    if url == "/p2000/betekenis-p2000-meldingen/":
        return "alias", "301", "/betekenis-p2000-meldingen/"
    if url in PAGINAS:
        return "pagina", "200", url
    if url in ("/sitemap.xml", "/robots.txt", "/404.html"):
        return "systeem", "200", url
    if url in ICONEN_BLIJVEN:
        return "icoon", "200", url
    if re.fullmatch(r"/(android-chrome|apple-touch-icon)-[\w-]+\.png", url):
        return "icoon", "301", "/apple-touch-icon.png"
    if url.startswith(("/css/", "/js/")):
        return "thema-asset", "410", ""
    if url in FOTOS_WEG:
        return "afbeelding-verwijderd", "410", ""
    if url.startswith("/img/"):
        naam = url.rsplit("/", 1)[1]
        if any(v in url or v.replace("-", "") in naam for v in VOERTUIGEN_WEG):
            return "afbeelding-voertuig-weg", "410", ""
        if url.startswith(("/img/nieuws/", "/img/voertuigen/", "/img/carousel/", "/img/clients/12")) or naam in (
            "logo.png",
            "logo-small.png",
            "word_jij_onze_vrijwilliger.png",
        ):
            if naam in bronnen:
                return "afbeelding", "301", "nieuw pad na normalisatie (fase 3)"
            return "afbeelding-ongebruikt", "410", ""
        if naam in bronnen:  # bijv. standard_news_image.jpeg als banner van een artikel
            return "afbeelding", "301", "nieuw pad na normalisatie (fase 3)"
        return "thema-afbeelding", "410", ""
    return "onbekend", "vraag", ""


def main():
    if len(sys.argv) != 2:
        sys.exit("gebruik: python tools/inventaris_legacy.py <hugo-build-map>")
    build = Path(sys.argv[1])
    bronnen = gebruikte_afbeeldingen()
    w = csv.writer(sys.stdout, lineterminator="\n")
    w.writerow(["url", "soort", "actie", "doel"])
    for url in urls(build):
        soort, actie, doel = classificeer(url, build, bronnen)
        if soort in ("pagina", "taxonomie", "paginering") and is_alias(build, url) and actie == "200":
            soort = "alias"
        w.writerow([url, soort, actie, doel])


if __name__ == "__main__":
    main()

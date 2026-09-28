"""Controleert een gepubliceerde site (livegang-checklist, MIGRATIE.md hoofdstuk 8).

Gebruik:
    python tools/controleer_live.py https://v2.brandweeruitgeest.nl
    python tools/controleer_live.py https://brandweeruitgeest.nl --www

Controleert:
- elke oude URL uit data/legacy-urls.csv: de vastgelegde 200, 301 of 410; een 301 moet
  (binnen drie stappen) op een 200 op dezelfde site uitkomen;
- elke pagina uit de sitemap geeft 200;
- securityheaders precies zoals in CLAUDE.md, caching van HTML en gehashte bestanden;
- http gaat met 301 naar https, een onbekende URL geeft de eigen 404, het manifest is niet op te vragen;
- X-Robots-Tag noindex alleen op v2.; met --www ook de 301 van www naar zonder www.

Alleen standaardbibliotheek. Exitcode 1 als er iets niet klopt.
"""

import argparse
import csv
import http.client
import os
import re
import ssl
import sys
import time
from pathlib import Path
from urllib.parse import urljoin, urlsplit

ROOT = Path(__file__).resolve().parent.parent

HEADERS = {
    "strict-transport-security": "max-age=31536000; includeSubDomains",
    "content-security-policy": "default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; "
                               "font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; "
                               "form-action 'self'; upgrade-insecure-requests",
    "x-content-type-options": "nosniff",
    "referrer-policy": "strict-origin-when-cross-origin",
    "cross-origin-opener-policy": "same-origin",
    "permissions-policy": "geolocation=(), camera=(), microphone=(), browsing-topics=()",
}

fouten = []


def fout(tekst):
    fouten.append(tekst)
    print("FOUT:", tekst)


def verbinding(d):
    """Verbinding naar de site, via een proxy als HTTPS_PROXY/HTTP_PROXY gezet is."""
    proxy = os.environ.get("HTTPS_PROXY" if d.scheme == "https" else "HTTP_PROXY") \
        or os.environ.get("https_proxy" if d.scheme == "https" else "http_proxy")
    if d.scheme == "https":
        ctx = ssl.create_default_context(cafile=os.environ.get("SSL_CERT_FILE"))
        if proxy:
            p = urlsplit(proxy)
            c = http.client.HTTPSConnection(p.hostname, p.port or 8080, timeout=20, context=ctx)
            c.set_tunnel(d.netloc)
            return c
        return http.client.HTTPSConnection(d.netloc, timeout=20, context=ctx)
    if proxy:
        p = urlsplit(proxy)
        c = http.client.HTTPConnection(p.hostname, p.port or 8080, timeout=20)
        c.set_tunnel(d.netloc, 80)
        return c
    return http.client.HTTPConnection(d.netloc, timeout=20)


def vraag(url, methode="HEAD"):
    """(status, headers, body) zonder redirects te volgen."""
    d = urlsplit(url)
    for poging in range(3):
        try:
            c = verbinding(d)
            pad = (d.path or "/") + (f"?{d.query}" if d.query else "")
            c.request(methode, pad, headers={"User-Agent": "brandweeruitgeest-controle"})
            r = c.getresponse()
            body = r.read() if methode == "GET" else b""
            return r.status, {k.lower(): v for k, v in r.getheaders()}, body
        except OSError as e:
            if poging == 2:
                return 0, {}, str(e).encode()
            time.sleep(2)


def volg(url, max_stappen=3):
    """Volgt redirects; geeft (laatste status, laatste url)."""
    for _ in range(max_stappen + 1):
        status, h, _ = vraag(url)
        if status in (301, 302, 307, 308) and "location" in h:
            url = urljoin(url, h["location"])
            continue
        return status, url
    return 0, url


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("site", help="bijv. https://v2.brandweeruitgeest.nl")
    ap.add_argument("--www", action="store_true", help="ook www naar zonder www controleren")
    args = ap.parse_args()
    site = args.site.rstrip("/")
    if not re.fullmatch(r"https://(v2\.)?brandweeruitgeest\.nl", site):
        sys.exit("Alleen https://brandweeruitgeest.nl of https://v2.brandweeruitgeest.nl")
    host = urlsplit(site).netloc

    # 1. Oude URL's.
    with (ROOT / "data" / "legacy-urls.csv").open(encoding="utf-8", newline="") as f:
        oud = list(csv.DictReader(f))
    for r in oud:
        status, h, _ = vraag(site + r["url"])
        if str(status) != r["actie"]:
            fout(f"{r['url']}: {status}, verwacht {r['actie']}")
        elif status == 301:
            eind, waar = volg(urljoin(site + r["url"], h.get("location", "")))
            if eind != 200 or urlsplit(waar).netloc != host:
                fout(f"{r['url']}: 301 komt uit op {eind} {waar}")
    print(f"Oude URL's: {len(oud)} gecontroleerd.")

    # 2. Pagina's uit de sitemap.
    status, _, body = vraag(site + "/sitemap.xml", "GET")
    paginas = re.findall(r"<loc>([^<]+)</loc>", body.decode("utf-8", "replace")) if status == 200 else []
    if not paginas:
        fout(f"/sitemap.xml: {status} of leeg")
    for loc in paginas:
        pad = urlsplit(loc).path
        s, _, _ = vraag(site + pad)
        if s != 200:
            fout(f"{pad} (sitemap): {s}")
    print(f"Sitemap: {len(paginas)} pagina's gecontroleerd.")

    # 3. Headers en caching.
    status, h, body = vraag(site + "/", "GET")
    if status != 200:
        fout(f"/: {status}")
    for naam, waarde in HEADERS.items():
        if h.get(naam) != waarde:
            fout(f"header {naam}: '{h.get(naam)}', verwacht '{waarde}'")
    if "max-age=300" not in h.get("cache-control", ""):
        fout(f"HTML cache-control: '{h.get('cache-control')}'")
    css = re.search(r'href="(/[^"]+\.[0-9a-f]{8}\.css)"', body.decode("utf-8", "replace"))
    if css:
        _, hc, _ = vraag(site + css.group(1))
        if "immutable" not in hc.get("cache-control", ""):
            fout(f"{css.group(1)}: cache-control '{hc.get('cache-control')}'")
    else:
        fout("geen gehashte stylesheet gevonden op /")
    robots = h.get("x-robots-tag", "")
    if host.startswith("v2.") and "noindex" not in robots:
        fout("v2: X-Robots-Tag noindex ontbreekt")
    if not host.startswith("v2.") and robots:
        fout(f"hoofddomein: X-Robots-Tag '{robots}' moet weg")

    # 4. Overige.
    status, h, _ = vraag(f"http://{host}/over-ons/")
    if status != 301 or not h.get("location", "").startswith(f"https://{host}/"):
        fout(f"http naar https: {status} {h.get('location')}")
    status, _, body = vraag(site + "/bestaat-niet-" + str(int(time.time())) + "/", "GET")
    if status != 404 or b"Brandweer Uitgeest" not in body:
        fout(f"eigen 404-pagina: {status}")
    status, _, _ = vraag(site + "/.deploy-manifest.json")
    if status not in (403, 404):
        fout(f"/.deploy-manifest.json is op te vragen: {status}")
    if args.www:
        status, h, _ = vraag(f"https://www.{host}/over-ons/")
        if status != 301 or h.get("location") != f"https://{host}/over-ons/":
            fout(f"www naar zonder www: {status} {h.get('location')}")

    print(f"Klaar: {len(fouten)} fout(en).")
    sys.exit(1 if fouten else 0)


if __name__ == "__main__":
    main()

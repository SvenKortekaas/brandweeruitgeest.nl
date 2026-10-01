"""Plaatst een nieuwe P2000-uitruk op Facebook en Instagram (besluit Sven 01-10-2026).

Gebruik (normaal via .github/workflows/p2000.yml, na het publiceren van de site):
    python tools/sociaal.py facebook       # post op de Facebook-pagina
    python tools/sociaal.py instagram      # post op Instagram
    python tools/sociaal.py facebook --droog   # alleen tonen, niets posten
    python tools/sociaal.py controleer         # alleen lezen: kloppen token, pagina en account?

De uitruk komt uit de omgevingsvariabele UITRUK (JSON van import_p2000.py). Alleen regels met
publiceren=ja worden gepost, met dezelfde gegevens als op de site: prio, melding, straat, plaats.

Nodig in de GitHub-omgeving p2000 (Sven): META_TOKEN (paginatoken dat niet verloopt),
FB_PAGINA_ID en IG_ACCOUNT_ID. Ontbreken ze, dan wordt er niets gepost en slaagt de stap.

De afbeelding (verplicht voor Instagram) maakt build.py met maak_afbeelding() en staat op
de site onder /sociaal/; Facebook en Instagram halen hem daar op.
"""

import argparse
import datetime as dt
import json
import os
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

import yaml
from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
GRAPH = "https://graph.facebook.com/v23.0"  # versie van de Graph API van Meta
MAANDEN = ["januari", "februari", "maart", "april", "mei", "juni", "juli", "augustus",
           "september", "oktober", "november", "december"]
DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag", "zaterdag", "zondag"]
ROOD = (179, 0, 27)
WIT = (255, 255, 255)
MAAT = 1080
WERVING = "Wil jij de volgende keer ook mee? Word lid van brandweer Uitgeest!"
DAGEN_BEWAREN = 7  # build.py maakt afbeeldingen voor P2000-uitrukken van de laatste zoveel dagen


def site():
    return yaml.safe_load((ROOT / "data" / "site.yaml").read_text(encoding="utf-8"))


def moment(regel):
    return dt.datetime.fromisoformat(f"{regel['datum']} {regel['tijd'] or '00:00'}")


def afbeelding_pad(regel):
    """Pad op de site, bijv. /sociaal/uitruk-2026-10-01-0347.jpg."""
    return f"/sociaal/uitruk-{regel['datum']}-{(regel['tijd'] or '0000').replace(':', '')}.jpg"


def datum_tekst(regel):
    m = moment(regel)
    tekst = f"{DAGEN[m.weekday()]} {m.day} {MAANDEN[m.month - 1]} {m.year}"
    return f"{tekst}, {regel['tijd']}" if regel["tijd"] else tekst


def regels_tekst(regel):
    adres = ", ".join(x for x in (regel["adres"], regel["plaats"]) if x)
    melding = f"Prio {regel['prio']}: {regel['melding']}" if regel["prio"] else regel["melding"]
    return melding, adres


def bericht(regel, platform):
    melding, adres = regels_tekst(regel)
    gegevens = site()
    url = f"{gegevens['url']}/uitrukken/{regel['datum'][:4]}/"
    delen = ["Uitruk brandweer Uitgeest", "", melding, adres, datum_tekst(regel).capitalize(), "",
             WERVING]  # werving (besluit Sven 01-10-2026)
    if platform == "instagram":  # links zijn op Instagram niet klikbaar
        delen += ["Kijk voor de vacature en alle uitrukken op brandweeruitgeest.nl", "",
                  "#brandweer #brandweeruitgeest #uitgeest #112 #heldengezocht"]
    else:
        delen += [f"Bekijk de vacature: {gegevens['werving']['link']}", "",
                  f"Alle uitrukken: {url}"]
    return "\n".join(delen)


def _font(grootte):
    return ImageFont.load_default(size=grootte)


def _regels(tekst, font, breedte, teken):
    """Breekt tekst af op woorden zodat elke regel binnen de breedte past."""
    uit, regel = [], ""
    for woord in tekst.split():
        proef = f"{regel} {woord}".strip()
        if teken.textlength(proef, font=font) <= breedte or not regel:
            regel = proef
        else:
            uit.append(regel)
            regel = woord
    if regel:
        uit.append(regel)
    return uit


def maak_afbeelding(regel, doel):
    """Vierkante JPEG (1080 x 1080) in de huisstijl, zonder metadata."""
    im = Image.new("RGB", (MAAT, MAAT), ROOD)
    teken = ImageDraw.Draw(im)
    marge = 90
    logo_pad = ROOT / "static" / "logo.png"
    y = marge
    if logo_pad.exists():
        with Image.open(logo_pad) as logo:
            logo = logo.convert("RGBA")
            logo.thumbnail((MAAT - 2 * marge, 160))
            vlak = Image.new("RGBA", (logo.width + 40, logo.height + 40), WIT + (255,))
            vlak.alpha_composite(logo, (20, 20))
            im.paste(vlak.convert("RGB"), (marge, y))
            y += vlak.height + 70
    teken.text((marge, y), "UITRUK", font=_font(64), fill=WIT)
    y += 100
    melding, adres = regels_tekst(regel)
    groot = _font(80)
    for r in _regels(melding, groot, MAAT - 2 * marge, teken)[:4]:
        teken.text((marge, y), r, font=groot, fill=WIT)
        y += 100
    y += 30
    middel = _font(52)
    for r in _regels(adres, middel, MAAT - 2 * marge, teken)[:2] + [datum_tekst(regel).capitalize()]:
        teken.text((marge, y), r, font=middel, fill=WIT)
        y += 70
    teken.text((marge, MAAT - marge - 40), "brandweeruitgeest.nl", font=_font(44), fill=WIT)
    doel.parent.mkdir(parents=True, exist_ok=True)
    im.save(doel, "JPEG", quality=85, optimize=True)


def recente_p2000(jaren, vandaag):
    """P2000-uitrukken (publiceren=ja) van de laatste DAGEN_BEWAREN dagen, voor build.py."""
    grens = vandaag - dt.timedelta(days=DAGEN_BEWAREN)
    for regels in jaren.values():
        for r in regels:
            if r["bron"] == "p2000" and r["publiceren"] == "ja" and r["datum"] >= grens:
                yield r


# Meta Graph API

def graph(pad, velden, methode="POST"):
    data = urllib.parse.urlencode(velden).encode()
    if methode == "GET":
        verzoek = urllib.request.Request(f"{GRAPH}/{pad}?{data.decode()}")
    else:
        verzoek = urllib.request.Request(f"{GRAPH}/{pad}", data=data, method="POST")
    try:
        with urllib.request.urlopen(verzoek, timeout=60) as antwoord:
            return json.load(antwoord)
    except urllib.error.HTTPError as e:
        # De foutmelding van Meta bevat het token niet; wel de reden.
        sys.exit(f"FOUT van Meta ({e.code}): {e.read().decode(errors='replace')[:500]}")


def facebook(regel, token, pagina, afbeelding_url):
    uit = graph(f"{pagina}/photos", {"url": afbeelding_url, "message": bericht(regel, "facebook"),
                                     "access_token": token})
    print(f"Facebook: geplaatst ({uit.get('post_id') or uit.get('id')}).")


def instagram(regel, token, account, afbeelding_url):
    media = graph(f"{account}/media", {"image_url": afbeelding_url,
                                       "caption": bericht(regel, "instagram"), "access_token": token})
    for _ in range(20):  # wachten tot Instagram de afbeelding heeft verwerkt
        status = graph(media["id"], {"fields": "status_code", "access_token": token}, "GET")
        if status.get("status_code") == "FINISHED":
            break
        if status.get("status_code") == "ERROR":
            sys.exit("FOUT: Instagram kon de afbeelding niet verwerken")
        time.sleep(3)
    uit = graph(f"{account}/media_publish", {"creation_id": media["id"], "access_token": token})
    print(f"Instagram: geplaatst ({uit.get('id')}).")


def controleer():
    """Leest alleen: hoort het token bij de juiste pagina en het juiste Instagram-account?"""
    token = os.environ.get("META_TOKEN", "")
    pagina = os.environ.get("FB_PAGINA_ID", "")
    account = os.environ.get("IG_ACCOUNT_ID", "")
    if not (token and pagina and account):
        sys.exit("FOUT: META_TOKEN, FB_PAGINA_ID of IG_ACCOUNT_ID ontbreekt in de omgeving p2000")
    p = graph(pagina, {"fields": "name,instagram_business_account", "access_token": token}, "GET")
    print(f"Facebook-pagina: {p.get('name')}")
    gekoppeld = (p.get("instagram_business_account") or {}).get("id")
    i = graph(account, {"fields": "username", "access_token": token}, "GET")
    print(f"Instagram-account: @{i.get('username')}")
    if gekoppeld != account:
        sys.exit("FOUT: het Instagram-account is niet gekoppeld aan deze Facebook-pagina")
    print("In orde: token, pagina en Instagram-account horen bij elkaar. Er is niets gepost.")


def main():
    if sys.argv[1:] == ["controleer"]:
        return controleer()
    ap = argparse.ArgumentParser(description="Plaatst een uitruk op Facebook of Instagram.")
    ap.add_argument("platform", choices=["facebook", "instagram"])
    ap.add_argument("--droog", action="store_true", help="alleen tonen, niets posten")
    args = ap.parse_args()

    regel = json.loads(os.environ.get("UITRUK") or "{}")
    if not regel:
        sys.exit("FOUT: geen uitruk meegegeven (UITRUK)")
    if regel.get("publiceren") != "ja":
        print("Niet gepost: deze uitruk staat niet op de site (publiceren=nee).")
        return
    afbeelding_url = site()["url"] + afbeelding_pad(regel)
    print(f"Afbeelding: {afbeelding_url}\n\n{bericht(regel, args.platform)}\n")
    if args.droog:
        print("Droog: niets gepost.")
        return

    token = os.environ.get("META_TOKEN", "")
    doel = os.environ.get("FB_PAGINA_ID" if args.platform == "facebook" else "IG_ACCOUNT_ID", "")
    if not token or not doel:
        print("Niet gepost: META_TOKEN, FB_PAGINA_ID of IG_ACCOUNT_ID ontbreekt in de omgeving p2000.")
        return
    if args.platform == "facebook":
        facebook(regel, token, doel, afbeelding_url)
    else:
        instagram(regel, token, doel, afbeelding_url)


if __name__ == "__main__":
    main()

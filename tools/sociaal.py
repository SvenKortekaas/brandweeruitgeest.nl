"""Plaatst een nieuwe P2000-uitruk op Facebook en Instagram (besluit Sven 01-10-2026).

Gebruik (normaal via .github/workflows/p2000.yml, na het publiceren van de site):
    python tools/sociaal.py facebook       # post op de Facebook-pagina
    python tools/sociaal.py instagram      # post op Instagram
    python tools/sociaal.py facebook --droog   # alleen tonen, niets posten
    python tools/sociaal.py controleer         # alleen lezen: kloppen token, pagina en account?
    python tools/sociaal.py facebook --uitruk "2026-10-20 11:56"   # bestaande uitruk alsnog
                                               # (workflow "Uitruk alsnog op Facebook en Instagram")

De uitruk komt uit de omgevingsvariabele UITRUK (JSON van import_p2000.py). Alleen regels met
publiceren=ja worden gepost, met dezelfde gegevens als op de site: prio, melding, straat, plaats.

Nodig in de GitHub-omgeving p2000 (Sven): META_TOKEN (token van de systeemgebruiker dat
niet verloopt; voor Facebook vraagt het script daarmee het paginatoken op),
FB_PAGINA_ID en IG_ACCOUNT_ID. Ontbreken ze, dan wordt er niets gepost en slaagt de stap.

De afbeelding (verplicht voor Instagram) maakt build.py met maak_afbeelding() en staat op
de site onder /sociaal/; Facebook en Instagram halen hem daar op.
"""

import argparse
import csv
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


def lees_jaren():
    """Uitrukken van dit en vorig jaar, zoals build.py ze aan recente_p2000() geeft."""
    jaren = {}
    for jaar in (dt.date.today().year - 1, dt.date.today().year):
        pad = ROOT / "data" / "uitrukken" / f"{jaar}.csv"
        if pad.exists():
            with pad.open(encoding="utf-8", newline="") as f:
                jaren[jaar] = [dict(r, datum=dt.date.fromisoformat(r["datum"])) for r in csv.DictReader(f)]
    return jaren


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

class MetaFout(Exception):
    """Fout van de Graph API. De tekst bevat het token niet; wel de reden."""

    def __init__(self, code, tekst):
        super().__init__(f"FOUT van Meta ({code}): {tekst[:500]}")
        self.tekst = tekst


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
        raise MetaFout(e.code, e.read().decode(errors="replace")) from None


def paginatoken(token, pagina):
    """Posten op een pagina kan alleen met een paginatoken. Het token van de systeemgebruiker
    (META_TOKEN) geeft dat token voor de pagina waar hij aan gekoppeld is. Met het token van de
    systeemgebruiker zelf weigert Meta het posten (melding over publish_actions)."""
    uit = graph(pagina, {"fields": "access_token", "access_token": token}, "GET")
    if not uit.get("access_token"):
        sys.exit("FOUT: geen paginatoken. Koppel de systeemgebruiker in Meta Business aan de pagina "
                 "(met volledige toegang) en geef de app de rechten pages_manage_posts en "
                 "pages_read_engagement.")
    return uit["access_token"]


def facebook(regel, token, pagina, afbeelding_url):
    uit = graph(f"{pagina}/photos", {"url": afbeelding_url, "message": bericht(regel, "facebook"),
                                     "access_token": paginatoken(token, pagina)})
    print(f"Facebook: geplaatst ({uit.get('post_id') or uit.get('id')}).")


def instagram_container(token, account, afbeelding_url, caption):
    """Maakt een mediacontainer (nog niet gepubliceerd) en wacht tot Instagram de afbeelding
    heeft verwerkt. Lukt het ophalen van de afbeelding niet meteen, dan nog twee keer proberen."""
    for poging in range(3):
        try:
            media = graph(f"{account}/media", {"image_url": afbeelding_url, "caption": caption,
                                               "access_token": token})
            break
        except MetaFout as e:
            if poging == 2 or '"code":9004' not in e.tekst:
                raise
            print(f"Instagram kon de afbeelding niet ophalen, over 30 seconden opnieuw ({e})")
            time.sleep(30)
    for _ in range(20):  # wachten tot Instagram de afbeelding heeft verwerkt
        status = graph(media["id"], {"fields": "status_code", "access_token": token}, "GET")
        if status.get("status_code") == "FINISHED":
            return media["id"]
        if status.get("status_code") == "ERROR":
            sys.exit("FOUT: Instagram kon de afbeelding niet verwerken")
        time.sleep(3)
    sys.exit("FOUT: Instagram is na een minuut nog niet klaar met de afbeelding")


def instagram(regel, token, account, afbeelding_url):
    container = instagram_container(token, account, afbeelding_url, bericht(regel, "instagram"))
    uit = graph(f"{account}/media_publish", {"creation_id": container, "access_token": token})
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
    paginatoken(token, pagina)
    print("Paginatoken voor Facebook: in orde.")
    # Kan Instagram de afbeelding van de site ophalen? Een container zonder media_publish
    # verschijnt niet op Instagram en vervalt na 24 uur.
    regels = sorted(recente_p2000(lees_jaren(), dt.date.today()), key=moment)
    if regels:
        url = site()["url"] + afbeelding_pad(regels[-1])
        instagram_container(token, account, url, "")
        print(f"Instagram kan de afbeelding ophalen: {url}")
    else:
        print("Geen recente P2000-uitruk met afbeelding; ophalen door Instagram niet getest.")
    print("In orde: token, pagina en Instagram-account horen bij elkaar. Er is niets gepost.")


def zoek_uitruk(tekst):
    """Zoekt een P2000-uitruk van de laatste DAGEN_BEWAREN dagen op datum en tijd. Alleen die
    hebben een afbeelding op de site."""
    for r in recente_p2000(lees_jaren(), dt.date.today()):
        if f"{r['datum']} {r['tijd']}" == " ".join(tekst.split()):
            return dict(r, datum=r["datum"].isoformat())
    sys.exit(f"FOUT: geen P2000-uitruk op de site van de laatste {DAGEN_BEWAREN} dagen op '{tekst}'")


def main():
    if sys.argv[1:] == ["controleer"]:
        return controleer()
    ap = argparse.ArgumentParser(description="Plaatst een uitruk op Facebook of Instagram.")
    ap.add_argument("platform", choices=["facebook", "instagram"])
    ap.add_argument("--droog", action="store_true", help="alleen tonen, niets posten")
    ap.add_argument("--uitruk", metavar="'JJJJ-MM-DD UU:MM'",
                    help="een bestaande P2000-uitruk alsnog posten, in plaats van UITRUK")
    args = ap.parse_args()

    if args.uitruk:
        regel = zoek_uitruk(args.uitruk)
    else:
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
    try:
        main()
    except MetaFout as e:
        sys.exit(str(e))

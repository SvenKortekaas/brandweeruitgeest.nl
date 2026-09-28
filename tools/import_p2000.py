"""Zet één P2000-melding om in een uitruk in data/uitrukken/JJJJ.csv.

Gebruik (normaal via de workflow .github/workflows/p2000.yml, gestart door Home Assistant):
    python tools/import_p2000.py --tijdstip "2026-09-27 00:35:39" \\
        --tekst "P 1 BNH-01 BR wegvervoer Broekpolderweg Uitgeest 122030" --capcodes "107711"
    ... --apply     # schrijft de regel; zonder --apply alleen tonen

Zonder argumenten worden P2000_TIJDSTIP, P2000_TEKST en P2000_CAPCODES uit de omgeving gelezen.
De invoer komt van buiten en wordt behandeld als data: alleen het vaste formaat wordt geaccepteerd.

Uitkomst (exitcode):
    0  nieuw (geschreven met --apply) of bewust overgeslagen (al aanwezig, intrekking, ...)
    2  afgekeurd: niets geschreven, de reden staat in de uitvoer

Regels (CLAUDE.md, PLAN-P2000.md):
- alleen capcode 0107711 (Vrijwilligers) telt;
- prio 1, 2 of 3; melding via tools/p2000.yaml; alleen straat (of weg en hectometer) en plaats;
- geen huisnummers, objectnamen of eenheidsnummers; vrije tekst wordt nooit overgenomen;
- bij twijfel niet publiceren: de regel wordt dan niet geschreven en de import faalt zichtbaar.
"""

import argparse
import csv
import datetime as dt
import os
import re
import sys
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

ROOT = Path(__file__).resolve().parent.parent
UITRUKKEN = ROOT / "data" / "uitrukken"
INSTELLINGEN = ROOT / "tools" / "p2000.yaml"
KOLOMMEN = ["nr", "datum", "tijd", "prio", "melding", "adres", "plaats", "bron", "publiceren"]
TIJDZONE = ZoneInfo("Europe/Amsterdam")

MAX_LENGTE = 300
TOEGESTAAN = re.compile(r"^[\w\s.,:;/()'&+\-]*$")
PRIO = re.compile(r"^\s*(?:P|PRIO)\s*(\d)\b\s*", re.I)
REGIO = re.compile(r"^(?:[A-Z]{2,4}-\d{1,2}\b\s*)+")                  # BNH-01
EXTRA = re.compile(r"\((?:dia|ter info)[^)]*\)|\bdia\s*:\s*\w+", re.I)  # (dia: ja)
EENHEDEN = re.compile(r"(?:\s+\d{4,7})+\s*$")                          # 122030 122002
WEG = re.compile(r"\b[AN]\s?\d{1,3}\b.*$")                             # A9 Li 61,0 / N203 57,6
HUISNUMMER = re.compile(r"\s+\d{1,5}\s?[a-zA-Z]{0,2}(?:\s?-\s?\d+)?$")
INITIALEN = re.compile(r"^(?:[A-Z]\.)+$")
STRAATEINDE = re.compile(
    r"(straat|weg|laan|plein|dijk|kade|pad|gracht|singel|hof|dreef|park|erf|werf|baan|steeg|wal"
    r"|veld|geest|duin|meer|polder|burg|wijk|kamp|akker|land|loop|zoom|brink|markt|haven|dam|oord"
    r"|ring|tuin|hoek|buurt|rak|horn|molen|bonkelaar|boterbloem)$", re.I)


class Afgekeurd(Exception):
    pass


def lees_instellingen():
    with INSTELLINGEN.open(encoding="utf-8") as f:
        return yaml.safe_load(f)


def lees_jaar(jaar):
    pad = UITRUKKEN / f"{jaar}.csv"
    if not pad.exists():
        return []
    with pad.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def schrijf_jaar(jaar, regels):
    regels.sort(key=lambda r: (r["datum"], r["tijd"] or ""))
    for i, r in enumerate(regels, start=1):
        r["nr"] = str(i)
    pad = UITRUKKEN / f"{jaar}.csv"
    with pad.open("w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=KOLOMMEN, lineterminator="\n")
        w.writeheader()
        w.writerows(regels)


def bekende_straten():
    """Straten die al in de uitrukken staan (zonder huisnummer), voor het herkennen van het adres."""
    straten = set()
    for pad in UITRUKKEN.glob("*.csv"):
        with pad.open(encoding="utf-8", newline="") as f:
            for r in csv.DictReader(f):
                a = HUISNUMMER.sub("", r["adres"].strip())
                if a and r["plaats"] and not WEG.search(a) and not re.search(r"\d", a):
                    straten.add(a.lower())
    return straten


def lees_tijdstip(tekst, nu):
    s = tekst.strip().replace("T", " ")
    try:
        t = dt.datetime.fromisoformat(s)
    except ValueError:
        raise Afgekeurd(f"ongeldig tijdstip '{tekst[:40]}'")
    t = t.replace(tzinfo=TIJDZONE) if t.tzinfo is None else t.astimezone(TIJDZONE)
    if t > nu + dt.timedelta(minutes=10) or t < nu - dt.timedelta(days=7):
        raise Afgekeurd(f"tijdstip {t:%d-%m-%Y %H:%M} ligt niet in de afgelopen 7 dagen")
    return t


def zoek_melding(rest, cfg):
    """(korte melding, rest van de tekst na de melding)."""
    laag = rest.lower()
    beste = None
    for begin, kort in cfg["meldingen"].items():
        b = begin.lower()
        if laag.startswith(b) and (len(laag) == len(b) or not laag[len(b)].isalnum()):
            if beste is None or len(b) > len(beste[0]):
                beste = (b, kort)
    if beste:
        return beste[1], rest[len(beste[0]):].strip()
    m = re.match(r"BR\s+([a-zé]+)\b", rest, re.I)
    if m:
        return f"Brand {m.group(1).lower()}", rest[m.end():].strip()
    raise Afgekeurd("melding niet herkend; voeg het begin toe aan 'meldingen' in tools/p2000.yaml")


def zoek_plaats(rest, cfg):
    for p in sorted(cfg["plaatsen"], key=len, reverse=True):
        if rest.lower().endswith(" " + p.lower()) or rest.lower() == p.lower():
            return rest[: len(rest) - len(p)].strip(), p
    raise Afgekeurd("geen bekende plaats aan het eind; voeg de plaats toe aan 'plaatsen' in tools/p2000.yaml")


def zoek_adres(rest, cfg, straten):
    """Alleen de straat (of weg met hectometer); objectnamen en huisnummers vallen weg."""
    w = WEG.search(rest)
    if w:
        return w.group(0).strip()
    rest = HUISNUMMER.sub("", rest).strip()
    woorden = rest.split()
    # 1. Langste bekende straat aan het eind.
    for n in range(len(woorden), 0, -1):
        kandidaat = " ".join(woorden[-n:])
        if kandidaat.lower() in straten:
            return kandidaat
    # 2. Laatste woord ziet eruit als een straatnaam, met voorvoegsels ervoor.
    if woorden and STRAATEINDE.search(woorden[-1]):
        voor = {v.lower() for v in cfg["straat_voorvoegsels"]}
        i = len(woorden) - 1
        while i > 0 and (woorden[i - 1].lower() in voor or INITIALEN.match(woorden[i - 1])):
            i -= 1
        # Voornaam vóór een tussenvoegsel ("Gerrit van Assendelftstraat").
        if 0 < i < len(woorden) - 1 and woorden[i].lower() in ("van", "de", "ter", "ten") \
                and woorden[i - 1][:1].isupper():
            i -= 1
        return " ".join(woorden[i:])
    raise Afgekeurd("straat niet herkend")


def verwerk(tijdstip, tekst, capcodes, cfg, straten, nu):
    """Geeft (status, regel of None, uitleg). status: nieuw, overgeslagen."""
    tekst = " ".join(tekst.split())
    if not tekst or len(tekst) > MAX_LENGTE or not TOEGESTAAN.match(tekst):
        raise Afgekeurd("tekst leeg, te lang of met onverwachte tekens")
    codes = {c.lstrip("0") for c in re.split(r"[\s,;]+", capcodes) if c.strip()}
    if cfg["capcode"].lstrip("0") not in codes:
        raise Afgekeurd(f"capcode {cfg['capcode']} staat niet in de melding")
    laag = tekst.lower()
    for woord in cfg["overslaan"]:
        if woord.lower() in laag:
            return "overgeslagen", None, f"bevat '{woord}'"
    t = lees_tijdstip(tijdstip, nu)
    m = PRIO.match(tekst)
    if not m:
        raise Afgekeurd("geen prio (P 1, P 2 of P 3) aan het begin")
    if m.group(1) not in ("1", "2", "3"):
        raise Afgekeurd(f"prio {m.group(1)} is geen 1, 2 of 3")
    rest = REGIO.sub("", tekst[m.end():]).strip()
    rest = EXTRA.sub(" ", rest)
    rest = EENHEDEN.sub("", " ".join(rest.split())).strip()
    melding, rest = zoek_melding(rest, cfg)
    rest, plaats = zoek_plaats(rest, cfg)
    adres = zoek_adres(rest, cfg, straten)
    regel = {"nr": "", "datum": t.date().isoformat(), "tijd": t.strftime("%H:%M"), "prio": m.group(1),
             "melding": melding, "adres": adres, "plaats": plaats, "bron": "p2000", "publiceren": "ja"}
    for woord in cfg.get("niet_publiceren", []):
        if woord.lower() in melding.lower():
            regel["publiceren"] = "nee"
    # Zelfde uitruk al aanwezig (herhaalalarm, opschaling, of dezelfde melding nog een keer)?
    venster = dt.timedelta(minutes=cfg["zelfde_uitruk_minuten"])
    bestaand = lees_jaar(t.year)
    for r in bestaand:
        if r["datum"] != regel["datum"] or not r["tijd"]:
            continue
        t2 = dt.datetime.fromisoformat(f"{r['datum']} {r['tijd']}").replace(tzinfo=TIJDZONE)
        if abs(t - t2) <= venster and (r["adres"].lower(), r["plaats"].lower()) == (adres.lower(), plaats.lower()):
            return "overgeslagen", None, f"al aanwezig als nr {r['nr']} ({r['datum']} {r['tijd']})"
    vandaag = sum(1 for r in bestaand if r["datum"] == regel["datum"] and r["bron"] == "p2000")
    if vandaag >= cfg["max_per_dag"]:
        raise Afgekeurd(f"al {vandaag} P2000-uitrukken op {regel['datum']}, maximum is {cfg['max_per_dag']}")
    return "nieuw", regel, ""


def samenvatting(regel_tekst):
    """Schrijft ook naar de samenvatting van de GitHub-run, als die er is."""
    print(regel_tekst)
    pad = os.environ.get("GITHUB_STEP_SUMMARY")
    if pad:
        with open(pad, "a", encoding="utf-8") as f:
            f.write(regel_tekst + "\n\n")


def main():
    ap = argparse.ArgumentParser(description="Zet een P2000-melding om in een uitruk.")
    ap.add_argument("--tijdstip", default=os.environ.get("P2000_TIJDSTIP", ""))
    ap.add_argument("--tekst", default=os.environ.get("P2000_TEKST", ""))
    ap.add_argument("--capcodes", default=os.environ.get("P2000_CAPCODES", ""))
    ap.add_argument("--apply", action="store_true", help="regel echt schrijven")
    args = ap.parse_args()

    cfg = lees_instellingen()
    with (ROOT / "tools" / "meldingen.yaml").open(encoding="utf-8") as f:
        cfg["niet_publiceren"] = (yaml.safe_load(f) or {}).get("niet_publiceren") or []

    nu = dt.datetime.now(TIJDZONE)
    try:
        status, regel, uitleg = verwerk(args.tijdstip, args.tekst, args.capcodes, cfg, bekende_straten(), nu)
    except Afgekeurd as e:
        samenvatting(f"**Afgekeurd:** {e}.\n\nP2000-tekst: `{args.tekst[:MAX_LENGTE]}`")
        sys.exit(2)
    if status == "overgeslagen":
        samenvatting(f"Overgeslagen: {uitleg}.")
        return
    beschrijving = (f"{regel['datum']} {regel['tijd']}, prio {regel['prio']}, {regel['melding']}, "
                    f"{regel['adres']}, {regel['plaats']} (publiceren: {regel['publiceren']})")
    if not args.apply:
        samenvatting(f"Nieuw (niet geschreven, gebruik --apply): {beschrijving}")
        return
    jaar = int(regel["datum"][:4])
    regels = lees_jaar(jaar)
    regels.append(regel)
    schrijf_jaar(jaar, regels)
    samenvatting(f"Nieuwe uitruk: {beschrijving}")
    uitvoer = os.environ.get("GITHUB_OUTPUT")
    if uitvoer:
        with open(uitvoer, "a", encoding="utf-8") as f:
            f.write("nieuw=ja\n")


if __name__ == "__main__":
    main()

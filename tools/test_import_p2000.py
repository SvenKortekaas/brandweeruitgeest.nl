"""Test van tools/import_p2000.py: P2000-tekst naar de regel die op de site komt.

Gebruik:
    python tools/test_import_p2000.py

Draait in de workflow "Bouwen en publiceren". Schrijft niets; de bestaande uitrukken worden
vervangen door een vaste lijst, zodat de uitkomst niet van de data afhangt.
"""

import datetime as dt
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import import_p2000 as p  # noqa: E402

NU = dt.datetime(2026, 10, 21, 12, 0, tzinfo=p.TIJDZONE)
TIJDSTIP = "2026-10-21 11:56"

# P2000-tekst -> (prio, melding, adres, plaats)
NIEUW = {
    "P 1 BNH-01 BR wegvervoer Broekpolderweg Uitgeest 122030":
        ("1", "Brand wegvervoer", "Broekpolderweg", "Uitgeest"),
    "P 1 BNH-01 (Grote BR) BR woning (schoorsteen) Molenwerf Uitgeest 122030":
        ("1", "Grote brand woning schoorsteen", "Molenwerf", "Uitgeest"),
    "P 2 BNH-02 Stank/hind. lucht (Gaslekkage) (gaslucht) (buiten) Molenwerf Uitgeest 122030":
        ("2", "Gaslekkage", "Molenwerf", "Uitgeest"),
    "P 1 BNH-01 (Middel HV) HV weg A9 Li 60,1 Uitgeest 122030":
        ("1", "Hulpverlening weg (middel HV)", "A9 Li 60,1", "Uitgeest"),
    "P 1 BNH-02 Reanimatie Benesserlaan Uitgeest 122002":
        ("1", "Reanimatie", "Benesserlaan", "Uitgeest"),
    # Huisnummer weg, voornaam en tussenvoegsel blijven bij de straat.
    "P 2 BNH-01 BR woning Gerrit van Assendelftstraat 12 Uitgeest 122030":
        ("2", "Brand woning", "Gerrit van Assendelftstraat", "Uitgeest"),
    "P 2 BNH-01 BR woning Molenwerf 25a Uitgeest 122030":
        ("2", "Brand woning", "Molenwerf", "Uitgeest"),
    "P 1 BNH-01 (Pel. GW G3000 1) BR natuur Zeeweg Bloemendaal 122030":
        ("1", "Natuurbrand (waterpeloton)", "Zeeweg", "Bloemendaal"),
    "P 2 BNH-01 (aflossing) Herenweg Heemstede 122030":
        ("2", "Aflossing", "Herenweg", "Heemstede"),
    # Intrekbericht zonder eerdere alarmering: de uitruk komt er één keer bij.
    "P 1 BNH-01 (Intrekken Alarm Brw) BR woning Molenwerf Uitgeest 127131":
        ("1", "Brand woning", "Molenwerf", "Uitgeest"),
}

OVERGESLAGEN = [
    "P 2 BNH-01 Proefalarm kazerne Molenwerf Uitgeest",
]

AFGEKEURD = [
    "P 5 BNH-01 BR woning Molenwerf Uitgeest",               # prio buiten 1, 2, 3
    "P 1 BNH-01 Onbekend iets Molenwerf Uitgeest",           # melding niet in p2000.yaml
    "P 1 BNH-01 BR natuur Kennemerduinen Bloemendaal",       # geen straat: bij twijfel niet
    "P 1 BNH-01 BR woning Molenwerf Onbekendedorp",          # plaats niet in plaatsen.yaml
    "BR woning Molenwerf Uitgeest",                          # geen prio
]


def verwerk(tekst, bestaand=(), capcodes="0107711"):
    p.lees_jaar = lambda jaar: [dict(r) for r in bestaand]
    return p.verwerk(TIJDSTIP, tekst, capcodes, cfg, set(), NU)


def afgekeurd(tekst, **kw):
    try:
        verwerk(tekst, **kw)
    except p.Afgekeurd:
        return True
    return False


cfg = p.lees_instellingen()
cfg["niet_publiceren"] = []

for tekst, verwacht in NIEUW.items():
    status, regel, _ = verwerk(tekst)
    uit = (regel["prio"], regel["melding"], regel["adres"], regel["plaats"]) if regel else None
    assert status == "nieuw" and uit == verwacht, f"{tekst}\n  kreeg {status} {uit}\n  verwacht {verwacht}"

for tekst in OVERGESLAGEN:
    assert verwerk(tekst)[0] == "overgeslagen", tekst

for tekst in AFGEKEURD:
    assert afgekeurd(tekst), f"niet afgekeurd: {tekst}"

assert afgekeurd("P 1 BNH-01 BR woning Molenwerf Uitgeest", capcodes="0106530"), "andere capcode"

# Herhaalalarm, opschaling of intrekking binnen het venster: dezelfde uitruk.
eerder = [{"nr": "1", "datum": "2026-10-21", "tijd": "11:40", "prio": "1", "melding": "Brand woning",
           "adres": "Molenwerf", "plaats": "Uitgeest", "bron": "p2000", "publiceren": "ja"}]
for tekst in ("P 1 BNH-01 (Grote BR) BR woning Molenwerf Uitgeest",
              "P 1 BNH-01 (Intrekken Alarm Brw) BR woning Molenwerf Uitgeest"):
    assert verwerk(tekst, bestaand=eerder)[0] == "overgeslagen", tekst
assert verwerk("P 1 BNH-01 BR woning Benesserlaan Uitgeest", bestaand=eerder)[0] == "nieuw"

print(f"P2000-import: {len(NIEUW) + len(OVERGESLAGEN) + len(AFGEKEURD) + 4} gevallen in orde.")

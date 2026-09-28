"""Zet de gebouwde site (public/) via FTPS op de webserver.

Alleen standaardbibliotheek. Verbindt altijd met TLS en controleert het certificaat;
onversleuteld FTP wordt geweigerd.

Werking:
- Na elke upload staat op de server `.deploy-manifest.json` met de hash van elk bestand
  dat deze tool heeft geplaatst.
- Normale update: alleen gewijzigde en nieuwe bestanden uploaden, bestanden die niet meer
  in public/ staan verwijderen (alleen bestanden uit het vorige manifest).
- Eerste keer (`--opruimen`): alles op de server dat niet in public/ staat wordt verwijderd,
  behalve beschermde paden. Zonder manifest op de server weigert een normale update, zodat
  de livegang altijd bewust gebeurt.
- `.htaccess` gaat als laatste bestand omhoog: dat is het moment waarop de nieuwe site live is.
- Terugdraaien (`--terugdraaien`): zet alleen de oude tijdelijke `.htaccess` terug
  (doorverwijzing naar brandweer.nl, `tools/htaccess-terugdraaien`). De site is dan
  direct weer offline; de volgende gewone publicatie zet de nieuwe `.htaccess` terug.

Gegevens komen uit omgevingsvariabelen (GitHub Secrets), nooit uit de repo:
    FTP_SERVER, FTP_POORT (standaard 21), FTP_GEBRUIKER, FTP_WACHTWOORD,
    FTP_MAP (optioneel, map op de server; standaard de map waarin je na inloggen staat)

Gebruik:
    python tools/deploy.py public --droog            # alleen tonen wat er zou gebeuren
    python tools/deploy.py public                    # update
    python tools/deploy.py public --opruimen --droog # eerste keer, eerst kijken
    python tools/deploy.py public --opruimen         # eerste keer, echt
    python tools/deploy.py public --terugdraaien     # terug naar de tijdelijke doorverwijzing
"""

import argparse
import ftplib
import hashlib
import io
import json
import os
import ssl
import sys
from pathlib import Path, PurePosixPath

MANIFEST = ".deploy-manifest.json"

TERUGDRAAIEN = Path(__file__).resolve().parent / "htaccess-terugdraaien"

# Nooit verwijderen, ook niet bij --opruimen. Mappen gelden inclusief inhoud.
# Sven (27-09-2026): alles op de server mag weg. Alleen .well-known blijft, die is nodig
# om het HTTPS-certificaat te vernieuwen. Sven (28-09-2026): ook .cagefs en .cl.selector
# (van de hosting) blijven staan.
BESCHERMD = {".well-known", ".cagefs", ".cl.selector", MANIFEST}


def meld(tekst):
    print(tekst, flush=True)


def lokale_bestanden(bron):
    """{pad: sha256} voor alle bestanden in public/, met / als scheidingsteken."""
    uit = {}
    for p in sorted(bron.rglob("*")):
        if p.is_file():
            uit[p.relative_to(bron).as_posix()] = hashlib.sha256(p.read_bytes()).hexdigest()
    return uit


def verbind():
    ontbrekend = [n for n in ("FTP_SERVER", "FTP_GEBRUIKER", "FTP_WACHTWOORD") if not os.environ.get(n)]
    if ontbrekend:
        sys.exit(f"FOUT: omgevingsvariabele(n) ontbreken: {', '.join(ontbrekend)}")
    context = ssl.create_default_context(cafile=os.environ.get("FTP_CA_BESTAND") or None)
    ftp = ftplib.FTP_TLS(context=context, timeout=60)
    ftp.encoding = "utf-8"
    try:
        ftp.connect(os.environ["FTP_SERVER"], int(os.environ.get("FTP_POORT") or 21))
        ftp.auth()
    except ftplib.error_perm as e:
        sys.exit(f"FOUT: de server ondersteunt geen FTPS (AUTH TLS): {e}. Onversleuteld FTP wordt niet gebruikt.")
    except ssl.SSLError as e:
        sys.exit(f"FOUT: TLS-certificaat van de server niet geldig: {e}")
    ftp.login(os.environ["FTP_GEBRUIKER"], os.environ["FTP_WACHTWOORD"])
    ftp.prot_p()
    if os.environ.get("FTP_MAP"):
        ftp.cwd(os.environ["FTP_MAP"])
    return ftp


def is_beschermd(pad):
    return PurePosixPath(pad).parts[0] in BESCHERMD


def lijst_server(ftp, map_=""):
    """Alle bestanden op de server (relatief), recursief. Geeft (bestanden, mappen)."""
    bestanden, mappen = [], []
    try:
        items = list(ftp.mlsd(map_ or ".", facts=["type"]))
        for naam, feiten in items:
            if naam in (".", ".."):
                continue
            pad = f"{map_}/{naam}" if map_ else naam
            if feiten.get("type") == "dir":
                if is_beschermd(pad):
                    continue
                mappen.append(pad)
                b, m = lijst_server(ftp, pad)
                bestanden += b
                mappen += m
            elif feiten.get("type") == "file":
                bestanden.append(pad)
    except ftplib.error_perm as e:
        sys.exit(f"FOUT: kan de mappen op de server niet lezen (MLSD): {e}")
    return bestanden, mappen


def lees_manifest(ftp):
    buf = io.BytesIO()
    try:
        ftp.retrbinary(f"RETR {MANIFEST}", buf.write)
    except ftplib.error_perm:
        return None
    return json.loads(buf.getvalue().decode("utf-8"))


def maak_mappen(ftp, pad, bestaand):
    deel = PurePosixPath(pad).parent
    for i in range(1, len(deel.parts) + 1):
        m = "/".join(deel.parts[:i])
        if m and m not in bestaand:
            try:
                ftp.mkd(m)
            except ftplib.error_perm:
                pass  # bestaat al
            bestaand.add(m)


def upload(ftp, bron, pad, mappen):
    maak_mappen(ftp, pad, mappen)
    with (bron / pad).open("rb") as f:
        ftp.storbinary(f"STOR {pad}", f)


def terugdraaien(droog):
    inhoud = TERUGDRAAIEN.read_bytes()
    meld("Terugdraaien: .htaccess wordt de tijdelijke doorverwijzing naar brandweer.nl"
         f"{' (droog, er verandert niets)' if droog else ''}.")
    if droog:
        return
    ftp = verbind()
    ftp.storbinary("STOR .htaccess", io.BytesIO(inhoud))
    # Manifest bijwerken, zodat de volgende publicatie de echte .htaccess weer plaatst.
    vorig = lees_manifest(ftp)
    if vorig is not None:
        vorig.setdefault("bestanden", {})[".htaccess"] = hashlib.sha256(inhoud).hexdigest()
        data = json.dumps(vorig, indent=0, sort_keys=True).encode("utf-8")
        ftp.storbinary(f"STOR {MANIFEST}", io.BytesIO(data))
    ftp.quit()
    meld("Klaar. De site verwijst weer door naar brandweer.nl.")


def main():
    ap = argparse.ArgumentParser(description="Publiceer public/ via FTPS.")
    ap.add_argument("bron", type=Path, help="map met de gebouwde site, meestal public")
    ap.add_argument("--droog", action="store_true", help="alleen tonen, niets wijzigen")
    ap.add_argument("--opruimen", action="store_true", help="eerste keer: verwijder alles wat niet bij de site hoort")
    ap.add_argument("--terugdraaien", action="store_true", help="zet de tijdelijke doorverwijzing naar brandweer.nl terug")
    args = ap.parse_args()

    if args.terugdraaien:
        terugdraaien(args.droog)
        return

    if not (args.bron / "index.html").is_file() or not (args.bron / ".htaccess").is_file():
        sys.exit(f"FOUT: {args.bron} bevat geen gebouwde site (index.html of .htaccess ontbreekt)")

    lokaal = lokale_bestanden(args.bron)
    ftp = verbind()
    vorig = lees_manifest(ftp)

    if vorig is None and not args.opruimen:
        sys.exit("FOUT: geen manifest op de server gevonden. Dit is de eerste keer: "
                 "start de workflow handmatig met opruimen (eerst droog).")

    if args.opruimen:
        server, _ = lijst_server(ftp)
        weg = sorted(p for p in server if p not in lokaal and not is_beschermd(p))
        gewijzigd = sorted(lokaal)  # alles opnieuw, de oude inhoud is onbekend
    else:
        oud = vorig.get("bestanden", {})
        weg = sorted(p for p in oud if p not in lokaal and not is_beschermd(p))
        gewijzigd = sorted(p for p, h in lokaal.items() if oud.get(p) != h)

    # .htaccess als laatste: dan pas gaat de nieuwe configuratie (en dus de site) live.
    volgorde = [p for p in gewijzigd if p != ".htaccess"] + [p for p in gewijzigd if p == ".htaccess"]

    meld(f"{len(volgorde)} bestand(en) uploaden, {len(weg)} verwijderen"
         f"{' (droog, er verandert niets)' if args.droog else ''}.")
    for p in volgorde:
        meld(f"  + {p}")
    for p in weg:
        meld(f"  - {p}")

    if args.droog:
        ftp.quit()
        return

    mappen = set()
    for p in volgorde:
        upload(ftp, args.bron, p, mappen)
    for p in weg:
        try:
            ftp.delete(p)
        except ftplib.error_perm as e:
            meld(f"  let op: kon {p} niet verwijderen: {e}")
    # Lege mappen opruimen, diepste eerst. Mappen die nog bestanden bevatten blijven staan.
    lokale_mappen = {str(PurePosixPath(p).parent) for p in lokaal}
    kandidaten = {str(PurePosixPath(p).parent) for p in weg}
    for m in sorted(kandidaten, key=lambda x: -x.count("/")):
        while m not in ("", ".") and m not in lokale_mappen and not is_beschermd(m):
            try:
                ftp.rmd(m)
            except ftplib.error_perm:
                break
            m = str(PurePosixPath(m).parent)

    data = json.dumps({"bestanden": lokaal}, indent=0, sort_keys=True).encode("utf-8")
    ftp.storbinary(f"STOR {MANIFEST}", io.BytesIO(data))
    ftp.quit()
    meld("Klaar.")


if __name__ == "__main__":
    main()

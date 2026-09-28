"""Kiest de juiste FTP-gegevens per branch en start tools/deploy.py (voor de workflows).

- master: de echte site, met PROD_GEBRUIKER, PROD_WACHTWOORD en eventueel PROD_MAP;
- v2:     de testsite, met TEST_GEBRUIKER, TEST_WACHTWOORD en eventueel TEST_MAP.
FTP_SERVER en FTP_POORT zijn voor beide gelijk. master valt nooit terug op de testgegevens.

Bij GEBEURTENIS=workflow_dispatch worden OPRUIMEN, TERUGDRAAIEN en DROOG doorgegeven.
"""

import os
import subprocess
import sys
from pathlib import Path

DEPLOY = Path(__file__).resolve().parent / "deploy.py"


def main():
    branch = os.environ.get("BRANCH", "")
    soort = {"master": "PROD", "v2": "TEST"}.get(branch)
    if not soort:
        sys.exit(f"FOUT: publiceren kan alleen vanaf master of v2, niet '{branch}'")
    env = dict(os.environ)
    env["FTP_GEBRUIKER"] = os.environ.get(f"{soort}_GEBRUIKER", "")
    env["FTP_WACHTWOORD"] = os.environ.get(f"{soort}_WACHTWOORD", "")
    env["FTP_MAP"] = os.environ.get(f"{soort}_MAP", "")
    if not env["FTP_GEBRUIKER"] or not env["FTP_WACHTWOORD"]:
        naam = "FTP_GEBRUIKER_PROD en FTP_WACHTWOORD_PROD" if soort == "PROD" else "FTP_GEBRUIKER en FTP_WACHTWOORD"
        sys.exit(f"FOUT: {naam} ontbreken in de GitHub-omgeving")
    print(f"Publiceren vanaf {branch} naar de {'echte site' if soort == 'PROD' else 'testsite'}.")

    args = [sys.executable, str(DEPLOY), "public"]
    if os.environ.get("GEBEURTENIS") == "workflow_dispatch":
        if os.environ.get("TERUGDRAAIEN") == "TERUGDRAAIEN":
            args.append("--terugdraaien")
        elif os.environ.get("OPRUIMEN") == "OPRUIMEN":
            args.append("--opruimen")
        if os.environ.get("DROOG") == "true":
            args.append("--droog")
    sys.exit(subprocess.call(args, env=env))


if __name__ == "__main__":
    main()

"""Controleert dat er nergens een link naar een Claude-sessie staat (besluit Sven 01-10-2026).

Kijkt naar commitberichten (een reeks, bijv. origin/master..HEAD), de titel en beschrijving van
een pull request (omgevingsvariabelen PR_TITEL en PR_TEKST) en alle bestanden in de repo.
Gebruik:
    python tools/geen_sessielinks.py [REEKS]
Exitcode 1 als er iets gevonden is.
"""

import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PATROON = re.compile(r"claude\.ai/code/session|claude\.ai/chat/|session_0[0-9A-Za-z]{10,}|Claude-Session:", re.I)


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, check=True).stdout


def main():
    gevonden = []
    if len(sys.argv) > 1:
        for blok in git("log", "--format=%H%n%B%x00", sys.argv[1]).split("\0"):
            if PATROON.search(blok):
                gevonden.append(f"commit {blok.strip().splitlines()[0][:10]}")
    for naam in ("PR_TITEL", "PR_TEKST"):
        if PATROON.search(os.environ.get(naam, "")):
            gevonden.append(f"pull request ({naam})")
    for pad in git("ls-files").splitlines():
        if pad == "tools/geen_sessielinks.py":
            continue
        try:
            tekst = (ROOT / pad).read_text(encoding="utf-8")
        except (UnicodeDecodeError, FileNotFoundError, IsADirectoryError):
            continue
        if PATROON.search(tekst):
            gevonden.append(f"bestand {pad}")
    if gevonden:
        print("FOUT: link naar een Claude-sessie gevonden in:")
        for g in gevonden:
            print(f"  - {g}")
        print("Haal de link weg (commit: nieuw bericht; pull request: beschrijving aanpassen).")
        sys.exit(1)
    print("Geen sessielinks gevonden.")


if __name__ == "__main__":
    main()

# Plan: nieuwe uitrukken automatisch uit P2000

Status: plan goedgekeurd door Sven (28-09-2026). GitHub-kant gebouwd en getest met verzonnen meldingen (28-09-2026); HA nog niet aangepast.

## Besluiten Sven (28-09-2026)

- Volledig automatisch, via Home Assistant (HA).
- Alleen capcode **0107711 (Vrijwilligers)** telt als uitruk. De andere capcodes van Uitgeest (0107702 Kazernecoördinator, 0107784 Kazernehek, 0107781 Lichtkrant, 0107710 Bevelvoerder van Dienst) tellen niet.
- P2000-meldingen van Uitgeest direct publiceren, zonder goedkeuring per melding.
- Beleid VRK: P2000-meldingen mogen direct geplaatst worden. Alle andere informatie over uitrukken pas na 24 uur.
- Testfase: publiceren naar v2.brandweeruitgeest.nl. Bij livegang omzetten naar de echte site (staat in de livegang-checklist, `MIGRATIE.md` hoofdstuk 8).
- Claude mag de wijzigingen in HA doen, na akkoord op dit plan.

## Hoe het werkt

```
112radar.nl -> webhook -> Home Assistant -> GitHub (workflow starten) -> build + check -> FTPS -> site
```

HA ontvangt al P2000-meldingen van 112radar.nl (automatisering "Brandweer: 112radar Notificatie"). Bij een melding met capcode 107711 stuurt HA het tijdstip en de tekst door naar GitHub. GitHub maakt er een regel van, bouwt en controleert de site en publiceert direct.

## Wijzigingen in Home Assistant

1. **`rest_command` (Sven, in `configuration.yaml`).** Een `rest_command` kan alleen in YAML, en de sleutel hoort in `secrets.yaml`. Die raakt Claude niet aan. Claude levert de tekst:

   ```yaml
   rest_command:
     brandweeruitgeest_p2000:
       url: https://api.github.com/repos/SvenKortekaas/brandweeruitgeest.nl/actions/workflows/p2000.yml/dispatches
       method: POST
       headers:
         Authorization: !secret github_p2000_token
         Accept: application/vnd.github+json
         X-GitHub-Api-Version: "2022-11-28"
       content_type: application/json
       payload: >-
         {"ref": {{ ref | tojson }}, "inputs": {"tijdstip": {{ tijdstip | tojson }}, "tekst": {{ tekst | tojson }}, "capcodes": {{ capcodes | tojson }}}}
   ```

   In `secrets.yaml`: `github_p2000_token: "Bearer github_pat_..."`.

2. **Automatisering "Brandweer: 112radar Notificatie" (Claude, via de HA-koppeling).** Eén stap erbij, ná de bestaande `choose`:
   - als 107711 in de capcodes staat: `rest_command.brandweeruitgeest_p2000` met `ref: v2` (testfase), `tijdstip: first_message_at`, `tekst: body`, `capcodes`: de capcodes van de melding (de workflow controleert zelf nog een keer op 107711);
   - `continue_on_error: true`, zodat een storing bij GitHub nooit je pushmeldingen tegenhoudt.

   Waarom los van de `choose`: een `choose` voert alleen de eerste passende keuze uit. Staat bij een incident ook de OvD Noord (106530) in de capcodes, dan wordt de keuze voor Uitgeest nu overgeslagen. Met een losse stap komt zo'n uitruk toch op de site: worden OvD Noord en Uitgeest tegelijk gealarmeerd, dan is het gewoon een uitruk van Uitgeest (besluit Sven 28-09-2026). De bestaande meldingen en teksten blijven verder precies zoals ze zijn.

3. **Webhook-naam blijft zoals hij is** (besluit Sven 28-09-2026).

Voor elke wijziging in HA maakt Claude eerst een kopie van de huidige automatisering, zodat terugzetten altijd kan.

## Wijzigingen in GitHub

1. **`tools/import_p2000.py`** (Claude):
   - accepteert alleen het vaste formaat: tijdstip als datum en tijd, tekst die begint met een prio (`P 1`, `A1`, `B2` enz.), maximale lengte;
   - één regel per incident: dezelfde straat binnen 30 minuten is dezelfde uitruk (herhaalalarm, opschaling);
   - melding wordt de korte tekst uit `tools/meldingen.yaml`, adres wordt straat en plaats; huisnummers, objectnamen, regiocodes (`BNH-01`) en eenheidsnummers gaan eruit;
   - proefalarmen, testberichten, intrekkingen en oefeningen worden overgeslagen;
   - bron `p2000`; opnieuw draaien geeft geen dubbele regels.
2. **`.github/workflows/p2000.yml`** (Claude): start alleen via `workflow_dispatch` met de twee invoervelden. De invoer gaat als omgevingsvariabele naar het script en nooit direct in een shellcommando (tegen script-injectie). Maximaal 10 meldingen per dag. Na de import: commit naar de branch uit `ref`, `build.py`, `check.py` en `deploy.py` (alleen gewijzigde bestanden, enkele minuten).
3. **Omgeving `p2000`** (Sven): nieuwe GitHub-omgeving met dezelfde FTP-secrets als `productie`, zonder goedkeuring, alleen voor de branches `v2` (testfase) en `master`. `productie` heeft ook geen goedkeuring (besluit Sven 28-09-2026).
4. **Sleutel voor HA** (Sven): fine-grained personal access token, alleen deze repo, alleen "Actions: Read and write", verloopt na een jaar (herinnering zetten).

## Is het veilig?

- HA hoeft niet extra open: HA stuurt alleen iets naar GitHub.
- De sleutel kan alleen workflows starten, geen code wijzigen en geen secrets lezen.
- Ergste geval als de sleutel uitlekt: iemand zet een nepmelding in het vaste formaat op de site. Oplossen: sleutel intrekken en de regel weghalen. Let op: omdat `productie` geen goedkeuring heeft, kan iemand met de sleutel ook "Bouwen en publiceren" starten, ook met `OPRUIMEN` of `TERUGDRAAIEN`. Dat is te herstellen (opnieuw publiceren), maar vervelend. Voorstel: die twee acties in een aparte omgeving `beheer` met goedkeuring (Sven: voor later, 28-09-2026).

## Volgorde

1. Claude bouwt `import_p2000.py` en `p2000.yml` op `v2` en test ze met verzonnen meldingen.
2. Sven maakt de sleutel, de omgeving `p2000` en de `rest_command`.
3. Claude voegt de stap toe aan de HA-automatisering (`ref: v2`).
4. Proef: één handmatige testmelding naar de testsite, daarna de eerste echte uitruk afwachten.
5. Livegang: `ref` naar `master` en `v2` uit de omgeving `p2000` halen (checklist).

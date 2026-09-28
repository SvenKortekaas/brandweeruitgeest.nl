# VOORTGANG.md: brandweeruitgeest.nl v2

Logboek voor overdracht tussen sessies. Lees eerst `CLAUDE.md`, dan dit bestand.

## Huidige fase

Live sinds 28-09-2026: brandweeruitgeest.nl draait op de nieuwe site. Werkwijze: Claude werkt op `v2` (testsite), Sven voegt pull requests samen naar `master`.

Fase 3: migratie. Uitgevoerd 28-09-2026, wacht op controle door Sven (op v2.brandweeruitgeest.nl). Fase 2 afgerond en goedgekeurd (27-09-2026). Fase 1 is goedgekeurd (27-09-2026).

## Gedaan

- `CLAUDE.md` toegevoegd (projectbrief).
- `VOORTGANG.md` toegevoegd (dit bestand).
- Dataschema uitrukken aangepast: `prio` en `plaats` verplicht (zie beslissingen).
- Hugo-site met `git mv` naar `legacy/` verplaatst.
- Legacy-site gebouwd met Hugo 0.119.0 extended (met tijdelijke offline vervanger voor de `tweet`-shortcode, buiten de repo).
- `tools/inventaris_legacy.py` en `data/legacy-urls.csv`: 473 oude URL's met voorstel 200, 301 of vraag.
- `.gitattributes` (LF) en `.gitignore` (`public/`, `.venv/`, `__pycache__/`, `.DS_Store`) bijgewerkt.
- `MIGRATIE.md` geschreven: inventaris, URL-structuur, redirecttabel, twijfelgevallen, inhoudelijke aanpassingen, wat vervalt.
- Fase 2: `requirements.txt`, `build.py`, `templates/`, `static/css/site.css`, `data/site.yaml`, `.htaccess`-generatie, `tools/check.py`.
- Voorbeeldinhoud: home, disclaimer, P2000, privacy (nieuw), voertuigen met 12-2030, één nieuwsartikel (kerstboom, YouTube als link), uitrukken 2022 (alle 52 regels, volgens de besluiten omgezet). Over ons en Posten Kennemerland zijn nog lege voorbeeldpagina's.
- README en CONTRIBUTING herschreven voor de Python-werkwijze, open bijdrage-gedachte behouden.
- `python build.py` en `python tools/check.py` slagen in een schone venv. Geen horizontale scroll op 390 px breed.

## Open

- Google Maps API-key uit `legacy/config.toml`: getest door Sven op 28-09-2026, Google antwoordt "The provided API key is invalid". De key is dood en onschadelijk; afgehandeld.
- **Onthouden: actuele feiten.** Aantal vrijwilligers is bekend (19, 28-09-2026) en Over ons is herschreven. Nog open: eisen voor nieuwe leden, copyrighttekst, foto's van 12-2001 en 12-1536 (nog niet, 28-09-2026). Gegevens van 12-2060 en 12-2011 kloppen (28-09-2026).
- 12-1536: pagina compleet met gegevens die Sven aanleverde uit Brandbase (27-09-2026): Mercedes-Benz Atego, opbouw en pomp Ziegler, 2018, 35-BLR-2, 272 pk, eigenaar Logistiek en Vakbekwaam Regio (12-1X). Nog nodig: eigen foto's of toestemming voor foto's van anderen.
- Voertuigpagina's 12-2001, 12-2002, 12-2060 en 12-2011 overgezet (27-09-2026, op verzoek van Sven vóór fase 3). Tekst letterlijk uit de oude site, met één correctie: de kop op de MSA-pagina (12-2060) was "Dienstauto" en is "Motorspuitaanhanger" geworden. Gegevens (bouwjaar, opmerkingen e.d.) zijn van de oude site en mogelijk verouderd.
- Idee voor de wervingstekst, nog uit te werken met Sven: "help mee om dorpelijk toegankelijk te houden" (letterlijk genoteerd). Sven werkt dit later uit; tot die tijd een voorlopige kop.
- Uitrukken 2023 t/m 27-09-2026 aangevuld (bron `eigen`). 20 uitrukken tussen 13-09-2022 en 11-01-2023 aangevuld uit P2000-meldingen die Sven plakte (28-09-2026, van p2000.page), bron `p2000`: korte meldingen, alleen straat en plaats (objectnamen weggelaten), intrekkingen en het contactbericht van 21-09-2022 niet meegenomen.
- Open vragen uit `CLAUDE.md`.
- Later (Sven, 28-09-2026): `OPRUIMEN` en `TERUGDRAAIEN` in een aparte GitHub-omgeving `beheer` met goedkeuring, zodat de HA-sleutel die niet zonder Sven kan starten. Zie `PLAN-P2000.md`, "Is het veilig?".

- Publiceren (voorbereid, 27-09-2026): `tools/deploy.py` (FTPS met certificaatcontrole, manifest, eerste keer opruimen) en `.github/workflows/build.yml`. Lokaal getest tegen een test-FTPS-server: weigert zonder manifest, droog opruimen, echt opruimen met beschermde paden, alleen wijzigingen uploaden, verwijderen, geen geldig certificaat. Nog niet tegen de echte server getest. Eerste run van de workflow op `v2` geslaagd (bouwen en controleren; publiceren terecht overgeslagen). Let op: pushes vanuit een Claude-sessie gebruiken het account van Sven en tellen dus als "zijn" push; Claude pusht daarom nooit naar `master`.
- **Testfase (28-09-2026):** de FTP-gegevens wijzen naar het subdomein v2.brandweeruitgeest.nl. Branch `v2` mag tijdens de testfase publiceren (workflow aangepast); Sven moet in de omgeving `productie` bij Deployment branches ook `v2` toestaan. Op host `v2.` stuurt de `.htaccess` `X-Robots-Tag: noindex`. Livegang = Sven wijst het pad van het hoofddomein naar dezelfde map; FTP-gegevens blijven gelijk. Daarna `v2` weer uit de workflow halen.
- **Sven:** GitHub-omgeving `productie` met secrets instellen (geen required reviewer, besluit 28-09-2026), AppVeyor uitzetten, oud FTP-wachtwoord wijzigen, backup maken. Stappen in `MIGRATIE.md` hoofdstuk 7.
- **Onthouden voor terugdraaien:** huidige `.htaccess` op de server (27-09-2026) is een tijdelijke 302 naar https://www.brandweer.nl/kazerne/uitgeest/. Staat in `tools/htaccess-terugdraaien` en `MIGRATIE.md` (Terugdraaien). Workflow-optie `TERUGDRAAIEN` zet hem terug.
- Fase 3 uitgevoerd (28-09-2026), zie `MIGRATIE.md` hoofdstuk 5b. `MIGRATIE_KLAAR = True`: alle controles slagen strikt. CI heeft een cache voor omgezette afbeeldingen. HTML-controle is een nestingcontrole, geen volledige W3C-validatie.
- AVG: bij 29 oude uitrukken met een medische melding is het huisnummer weggehaald (`tools/migrate_hugo.py`, controle in `check.py`). Hectometers als "Provincialeweg 53.7" blijven staan.
- Privacyverklaring: verantwoordelijke brandweer Uitgeest, Molenwerf 25; hosting Cloud86.
- Nieuwsfoto's hebben een algemene alt-tekst; later per foto beschrijven kan.

## Beslissingen van Sven

- 27-09-2026: in het dataschema van `data/uitrukken/JJJJ.csv` worden `prio` (1, 2 of 3) en `plaats` verplicht. `plaats` wordt altijd ingevuld, ook bij Uitgeest; "leeg betekent Uitgeest" vervalt. Historische regels zonder prio: niet raden, per jaar tellen in `MIGRATIE.md` en Sven vragen. Historische regels zonder plaats krijgen Uitgeest, behalve regels met wegnummer of hectometrering (A9, N203): niet invullen, vragen. `check.py` faalt op nieuwe regels zonder geldige prio of plaats. Vastgelegd in `CLAUDE.md`.

- 27-09-2026, antwoorden op de vragen van fase 1:
  1. Historische uitrukken zonder prio (568 regels): niet vullen, `prio` blijft leeg.
  2. Uitrukken met weg of hectometrering zonder plaats (235 regels): geen plaats. Wat we niet weten vullen we niet in.
  3. Adres is alleen een plaatsnaam (41 regels): die naam wordt `plaats`, `adres` leeg.
  4. Huisnummers in historische uitrukken (ca. 198 regels, 2013 t/m 2016): blijven staan vanwege historische waarde.
  5. Bedrijfsnamen in historische uitrukken blijven staan.
  6. Laat van de oude site weg wat niet meer nodig is. Er komen voorlopig geen nieuwsberichten, de site wordt vooral een informatiesite. Huidige voertuigen: 12-2030, 12-2001, 12-2002, 12-2060, 12-2011 en 12-1536 (van Vakbekwaamheid, staat op de kazerne in Uitgeest). 12-2031 en 12-2061 zijn er niet meer.
  7. Actuele feiten: Sven komt er later uitgebreid op terug.
  8. Twitter vervalt. Social media: alleen Facebook en Instagram.
  9. `MIGRATIE.md` nog niet gelezen; doorlopen via een vragenlijst.
  Verwerkt in `CLAUDE.md` (dataschema, privacyfilter, inhoudelijke aanpassingen).
- 27-09-2026, vragenlijst `MIGRATIE.md` ronde 1 en 2:
  1. De 31 oude nieuwsartikelen blijven als archief, URL's ongewijzigd.
  2. Geen pagina voor voormalige voertuigen. 12-2031 en 12-2061 via 301 naar `/voertuigen/`. Foto's van 12-2003 gaan niet mee.
  3. Thema-CSS/JS, thema-afbeeldingen en ongebruikte foto's krijgen `410 Gone`.
  4. Posten Kennemerland wordt een lijst met links naar OpenStreetMap.
  5. Instagram: @brandweeruitgeest.
  6. Werving op de homepage. ikwilbijbrandweeruitgeest.nl bestaat niet en komt er voorlopig niet (idee in de ijskast). Werving linkt naar https://www.werkenbijdevrk.nl/vacatures/brandweervrijwilliger/8fa2ec35-00b3-4844-be28-4cba4928301b
  7. Kapotte tekens in 5 uitrukregels herstellen (alleen codering).
- 27-09-2026, vragenlijst ronde 3:
  1. Homepage: werving, laatste uitrukken, adres en contact. Veiligheidstips en voertuigtegels niet op de homepage.
  2. Losse pagina's: Over ons, Betekenis P2000, Disclaimer en Privacy (nieuw). Posten Kennemerland blijft (ronde 1).
  3. Rest van `MIGRATIE.md` doorlopen via verdere vragenrondes.
- 27-09-2026, vragenlijst ronde 4:
  1. Akkoord op `/uitrukken/` en `/uitrukken/JJJJ/`, oude `/JJJJ/` via 301.
  2. Tags en categorieën helemaal weg, ook bij de artikelen.
  3. Alleen YouTube wordt een link; tweets en Facebook-post vervallen zonder link.
  4. Uitrukken per jaar opnieuw doornummeren (1 t/m N op datumvolgorde).
- 27-09-2026, vragenlijst ronde 5:
  1. Foto's: nette bestandsnamen, WebP/AVIF, oude adressen via 301. Akkoord.
  2. Zoekfunctie vervalt. Akkoord.
  3. Huidige favicons houden; 9 blijven op hetzelfde adres, 12 oude formaten via 301.
  4. Akkoord op `MIGRATIE.md` als geheel, start fase 2.
- 27-09-2026, akkoord fase 2:
  1. Uiterlijk akkoord (witte kop, rode accenten, rood wervingsblok, donkere voet).
  2. Nieuwsarchief alleen in de voet. Akkoord.
  3. Bronfoto's in `afbeeldingen/`. Akkoord.
  4. Disclaimer en privacyverklaring in fase 3 herschrijven "zoals het hoort volgens de Europese regels" (AVG/GDPR); contactformulier eruit.
  5. Fase 3 nog niet starten.
- 27-09-2026: uploadplan. Sven zet een nieuwe FTP-server, poort, gebruikersnaam en wachtwoord in GitHub Secrets. Bij de eerste keer moet al het oude weg wat niet nodig is; daarna werkt elke nieuwe versie de site bij. Alleen een push van Sven mag de website bijwerken.
- 27-09-2026, uploadplan vervolg:
  1. De nieuwe FTP-server ondersteunt echt FTPS.
  2. Elke publicatie met één klik goedkeuren (required reviewer in de omgeving `productie`). Vervallen op 28-09-2026: geen goedkeuring.
  3. Alles op de server mag weg bij de eerste livegang. Alleen `.well-known` blijft (nodig voor het HTTPS-certificaat).
  4. Huidige `.htaccess` op de server bewaren voor terugdraaien (zie Open).
- 27-09-2026: alle huidige voertuigen moeten op de site (12-2030, 12-2001, 12-2002, 12-2060, 12-2011). Gedaan, ook 12-1536 (voorlopig zonder foto en details).
- 27-09-2026, nieuwe uitrukken (vanaf 2023):
  1. Huisnummers weghalen en melden.
  2. Geen soorten meldingen verbergen (ook reanimatie en gezondheid tonen).
  3. Korte meldingen zoals op de oude site, via een vertaaltabel in `tools/meldingen.yaml` die Sven kan aanpassen.
- 28-09-2026: P2000-meldingen van p2000.page gebruiken om de ontbrekende uitrukken eind 2022 aan te vullen.
- 28-09-2026:
  1. "PKP N200 Re - Zeeweg 22" (2023): 22 is een hectometerpaal. Blijft staan.
  2. Oefeningen apart tellen (niet als uitruk). Gedaan: jaarpagina en overzicht tonen ze los.
  3. Hulp gevraagd bij het nalopen van `tools/meldingen.yaml`.
  4. Fase 3 mag starten.
  5. Testomgeving: alles eerst op v2.brandweeruitgeest.nl; FTP-gegevens wijzen daar al naar. Bij tevredenheid gaat het hoofddomein naar dezelfde map (alleen het pad verandert).
  6. Google Maps API-key: Sven weet niet meer bij welk Google-account; geldigheid onbekend.

- 28-09-2026, vervolg:
  1. Vertaaltabel meldingen blijft zoals hij is ("Gezondheid", "Stankoverlast", "Ongeval materieel", "Bijstand brandweer", "Afstemverzoek", "Herbezetting kazerne").
  2. `v2` toegevoegd aan de omgeving `productie` (Sven).
  3. Sven kan de workflow niet zelf handmatig starten; Claude start de droge opruim-run.
  4. AVG: huisnummer weghalen bij de 29 oude uitrukken met een medische melding. De overige oude huisnummers blijven.
  5. Verantwoordelijke voor de site: brandweer Uitgeest, Molenwerf 25. Hosting: Cloud86.

- 28-09-2026: droge opruim-run op `v2` door Claude gestart (Sven kon niet zelf starten). FTPS-verbinding met de server werkt; ca. 900 bestanden uploaden, 0 verwijderen (testmap leeg). De run liep zonder goedkeuring: er staat nog geen required reviewer op de omgeving `productie`.

- 28-09-2026: echte opruim-run naar v2.brandweeruitgeest.nl gedaan door Claude, met expliciet akkoord van Sven (run 20). Ca. 900 bestanden geüpload in ruim 16 minuten, 0 verwijderd. De volgende push (run 21) vond 0 wijzigingen: het manifest werkt. Nog steeds geen required reviewer op `productie`, dus elke push naar `v2` publiceert direct naar de testsite.
  - Verbeterpunt: een volledige upload duurt lang (elk bestand een eigen versleutelde verbinding). Normale updates zijn klein en snel.

- 28-09-2026, aanpassingen na bekijken testsite:
  1. Oefeningen zijn geen uitrukken: de 6 oefeningen in de nieuwe regels zijn weg. De oude "Brand oefening" uit 2012 is later ook weggehaald (zie hieronder).
  2. 12-2030: foto's van de binnenkant weg (oude adressen geven 410).
  3. 12-2001: foto's waren van het oude voertuig en zijn weg (410). Nieuwe gegevens: dienstbus DB-9, Mercedes-Benz Vito, opbouw Visser Leeuwarden, SG-508-V, 2018, 136 pk. Gebruikt voor cursussen en afspraken.
  4. 12-2002: kleine verzorging doen we niet meer. Het is een DA-T (dienstauto terrein): uitrukken, o.a. reanimaties, met de MSA naar natuurbranden en naar de boot 12-2011.
  5. Over ons herschreven: kort, huidige voertuigen, 19 vrijwilligers. `tools/migrate_hugo.py` overschrijft Over ons niet meer.
  6. Volgorde voertuigen: 12-2030, 12-2001, 12-2002, 12-2060, 12-2011, 12-1536.

- 28-09-2026, vervolg:
  1. "Brand oefening" van 11-12-2012 weggehaald: oefeningen zijn geen uitrukken. 2012 heeft nu 111 regels. `migrate_hugo.py` slaat de regel over (`LEGACY_WEG`) en `check.py` verwacht voor 2012 de oude telling min 1.
  2. Foto's van 12-2001 en 12-1536: nog niet.
  3. Gegevens van 12-2060 en 12-2011 kloppen.
  4. Sven vroeg om een plan om nieuwe uitrukken automatisch uit P2000 op de site te zetten: `PLAN-P2000.md` (idee, nog niet gebouwd, vragen staan onderaan).

- 28-09-2026, P2000-automatisering (antwoorden Sven):
  1. Bron: liefst volledig automatisch, via een webhook uit zijn Home Assistant (HA ontvangt nu al P2000 van 112radar.nl).
  2. Capcodes brandweer Uitgeest: 0107711 Vrijwilligers, 0107702 Kazernecoördinator, 0107784 Kazernehek, 0107781 Lichtkrant, 0107710 Bevelvoerder van Dienst.
  3. P2000-meldingen van Uitgeest direct publiceren.
  4. Beleid VRK: P2000-meldingen mogen direct geplaatst worden, alle andere informatie over uitrukken pas na 24 uur.
  - Ontwerp en veiligheidsafweging staan in `PLAN-P2000.md`. Nog niet gebouwd, wacht op akkoord.
  - Advies aan Sven: de bestaande HA-webhook `112radar_p2000` is vanaf internet bereikbaar en makkelijk te raden; een willekeurige naam geven.

- 28-09-2026, P2000 vervolg:
  1. Alleen capcode 0107711 (Vrijwilligers) telt als uitruk.
  2. Claude mag de wijzigingen in Home Assistant doen, na akkoord op het plan (`PLAN-P2000.md`, hoofdstuk "Wijzigingen in Home Assistant").
  3. Testfase: P2000 publiceert naar v2.brandweeruitgeest.nl, bij livegang omzetten naar de echte site. Opgenomen in de livegang-checklist (`MIGRATIE.md` hoofdstuk 8).
  4. De herkomst van regels met `bron=eigen` wordt nergens beschreven en er komt geen andere import bij dan P2000. Bijbehorende scripts en teksten verwijderd. Op verzoek van Sven is de historie van `v2` opnieuw opgebouwd als één commit bovenop `master` (force push, 28-09-2026). Sven heeft de oude workflow-runs in GitHub verwijderd.
  5. Plan Home Assistant goedgekeurd, met twee eisen: worden OvD Noord en Uitgeest tegelijk gealarmeerd, dan komt het gewoon als uitruk van Uitgeest op de site; de webhooknaam blijft zoals hij is.
  6. P2000-import en workflow bouwen: "denk het wel", dus eerst bouwen en testen op `v2`, pas daarna HA aanpassen.

- 28-09-2026, P2000-import gebouwd (nog niet actief):
  - `tools/import_p2000.py` en `tools/p2000.yaml`: zet één melding om in een uitruk (bron `p2000`). Alleen capcode 0107711, prio 1 t/m 3, melding via de tabel in `p2000.yaml`, alleen straat of weg met hectometer plus plaats. Overslaan bij intrekking, proefalarm, test en oefening; zelfde straat binnen 30 minuten is dezelfde uitruk; maximaal 10 per dag. Bij twijfel (onbekende melding, plaats of straat) wordt niets geschreven en faalt de run met de P2000-tekst erbij.
  - `.github/workflows/p2000.yml`: start via `workflow_dispatch` (tijdstip, tekst, capcodes), commit naar de branch en publiceert via de omgeving `p2000`. Getest met verzonnen meldingen, nog niet op GitHub gedraaid.
- 28-09-2026: Sven vraagt informatie over de 112NL-app op de site. Nieuwe pagina `/112nl-app/` (tekst van Sven plus de waarschuwing uit de flyer: misbruik van 112 is strafbaar, app niet testen), in de voet van de site en kort genoemd op de homepage.

- 28-09-2026, koppeling Home Assistant:
  - Sven: omgeving `p2000`, token, `rest_command.brandweeruitgeest_p2000` in HA, "Block force pushes" op `v2` weer aan. Of `github-actions[bot]` naar `v2` mag pushen is nog niet zeker.
  - Claude: in "Brandweer: 112radar Notificatie" een losse stap na de `choose` (alias "Uitruk naar brandweeruitgeest.nl"): bij capcode 107711 `rest_command.brandweeruitgeest_p2000` met `ref: v2`, `continue_on_error`. Terugzetten = die laatste stap weghalen.
  - Eerste proef gaf 404: GitHub kent een workflow pas als hij een keer gedraaid heeft. `p2000.yml` draait nu ook bij een push op de P2000-bestanden, alleen een zelftest.
  - Geen required reviewer op `productie` (besluit Sven 28-09-2026): elke push van Sven naar `v2` of `master` publiceert direct.
  - Aparte omgeving `beheer` met goedkeuring voor `OPRUIMEN` en `TERUGDRAAIEN`: nu niet, voor later (Sven, 28-09-2026). Staat bij Open.
  - Proef via HA (28-09-2026): proefalarm kwam aan in GitHub (run 2) en is terecht overgeslagen. De keten HA, token en workflow werkt.
  - Nieuwe pagina 112NL-app alleen in de voet, niet in het hoofdmenu (Sven).

- 28-09-2026, fase 4 weergave: filteren op maand en soort op de jaarpagina's, zonder JS.
  - Maand: sprongankers naar elke maand (bestond al).
  - Soort: zeven groepen (Brand, Automatische melding, Ongeval en hulpverlening, Ambulance en reanimatie, Water, Dieren, Overig), met aantallen. Een link naar `#soort-x` verbergt via CSS `:target` alle andere regels en lege maanden en toont "Je ziet alleen ...". De indeling staat in `SOORTGROEPEN` in `build.py` (op trefwoorden, want de oude meldingen hebben veel schrijfwijzen); de slugs staan ook in `static/css/site.css`.
  - De tabel met totalen per exacte melding blijft. Getest in Chromium op 1200 en 390 px breed.

- 28-09-2026, fase 5 livegang gestart (Sven: filter goed, door naar livegang). Sven gaf de sessie onbeperkt internet om te testen.
  - `tools/controleer_live.py` en workflow "Site controleren": testsite heeft alle 473 oude URL's goed, 69 pagina's 200, headers en caching goed. http naar https is vanuit de sessie niet te testen (proxy), wel in GitHub Actions.
  - Lighthouse op de testsite: performance 98 tot 100, toegankelijkheid 100, best practices 96 (logo 187x56 is te klein voor scherpe schermen), SEO 69 alleen door `noindex` op v2.
  - Hoofddomein en v2 staan op dezelfde server; livegang = hoofddomein naar de map van v2. Stappenplan in `MIGRATIE.md` hoofdstuk 7 ("Livegang: stappenplan").

- 28-09-2026, livegang (antwoorden Sven):
  1. Stap 1 gedaan: AppVeyor uit, wachtwoord gewijzigd, backup gemaakt.
  2. Twee FTP-accounts, zelfde server en poort: `FTP_GEBRUIKER`/`FTP_WACHTWOORD` voor de testsite (v2), `FTP_GEBRUIKER_PROD`/`FTP_WACHTWOORD_PROD` voor de echte site. `v2` blijft dus de testsite.
  3. Pull request `v2` naar `master`: akkoord. Werkwijze daarna: Claude werkt op `v2` en opent per afgeronde stap een pull request, Sven voegt samen. P2000-uitrukken gaan direct naar `master`.
  4. Groter logo (SVG of 3x zo groot): onthouden, later.
  5. Na de push naar `master`: geen verwijzingen naar het testadres in de code van de echte site, nu en later. Verse start: de map van de echte site leegmaken, alleen `.cagefs`, `.cl.selector` en `.well-known` houden (zo leeg mogelijk). Juiste `.htaccess` op beide sites.
  6. Waarschuwing in GitHub Actions over `ubuntu-latest` naar Ubuntu 26 (19-10-2026): runners vastgezet op `ubuntu-24.04`.
  - Uitgevoerd: `BOUW_OMGEVING` (live of test) in `build.py`: alleen de testbouw krijgt `noindex` en `Disallow: /`, de livebouw bevat geen testadres meer. `tools/publiceer.py` kiest de FTP-gegevens per branch (master valt nooit terug op de testgegevens). `deploy.py` beschermt `.cagefs` en `.cl.selector`.

- 28-09-2026, livegang uitgevoerd:
  - Sven voegde pull request #56 samen (squash) en zette de `_PROD`-secrets ook in de omgeving `p2000`. De eerste publicatie vanaf `master` stopte bewust (geen manifest), de `_PROD`-gegevens werkten.
  - `master` samengevoegd in `v2` (inhoud gelijk), zodat volgende pull requests alleen nieuwe wijzigingen tonen.
  - Droog opruimen op de echte site: 889 bestanden uploaden, 417 verwijderen, allemaal van de oude Hugo-site (img, tags, categories, css, js, oude jaar- en voertuigpagina's, oude iconen). Geen mail-, log- of hostingmappen: de FTP-map van het PROD-account is de webmap. Daarna echt opgeruimd (Claude, op verzoek van Sven).

- 28-09-2026, livegang afgerond: echte opruim-run geslaagd, brandweeruitgeest.nl live. Controle op het hoofddomein: 473 oude URL's, 69 pagina's, headers, www en http, 0 fouten (hier en in GitHub Actions). Geen testadres in de site. Home Assistant stuurt P2000 nu naar `master`; proefalarm via `master` terecht overgeslagen.

- 28-09-2026, opruimen repo (akkoord Sven: "ja, ja en ja"):
  1. Pull request #57 (documentatie): Sven voegt samen.
  2. `legacy/` verwijderd, samen met de eenmalige scripts `tools/migrate_hugo.py` en `tools/inventaris_legacy.py` die alleen `legacy/` lazen. `data/legacy-urls.csv` en de tellingen in `check.py` blijven. De bestanden staan nog in de git-historie (ook de ongeldige Google-key in `legacy/config.toml`).
  3. De drie Dependabot-pull requests (#53, #54, #55) voor het Hugo-thema gesloten, met uitleg.

## Volgende stap

1. Sven: pull request "Oude Hugo-site verwijderd" samenvoegen.
2. Eerste echte P2000-uitruk na livegang controleren op de site.
3. Later: groter logo (Sven).

# CLAUDE.md: brandweeruitgeest.nl v2

Projectbrief voor Claude Code. Lees dit volledig voordat je iets wijzigt.

## Doel

Herbouw van brandweeruitgeest.nl in deze repository (`SvenKortekaas/brandweeruitgeest.nl`) als snelle, veilige, statische website zonder trackers. De huidige Hugo-site (hugo-universal-theme, Hugo 0.119) wordt vervangen. Alle bruikbare inhoud komt mee: pagina's, nieuws, voertuigen en het volledige uitrukkenarchief 2008 t/m 2022. Uitrukken vanaf 2023 zijn aangevuld; nieuwe uitrukken komen automatisch uit P2000.

Taal van de site en van alle teksten, commits en commentaar: Nederlands.
Schrijfregel: gebruik geen em dashes (—) in teksten, code-commentaar of commits.

## Branch en werkruimte

- Alle werk gebeurt op branch `v2`. Heeft de sessie zelf een andere branch aangemaakt (bijv. `claude/...`), schakel dan over: `git fetch origin && (git checkout v2 || git checkout -b v2 origin/master)`.
- Na elke afgeronde stap: commit en `git push origin v2`.
- Nooit committen of pushen naar `master` en nooit zelf mergen. Werkwijze na livegang (besluit Sven 28-09-2026): Claude werkt op `v2` (de testsite v2.brandweeruitgeest.nl); is een stap af, dan opent Claude een pull request `v2` naar `master` en voegt Sven samen. Alleen P2000-uitrukken gaan automatisch rechtstreeks naar `master`.
- AppVeyor is uitgeschakeld (Sven, 28-09-2026). `master` wordt gebouwd en gepubliceerd door GitHub Actions.
- Eerste commit van fase 1 (na de commit met `CLAUDE.md` en `VOORTGANG.md`): verplaats de volledige Hugo-site met `git mv` naar `legacy/` (zodat de historie behouden blijft):
  `config.toml content/ data/ layouts/ static/ themes/ archetypes/ .forestry/ appveyor.yml deploy.sh minify.sh file_sizes.sh`
- Blijven in de root: `LICENSE.md` (GPL-3.0, niet wijzigen), `CODE_OF_CONDUCT.md`, `CONTRIBUTING.md`, `README.md`, `.github/`, `.gitattributes`, `.gitignore`.
- `legacy/` (de oude Hugo-site) en de eenmalige migratiescripts `tools/migrate_hugo.py` en `tools/inventaris_legacy.py` zijn na de livegang verwijderd (akkoord Sven 28-09-2026). Ze staan nog in de git-historie.
- De 3 Dependabot-pull requests voor het Hugo-thema zijn gesloten (akkoord Sven 28-09-2026).

## Overdracht tussen sessies en apparaten

Sven werkt afwisselend vanuit Claude Code op de iPhone (cloudsessie) en later vanaf een pc. Elke sessie begint zonder geheugen van de vorige. Daarom:

- De repo is de enige bron van waarheid. Niets mag alleen in een sessie bestaan.
- `VOORTGANG.md` in de root houdt bij: huidige fase, wat af is, wat open staat, beslissingen van Sven (met datum) en de eerstvolgende stap. Bij de start van een sessie eerst `CLAUDE.md` en `VOORTGANG.md` lezen. De laatste commit van elke sessie werkt `VOORTGANG.md` bij.
- Beslissingen die Sven in de chat geeft direct vastleggen in `VOORTGANG.md`, niet alleen uitvoeren.
- Alles moet lokaal werken op Windows, macOS en Linux met alleen Python:
  `python -m venv .venv`, `pip install -r requirements.txt`, `python build.py`, `python -m http.server -d public 8000`.
  Geen OS-specifieke paden of shellscripts als enige route. Regeleinden LF (vastleggen in `.gitattributes`).
- `.gitignore` bevat minimaal `public/`, `.venv/`, `__pycache__/`, `.DS_Store`.
- Geen secrets, tokens of lokale paden in de repo.
- Sven leest mee op een telefoon: sluit elke fase af met een korte samenvatting (wat gedaan, wat hij moet beslissen, genummerde vragen), zonder lange codeblokken.

## Uitgangspunten (niet onderhandelbaar)

1. **Statisch.** Output is platte HTML/CSS in `public/`. Geen server-side code, geen database, geen CMS.
2. **Geen trackers, geen externe verzoeken.** Geen analytics, geen externe fonts, geen CDN's (dus ook geen jQuery, Bootstrap, Font Awesome, Leaflet van unpkg), geen embeds (Facebook, YouTube, Google Maps), geen Formspree. Alles lokaal. Een externe link is prima, een externe resource niet.
3. **Minimaal JavaScript.** De site werkt volledig zonder JS. JS alleen als progressieve verbetering en altijd als los bestand, nooit inline.
4. **Bestaande URL's blijven werken.** Elke URL van de huidige site geeft een pagina of een 301, nooit een 404. Uitzondering (besluit 27-09-2026): oude thema-bestanden en ongebruikte afbeeldingen geven een 410, zie `data/legacy-urls.csv`.
5. **Privacy bij uitrukken.** Zie sectie Uitrukken. Bij twijfel: niet publiceren.
6. **Toegankelijk.** Richtlijn WCAG 2.2 AA.

## Stack

- Python 3.11+ met alleen: `jinja2`, `markdown`, `pyyaml`, `Pillow`. Vastgelegd in `requirements.txt`. Niets anders zonder overleg.
- `build.py` genereert de volledige site van `content/` + `data/` + `templates/` + `static/` naar `public/`.
- CSS: één handgeschreven stylesheet, huisstijlkleur rood, geen framework.
- Fonts: systeemfontstack.
- Iconen: inline SVG in templates, geen icon font.
- Hosting: bestaande Apache-hosting, configuratie via `.htaccess`.

## Doelstructuur (na fase 2)

```
/
├── CLAUDE.md
├── VOORTGANG.md
├── README.md                # bijgewerkt: hoe bouwen, hoe bijdragen
├── requirements.txt
├── build.py
├── tools/
│   ├── import_p2000.py      # P2000-melding -> data/uitrukken/*.csv
│   ├── p2000.yaml           # capcode, meldingen, inzetgrootte voor de P2000-import
│   ├── plaatsen.yaml        # woonplaatsen in VR Kennemerland, NHN, Zaanstreek-Waterland, Amsterdam-Amstelland
│   ├── sociaal.py           # nieuwe P2000-uitruk naar Facebook en Instagram
│   ├── meldingen.yaml       # normalisatie en publicatieregels per meldingssoort
│   └── check.py
├── content/
│   ├── index.md
│   ├── over-ons.md
│   ├── voertuigen.md
│   ├── voertuigen/          # 12-2001 ... 12-2061
│   ├── nieuws/
│   ├── posten-kennemerland.md
│   ├── betekenis-p2000-meldingen.md
│   ├── disclaimer.md
│   └── privacy.md           # nieuw: geen cookies, geen tracking
├── data/
│   ├── uitrukken/           # één CSV per jaar: 2008.csv ... 2026.csv
│   ├── carousel.yaml        # veiligheidstips (bel 112, vluchtplan, rook)
│   └── redirects.csv        # oude URL -> nieuwe URL
├── templates/
├── static/
├── .github/workflows/       # nieuwe build en deploy (fase 5)
└── public/                  # build-output, in .gitignore
```

## Wat er in legacy/ zat (inventaris vooraf, map verwijderd na livegang)

- `config.toml`: menu, adres (Molenwerf 25, 1911 DB Uitgeest), e-mail info@brandweeruitgeest.nl, social links (Facebook, Twitter, GitHub), permalinks `nieuws = /nieuws/:year/:month/:day/:filename/`.
- `content/2008.md` t/m `content/2022.md`: uitrukken als HTML-tabel in Markdown, ca. 1550 regels in totaal. Kolommen: Nr., Datum (`1-jan` of `01-jan`, jaar volgt uit de bestandsnaam), Melding, Adres. Oudere jaren hebben één `<td>` per regel, nieuwere één `<tr>` per regel. Meldingen vanaf ca. 2015 beginnen met `Prio 1/2/3`, oudere niet. Adres is straat, soms `straat, plaats` of een hectometrering (`A9 L 58,1c`).
- `content/12-20xx.md` + `voertuigen.md`: voertuigpagina's met foto's en voertuiggegevens.
- `content/nieuws/`: 31 artikelen (2016 t/m 2020), TOML front matter (`+++`), met tags, categories, banner, images.
- Shortcodes: `load-photoswipe`, `gallery`, `figure` (ca. 126 foto's), `facebook-post` (1x), `incident-location` (Leaflet-kaart via unpkg, 2x).
- `data/`: carousel (3 veiligheidstips), clients (voertuigen op home), features en testimonials (uitgeschakeld, niet migreren).
- `static/`: ca. 29 MB, waarvan afbeeldingen in `img/nieuws/`, `img/voertuigen/`, `img/carousel/`, plus favicons.

## Fase 1: analyse en URL-inventaris

1. Bouw de legacy-site één keer lokaal met Hugo 0.119 (`hugo -s legacy -d /tmp/legacy-public`) en maak uit het resultaat een volledige lijst van alle gegenereerde URL's, inclusief `/nieuws/page/N/`, `/tags/...`, `/categories/...`, RSS-feeds (`index.xml`) en afbeeldingen. Lukt de build niet, dan de lijst afleiden uit `content/`, permalinks en `static/`.
2. Schrijf `MIGRATIE.md` met: inventaris, voorstel nieuwe URL-structuur, redirecttabel, lijst van twijfelgevallen (zie hieronder), en een lijst van alles wat vervalt.
3. Stop en vraag akkoord.

### URL-beleid

- Nieuws: pad blijft gelijk (`/nieuws/JJJJ/MM/DD/slug/`), geen redirect nodig.
- Voertuigen: nieuw `/voertuigen/12-2030/`, oude `/12-2030/` via 301.
- Uitrukken: nieuw `/uitrukken/JJJJ/`, oude `/JJJJ/` via 301. Overzicht op `/uitrukken/`.
- Overige pagina's: slug blijft gelijk.
- Tag- en categoriepagina's vervallen: 301 naar `/nieuws/`.
- RSS: `/nieuws/index.xml` blijft bestaan (Atom/RSS genereren in `build.py`), `/index.xml` via 301.

## Fase 2: skelet

`build.py`, templates (basis, pagina, nieuwsoverzicht, nieuwsartikel, voertuig, uitrukken-jaar, uitrukken-overzicht), stylesheet, `.htaccess`-generatie, `check.py`. Met een handvol voorbeeldpagina's. Stop en vraag akkoord op uiterlijk en structuur.

## Fase 3: migratie

`tools/migrate_hugo.py`:

- Front matter van TOML naar YAML, velden: `title`, `date`, `description`, `banner`, `author`. Tags en categorieën vervallen helemaal (besluit 27-09-2026).
- `gallery`/`figure`/`load-photoswipe` wordt een eenvoudige fotogrid: `<figure>` met thumbnail die linkt naar de grote versie. Geen lightbox-JS.
- `youtube` wordt een gewone link naar de video. `facebook-post` en `tweet` vervallen zonder link, die posts bestaan mogelijk niet meer (besluit 27-09-2026).
- `incident-location` wordt een link naar OpenStreetMap op die coördinaten. Geen kaarttegels van externe servers.
- Fotocredits (bijv. 112-Uitgeest.nl) altijd behouden.
- Afbeeldingen: EXIF (incl. GPS) strippen, omzetten naar WebP en AVIF in 480/960/1600 px, origineel niet meer publiceren tenzij kleiner. Bestandsnamen normaliseren (geen spaties, haakjes, hoofdletterextensies), met 301 van de oude paden als die extern gelinkt kunnen zijn.
- Uitrukken 2008 t/m 2022 naar `data/uitrukken/JJJJ.csv` (schema hieronder). Controleer per jaar dat het aantal regels exact gelijk is aan het aantal `<tr>` in de body van de oude tabel.

### Inhoudelijke aanpassingen (markeren in MIGRATIE.md, niet stil doen)

- "Helden gezocht" en de wervingstekst op `over-ons` verwijzen naar de vacature brandweervrijwilliger bij de VRK (https://www.werkenbijdevrk.nl/vacatures/brandweervrijwilliger/8fa2ec35-00b3-4844-be28-4cba4928301b) in plaats van een contactformulier. ikwilbijbrandweeruitgeest.nl bestaat niet en komt er voorlopig niet (besluit 27-09-2026).
- Contactformulier (Formspree) vervalt, wordt `mailto:info@brandweeruitgeest.nl`. Let op: in `config.toml` staat het adres onvolledig als `info@brandweeruitgeest`.
- Twitter-link (`brw_utg`) vervalt, het account bestaat niet meer. Social links: alleen Facebook (facebook.com/brandweeruitgeest) en Instagram (@brandweeruitgeest).
- Verouderde feiten (aantal vrijwilligers, voertuigen, copyright "2004 - 2020"): lijst maken, niet zelf invullen.
- Historische uitrukken bevatten soms bedrijfsnamen bij automatische brandmeldingen (bijv. `ABM vd Lem`). Die blijven staan (besluit 27-09-2026).

## Fase 4: uitrukken en P2000-import

### Dataschema (`data/uitrukken/JJJJ.csv`)

| kolom      | verplicht | voorbeeld               | opmerking                                          |
|------------|-----------|-------------------------|----------------------------------------------------|
| nr         | ja        | 14                      | volgnummer binnen het jaar                         |
| datum      | ja        | 2022-02-18              | ISO                                                |
| tijd       | nee       | 21:37                   | leeg voor historische data                         |
| prio       | ja*       | 2                       | toegestane waarden: 1, 2, 3                        |
| melding    | ja        | Stormschade             | zonder "Prio X"-prefix, die gaat naar `prio`       |
| adres      | ja*       | Handelstraat            | straat of hectometrering, geen huisnummer (nieuw)  |
| plaats     | ja*       | Heemskerk               | ingevuld, ook bij Uitgeest                         |
| bron       | ja        | legacy / eigen / p2000  | p2000: uit P2000-meldingen                         |
| publiceren | ja        | ja                      | `nee` houdt de regel in de data maar uit de site   |

Historische data wordt zo letterlijk mogelijk overgenomen. Alleen splitsen (prio, plaats), niet herschrijven. Uitzondering: `nr` wordt per jaar opnieuw doorgenummerd, 1 t/m N op datumvolgorde (besluit 27-09-2026; de oude site had gaten en dubbele nummers).

\* Verplicht voor alle nieuwe regels (`bron=eigen` en `bron=p2000`). Voor historische regels (`bron=legacy`) geldt, besluit Sven 27-09-2026: wat we niet weten, vullen we niet in.

- Historische regels zonder prio in de bron (2008 t/m 2012 en 2 afwijkende regels): `prio` blijft leeg. Niet raden, niet afleiden.
- Historische regels zonder plaats: de oude site vermeldde de plaats alleen als die niet Uitgeest was (bijv. "Handelstraat, Heemskerk"). Regels met een straatnaam zonder plaatsnaam krijgen daarom plaats = Uitgeest. Regels met een wegnummer of hectometrering (A9, N203) krijgen geen plaats.
- Historische regels waarvan het adres alleen een plaatsnaam is (bijv. "Haarlem"): die naam wordt `plaats`, `adres` blijft leeg.
- Historische regels met een huisnummer (2013 t/m 2016) behouden het huisnummer vanwege de historische waarde. Uitzondering (besluit 28-09-2026, AVG): bij medische meldingen (reanimatie, afhijsen, letsel, persoon te water e.d.) wordt het huisnummer weggehaald; `check.py` faalt daarop.
- Bedrijfs- en instellingsnamen in historische regels (bijv. `ABM vd Lem`) blijven staan.
- `check.py` faalt op een gepubliceerde nieuwe regel zonder geldige prio, adres of plaats, en op een ingevulde prio buiten 1, 2, 3.
- Nieuwe regels (besluit Sven 27-09-2026): huisnummers worden weggehaald en gemeld (niet afgekeurd); oefeningen zijn geen uitrukken en worden overgeslagen (besluit 28-09-2026); een alarmering die daarna wordt ingetrokken telt wel als uitruk, maar het intrekbericht is geen aparte uitruk: alarm plus intrekking is samen 1 uitruk met de oorspronkelijke melding (besluit 29-09-2026); geen soorten meldingen verborgen; de melding is een korte tekst uit de vertaaltabel in `tools/meldingen.yaml`.

### Import uit P2000 (`tools/import_p2000.py`, `.github/workflows/p2000.yml`)

- Nieuwe uitrukken komen automatisch uit P2000, via Home Assistant. Ontwerp in `PLAN-P2000.md`.
- Alleen capcode 0107711 (Vrijwilligers) telt als uitruk van brandweer Uitgeest (besluit Sven 28-09-2026).
- Idempotent: opnieuw draaien geeft geen dubbele regels. Keurt een regel zonder geldige prio, adres of plaats af.
- Home Assistant stuurt P2000-uitrukken naar `master` (de echte site) sinds de livegang van 28-09-2026. Met `ref: v2` gaat een melding naar de testsite.
- Elke nieuwe P2000-uitruk met `publiceren=ja` wordt na het publiceren van de site automatisch op Facebook en Instagram geplaatst (`tools/sociaal.py`, besluit Sven 01-10-2026, mag van de VRK): alle soorten, dezelfde gegevens als op de site, met een vaste afbeelding in de huisstijl. Alleen vanaf `master`.
- Er komt geen andere import bij. De herkomst van regels met `bron=eigen` wordt nergens beschreven, niet in code, documentatie, commits of op de site (besluit Sven 28-09-2026).

### Privacyfilter (in de import en nogmaals in `check.py`, alleen op uitrukkendata)

- Huisnummers, postcodes, kentekens, telefoonnummers en persoonsnamen: regel afkeuren en melden, niet stil corrigeren. Uitzondering: huisnummers in historische regels (`bron=legacy`) blijven staan, zie Dataschema.
- Geen medische details, geen informatie over slachtoffers.
- Meldingssoorten die standaard `publiceren=nee` krijgen staan in `tools/meldingen.yaml` (bijv. assistentie ambulance bij personen, suïcidepreventie, zedenzaken). Die lijst vult Sven, Claude doet alleen een voorstel.
- Vrije tekst nooit overnemen.
- Beleid VRK (via Sven, 28-09-2026): P2000-meldingen mogen direct op de site. Alle andere informatie over uitrukken pas 24 uur na de uitruk.
- Automatische P2000-publicatie via Home Assistant: ontwerp in `PLAN-P2000.md`. Capcodes brandweer Uitgeest: 0107711 Vrijwilligers (telt als uitruk), 0107702 Kazernecoördinator, 0107784 Kazernehek, 0107781 Lichtkrant, 0107710 Bevelvoerder van Dienst.

### Weergave

- `/uitrukken/`: overzicht per jaar met aantallen (trend 2008 tot nu), links naar jaarpagina's.
- `/uitrukken/JJJJ/`: tabel met datum, prio, melding, adres; totalen per soort bovenaan.
- Filteren op maand/soort werkt via ankers zonder JS.

## Beveiliging

### Direct actiepunt (buiten Claude om)

`legacy/config.toml` bevat een Google Maps API-key in een publieke repo, en die staat in de git-historie. Sven trekt deze key in via Google Cloud Console. Claude neemt de key nergens over.

### `.htaccess` (gegenereerd door `build.py`)

- HTTPS-redirect, host normaliseren (kies `brandweeruitgeest.nl` zonder www, 301 van www).
- `Strict-Transport-Security: max-age=31536000; includeSubDomains`
- `Content-Security-Policy: default-src 'self'; img-src 'self' data:; style-src 'self'; script-src 'self'; font-src 'self'; connect-src 'self'; frame-ancestors 'none'; base-uri 'self'; form-action 'self'; upgrade-insecure-requests`
- `X-Content-Type-Options: nosniff`, `Referrer-Policy: strict-origin-when-cross-origin`, `Cross-Origin-Opener-Policy: same-origin`
- `Permissions-Policy: geolocation=(), camera=(), microphone=(), browsing-topics=()`
- `Options -Indexes`, geen toegang tot dotfiles
- Caching: `immutable` voor gehashte assets, korte cache voor HTML
- Alle 301's uit `data/redirects.csv`
- Eigen 404-pagina

Geen inline `<script>`, `<style>` of `style=""`, anders breekt de CSP.

Let op: op de server staat nu een tijdelijke `.htaccess` die doorverwijst naar brandweer.nl/kazerne/uitgeest. De eerste deploy van v2 overschrijft die. Dat is het moment van livegang en gebeurt alleen na expliciet akkoord.

## Fase 5: build, deploy en livegang

- Vervang AppVeyor door GitHub Actions (`.github/workflows/build.yml`):
  - bij elke push en PR: `pip install -r requirements.txt`, `python build.py`, `python tools/check.py`
  - deploy alleen vanaf `master`, alleen na geslaagde check
- De huidige deploy gebruikt `curl -k` over plain FTP (TLS-verificatie uit, wachtwoord onversleuteld). Nieuwe deploy (besluit 27-09-2026): `tools/deploy.py` via FTPS met certificaatcontrole naar een nieuwe FTP-server. Secrets `FTP_SERVER`, `FTP_POORT`, `FTP_GEBRUIKER`, `FTP_WACHTWOORD` (optioneel `FTP_MAP`) staan als environment secrets in de GitHub-omgeving `productie`.
- Alleen een push van Sven (`SvenKortekaas`) publiceert: `master` naar de echte site met `FTP_GEBRUIKER_PROD` en `FTP_WACHTWOORD_PROD`, `v2` naar de testsite met `FTP_GEBRUIKER` en `FTP_WACHTWOORD` (besluit Sven 28-09-2026; server en poort gelijk, keuze in `tools/publiceer.py`). De workflow controleert repo, branch en actor. Pull requests en forks krijgen nooit toegang tot de secrets.
- Livegang gedaan op 28-09-2026 met `OPRUIMEN` op `master` (eerst droog). Opruimen verwijdert alles wat niet bij de site hoort; `.well-known`, `.cagefs` en `.cl.selector` blijven. Terugdraaien naar de tijdelijke doorverwijzing: `TERUGDRAAIEN` (zet `tools/htaccess-terugdraaien` terug). Geen required reviewer op de omgeving `productie` (besluit Sven 28-09-2026): een push van Sven naar `master` (en tijdens de testfase `v2`) publiceert direct. Daarna synchroniseert elke publicatie via een manifest. Stappenplan: `MIGRATIE.md`, hoofdstuk 7.
- Deploy synchroniseert `public/` met de server. Verwijderen van oude Hugo-bestanden op de server pas na akkoord en na een backup.
- Geen verwijzingen naar het testadres (v2.brandweeruitgeest.nl) in de gebouwde site of de sitecode. De testsite wordt gebouwd met `BOUW_OMGEVING=test` (noindex en `Disallow: /`), de echte site met `live` (besluit Sven 28-09-2026). Runners vast op `ubuntu-24.04`.
- Livegang-checklist in `MIGRATIE.md`: redirects getest met `curl -I` op de volledige oude URL-lijst, securityheaders gecontroleerd, Lighthouse gedraaid, tijdelijke doorverwijzing weg.

## Prestaties

- Budget per pagina: HTML + CSS + JS < 100 kB (exclusief afbeeldingen). Eerste afbeelding < 150 kB. Geen enkel afbeeldingsbestand > 300 kB (de oude regel uit `file_sizes.sh` blijft gelden).
- Afbeeldingen met `width`/`height`, `srcset`, `loading="lazy"` behalve boven de vouw.
- Doel Lighthouse: 100 op alle vier de categorieën.

## Controles (`tools/check.py`, build faalt als één controle faalt)

1. Geen externe resources: geen externe URL in `src`, stylesheet-`href`, `@import`, `url()`, `<iframe>`, `<object>`.
2. Geen interne dode links. Elke URL uit de oude inventaris (`data/legacy-urls.csv`) geeft de daar vastgelegde 200, 301 of 410.
3. Privacyfilter over alle gepubliceerde uitrukken.
4. Aantal uitrukken per jaar 2008 t/m 2022 gelijk aan de legacy-telling.
5. Budgetten en maximale bestandsgrootte.
6. Elke afbeelding heeft `alt`, elke pagina een `title` en `description`, HTML valideert.

## Werkwijze voor Claude

- Werk per fase en stop na elke fase voor akkoord.
- Vraag voordat je een dependency toevoegt, content inhoudelijk wijzigt, bestanden verwijdert of iets aan deploy of server verandert.
- Deploy nooit zelf, raak nooit secrets aan.
- Kleine, beschrijvende commits in het Nederlands. Vermeld AI-ondersteuning met de trailer `Co-Authored-By: Claude <noreply@anthropic.com>`. Nooit links naar een AI-sessie of gesprek in commits, code, PR's of documentatie.
- Geen echte persoonsgegevens in testdata.
- `README.md` en `CONTRIBUTING.md` bijwerken voor de nieuwe werkwijze (Python in plaats van Hugo), de open bijdrage-gedachte uit de huidige README behouden.

## Open vragen

- Is er een testlocatie (subdomein of map) voor een proefdeploy?

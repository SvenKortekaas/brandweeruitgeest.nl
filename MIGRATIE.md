# MIGRATIE.md: van Hugo naar v2

Resultaat van fase 1 (analyse en URL-inventaris), 27-09-2026. Alles hieronder is een voorstel tot Sven akkoord geeft. Punten met **Besluit** zijn al beslist, zie `VOORTGANG.md`. **Akkoord op het geheel: 27-09-2026.**

## 1. Inventaris

### Werkwijze

- De oude site is gebouwd met Hugo 0.119.0 extended: `hugo -s legacy -d <map>`.
- De build faalt standaard op 3 `tweet`-shortcodes, omdat Hugo dan de Twitter-API aanroept. Voor de inventaris is tijdelijk (buiten de repo) een offline vervanger van die shortcode gebruikt. `legacy/` zelf is niet gewijzigd.
- `tools/inventaris_legacy.py` maakt van de build-output `data/legacy-urls.csv`: elke URL met soort, actie (200, 301 of 410) en doel. Dit is ook de lijst die `check.py` later gebruikt ("elke oude URL geeft 200, 301 of 410").

### Aantallen uit de build

| soort | aantal | voorstel |
|---|---|---|
| Pagina's (home, nieuws, over-ons, voertuigen, posten, P2000, disclaimer) | 7 | blijven (200) |
| Nieuwsartikelen 2016 t/m 2020 | 31 | blijven (200), pad gelijk |
| Voertuigpagina's `/12-20xx/` | 7 | 5 via 301 naar `/voertuigen/12-20xx/`; 12-2031 en 12-2061 via 301 naar `/voertuigen/` |
| Uitrukken `/2008/` t/m `/2022/` | 15 | 301 naar `/uitrukken/JJJJ/` |
| Tag- en categoriepagina's incl. `page/N` en feeds | 129 | 301 naar `/nieuws/` |
| Paginering `/page/N/` en `/nieuws/page/N/` | 8 | zie tabel 3 |
| Feeds `/index.xml`, `/nieuws/index.xml` | 2 | zie tabel 3 |
| Alias `/p2000/betekenis-p2000-meldingen/` | 1 | 301 |
| `sitemap.xml`, `robots.txt`, `404.html` | 3 | blijven (nieuw gegenereerd) |
| Favicons en manifest | 21 | 9 blijven, 12 via 301 |
| Gebruikte afbeeldingen (nieuws, voertuigen, carousel, logo) | 159 | 301 naar genormaliseerd pad (fase 3) |
| Foto's van 12-2031 en 12-2061 | 8 | 410 |
| Ongebruikte afbeeldingen | 41 | 410, zie 4.6 |
| Thema-afbeeldingen, CSS en JS van het Hugo-thema | 41 | 410, zie 4.6 |
| **Totaal** | **473** | |

### Inhoud

- **Nieuws:** 31 artikelen, allemaal met `title`, `date`, `description`, `author`, `banner`, `images`, `tags`, `categories`. 21 bestanden noemen een fotobron (o.a. 112-Uitgeest.nl), die blijven staan.
- **Shortcodes:** `figure` 151x, `gallery` 31x, `load-photoswipe` 31x, `tweet` 3x, `youtube` 2x, `incident-location` 2x, `facebook-post` 1x. `tweet` en `youtube` stonden niet in de inventaris vooraf.
- **Voertuigen:** 7 pagina's (12-2001, 12-2002, 12-2011, 12-2030, 12-2031, 12-2060, 12-2061) en `voertuigen.md`. Er is ook een fotomap `12-2003` zonder pagina.
- **Posten Kennemerland:** Leaflet-kaart via unpkg met posten uit `legacy/static/js/leaflet_brw_posten_kennemerland.js`, plus inline `style=""`.
- **Data:** carousel (3 veiligheidstips) en clients (6 voertuigtegels op home) gaan mee. Features en testimonials vervallen.
- **Afbeeldingen:** 236 bestanden in `legacy/static`, geen enkele boven 300 kB, geen EXIF of GPS gevonden. Grootste afmeting 1920 px, mediaan 1152 px. 135 bestandsnamen bevatten spaties, haakjes of hoofdletterextensies (bijv. `IMG_3695(Medium).JPG`).
- **Uitrukken:** 1528 regels in 15 jaarbestanden (de brief schatte ca. 1550). Het aantal `<tr>` in elke tabelbody is gelijk aan het aantal geparste regels, elke regel heeft precies 4 kolommen.

| jaar | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| regels | 95 | 113 | 119 | 127 | 112 | 116 | 104 | 91 | 106 | 126 | 124 | 76 | 98 | 69 | 52 |

## 2. Voorstel nieuwe URL-structuur

| pad | inhoud |
|---|---|
| `/` | home: werving, laatste uitrukken, adres en contact |
| `/nieuws/` en `/nieuws/page/N/` | archief van de 31 oude artikelen, 10 per pagina (zoals nu). Voorlopig komt er geen nieuw nieuws bij. |
| `/nieuws/JJJJ/MM/DD/slug/` | nieuwsartikel, ongewijzigd |
| `/nieuws/index.xml` | feed |
| `/uitrukken/` | overzicht per jaar met aantallen (akkoord 27-09-2026) |
| `/uitrukken/JJJJ/` | jaarpagina |
| `/voertuigen/` en `/voertuigen/<nummer>/` | huidige voertuigen: 12-2030, 12-2001, 12-2002, 12-2060, 12-2011, 12-1536 (nieuw) |
| `/over-ons/`, `/posten-kennemerland/`, `/betekenis-p2000-meldingen/`, `/disclaimer/` | ongewijzigd |
| `/privacy/` | nieuw: geen cookies, geen tracking |
| `/sitemap.xml`, `/robots.txt`, `/404.html` | nieuw gegenereerd |

## 3. Redirecttabel

Volledige lijst per URL: `data/legacy-urls.csv`. Samengevat als regels:

| oud | nieuw | code |
|---|---|---|
| `/12-20xx/` (2001, 2002, 2011, 2030, 2060) | `/voertuigen/12-20xx/` | 301 |
| `/12-2031/`, `/12-2061/` (niet meer in gebruik) | `/voertuigen/` | 301 |
| `/JJJJ/` (2008 t/m 2022) | `/uitrukken/JJJJ/` | 301 |
| `/tags/...` en `/categories/...` (alles, ook `page/N` en `index.xml`) | `/nieuws/` | 301 |
| `/index.xml` | `/nieuws/index.xml` | 301 |
| `/page/1/` | `/` | 301 |
| `/page/N/` (2 t/m 4) | `/nieuws/page/N/` | 301 |
| `/nieuws/page/1/` | `/nieuws/` | 301 |
| `/p2000/betekenis-p2000-meldingen/` | `/betekenis-p2000-meldingen/` | 301 |
| `/android-chrome-*.png`, `/apple-touch-icon-*x*.png` | `/apple-touch-icon.png` | 301 |
| `/img/...` gebruikte afbeeldingen | genormaliseerd pad, vastgelegd in `data/redirects.csv` in fase 3 | 301 |

Let op: `/nieuws/page/N/` blijft alleen 200 zolang er genoeg artikelen zijn voor die pagina. Valt een pagina weg, dan komt er een 301 naar `/nieuws/`.

## 4. Twijfelgevallen

### 4.1 Uitrukken zonder geldige prio

Besluit 27-09-2026: `prio` is verplicht (1, 2 of 3) en wordt niet geraden of afgeleid. Tellingen:

| jaar | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 t/m 2017 | 2018 | 2019 t/m 2022 | totaal |
|---|---|---|---|---|---|---|---|---|---|---|---|
| zonder geldige prio | 95 | 113 | 119 | 127 | 112 | 0 | 1 | 0 | 1 | 0 | **568** |

**Besluit 27-09-2026: niet vullen, `prio` blijft leeg.**

- 2008 t/m 2012 hebben nergens een prio (566 regels). Vanaf 2013 wel.
- 2014: `Prio 4 Wateroverlast` (prio 4 bestaat niet in het schema).
- 2018: `Prio 12 CO Melder` (waarschijnlijk tikfout voor 1 of 2).

### 4.2 Uitrukken zonder plaats

Besluit 27-09-2026: regels zonder plaatsnaam krijgen `Uitgeest`, behalve regels met een wegnummer of hectometrering.

**Weg of hectometrering zonder plaats: 235 regels. Besluit 27-09-2026: geen plaats.**

| jaar | 2008 | 2009 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 | 2018 | 2019 | 2020 | 2021 | 2022 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| aantal | 13 | 17 | 24 | 28 | 16 | 25 | 19 | 16 | 23 | 22 | 13 | 11 | 7 | 0 | 1 |

Voorbeelden: `A9`, `N203`, `N203 58,7`, `A9 L 58,1c`. Let op: de komma in een hectometrering is geen scheiding tussen straat en plaats.

**Extra gevallen die de regel "geen plaatsnaam = Uitgeest" niet goed dekt:**

- **Adres is alleen een plaatsnaam (41 regels, vooral 2008 t/m 2012):** bijv. adres `Haarlem`, `Beverwijk`, `Akersloot`, `Zaandam`. **Besluit 27-09-2026: die naam wordt plaats, adres leeg.**
- **Plaats tussen haakjes (17 regels, 2012, 2013, 2016):** bijv. `Ringvaart (Beverwijk)`, `Klein Dorregeest (Akersloot)`. Voorstel: splitsen naar plaats. Ook `(HMS)` (vermoedelijk Heemskerk) en `(Molen De Kat)` (geen plaats).
- **Komma zonder plaats erachter:** soms staat een bedrijfsnaam voor de komma, bijv. `Bobs Party Palace, Westerwerf` of `De Lelie, Rembrandtsingel, Akersloot`. Voorstel: alleen splitsen als het deel na de laatste komma een bekende plaatsnaam is, de rest handmatig beoordelen.
- **Andere schrijfwijzen:** `Provincialeweg 54,6` (hectometrering zonder wegnummer, 2009 en 2010), `Oprit 10 A9 Castricum`.

### 4.3 Huisnummers in historische uitrukken (privacy)

Ca. 198 regels in 2013 (55), 2014 (58), 2015 (42) en 2016 (43) bevatten een huisnummer, bijv. `Geesterweg 67`, `Prinses Beatrixlaan 18 C`, ook bij meldingen als `Reanimatie`. Het schema staat nooit een huisnummer toe en het privacyfilter keurt zulke regels af. **Besluit 27-09-2026: huisnummers blijven staan vanwege historische waarde.** Het privacyfilter maakt hiervoor een uitzondering bij `bron=legacy`.

### 4.4 Bedrijfs- en instellingsnamen

118 regels noemen een bedrijf of instelling, bijna allemaal automatische brandmeldingen:

- 2008 t/m 2012 in de melding: `ABM vd Lem`, `ABM Geesterheem`, `ABM de Waterjuffer`, `ABM Monkey Town`, `ABM de Slimp`, `ABM Heliomare`, `ABM Van der Valk Hotel`, `ABM KDV De Regenboog`, `ABM Kindergarden Waldijk`, `ABM Vrijburgschool`, `ABM Atece`, `ABM Vos Industrial Group`, `ABM Spanjaard HDC`, `ABM Westerheem`, `ABM Recreatieschap`.
- 2016 t/m 2022: `Brandmelding OMS` met straat, en een enkele naam in het adres, bijv. `Bobs Party Palace`, `De Lelie`, `Nuon centrale`, `Gasunie`, `OMS Politiebureau`, `OMS Slimp`.

**Besluit 27-09-2026: blijven staan.**

### 4.5 Overige datakwaliteit (alleen melden, niet stil corrigeren)

- **Nummering:** 2016 mist nr 51; 2018 heeft nr 5 en nr 24 dubbel. **Besluit 27-09-2026: per jaar opnieuw doornummeren, 1 t/m N op datumvolgorde.** `check.py` telt regels.
- **Maandafkortingen:** 2017 gebruikt `mar`, 2018 `maa` naast `mrt`. Omzetten naar ISO-datum is eenduidig.
- **Tekencodering:** 5 regels in 2014 en 2016 met kapotte tekens (`PatiÃ«nt`, `Pati�nt`). **Besluit 27-09-2026: herstellen naar `Patiënt`,** verder niets aan de tekst veranderen.
- **Tikfouten:** o.a. `Stromschade`, `Vezorging`. Voorstel: laten staan (letterlijk overnemen).
- **Gevoelige meldingssoorten:** o.a. `Reanimatie` (ca. 50), `Assistentie ambulance` en `Afhijsen patiënt` (ca. 60), `Persoon te water`. Die komen in fase 4 in het voorstel voor `tools/meldingen.yaml`.

### 4.6 Bestanden zonder duidelijke bestemming

Principe 4 zegt: elke oude URL geeft een pagina of een 301. Voor deze groepen is dat niet zinvol:

**Besluit 27-09-2026: alles in deze paragraaf krijgt `410 Gone`.** Dit is een bewuste uitzondering op principe 4.

- **CSS en JS van het Hugo-thema (21 bestanden, `/css/`, `/js/`).**
- **Thema-afbeeldingen (20 bestanden),** bijv. `/img/texture-violet.png`, `/img/clients/customer-1.png`, `/img/testimonials/...`. Voorstel: `410 Gone`.
- **Ongebruikte afbeeldingen (41 bestanden):** 36 foto's in 7 nieuwsmappen zonder artikel (2017 en 2021, bijv. `2017-07-19-Prio2BuitenbrandLagendijk`), 4 foto's van voertuig 12-2003 zonder pagina, en `logo-small.png`. Gaan niet mee naar de nieuwe site.

## 5. Inhoudelijke aanpassingen (fase 3, niet stil doen)

- **Besluit 27-09-2026:** "Helden gezocht" (home) en de wervingstekst op `over-ons` verwijzen naar de VRK-vacature brandweervrijwilliger (https://www.werkenbijdevrk.nl/vacatures/brandweervrijwilliger/8fa2ec35-00b3-4844-be28-4cba4928301b). ikwilbijbrandweeruitgeest.nl komt er voorlopig niet.
- Contactformulier (Formspree) vervalt, wordt `mailto:info@brandweeruitgeest.nl`. In `config.toml` staat het adres onvolledig als `info@brandweeruitgeest`; dat wordt hersteld.
- **Besluit 27-09-2026:** Twitter-link `brw_utg` vervalt. Social links: alleen Facebook en Instagram (@brandweeruitgeest).
- **Besluit 27-09-2026:** YouTube-video's (2x) worden gewone links naar de video. Tweets (3x) en de Facebook-post (1x) vervallen zonder link.
- **Besluit 27-09-2026:** Posten Kennemerland: de Leaflet-kaart wordt een lijst van posten met per post een link naar OpenStreetMap. Of de lijst nog klopt, controleert Sven.
- **Verouderde feiten (niet zelf invullen):**
  - `over-ons`: "24 vrijwilligers" (3x).
  - `over-ons`: "2 tankautospuiten, 12-2030 en 12-2031, 2 boten, 12-2011 en de 12-2010 ..." (voertuigenlijst).
  - `over-ons`: "in 2011 haalde we het record van 127 uitrukken" (klopt t/m 2022, maar niet bijgehouden).
  - `over-ons`: eisen voor nieuwe leden (18 t/m 40 jaar, woont in Uitgeest).
  - Footer: "Copyright (c) 2004 - 2020".
  - Voertuigen: **besluit 27-09-2026:** huidige voertuigen zijn 12-2030, 12-2001, 12-2002, 12-2060, 12-2011 en 12-1536 (van Vakbekwaamheid, staat op de kazerne). 12-2031 en 12-2061 zijn er niet meer.
  - Sven komt later uitgebreid terug op de actuele feiten.

## 5b. Uitgevoerd in fase 3 (28-09-2026)

Gedaan met `tools/migrate_hugo.py` (opnieuw te draaien, eerst zonder `--apply` voor een rapport):

- **Uitrukken 2008 t/m 2022:** per jaar precies evenveel regels als in de oude tabellen.
  - Prio en plaats zijn gesplitst volgens de besluiten en er is per jaar doorgenummerd.
  - De kapotte tekens zijn hersteld naar "Patiënt".
  - Bij wegen staat de plaats alleen als de bron hem direct na de hectometer noemt, bijv. "A9 L 61.0 Uitgeest".
  - "Velsen – Noord" en "Corus Beverwijk" krijgen de juiste plaats.
  - "(HMS)" (2012) heeft geen plaats gekregen: afkorting, niet geraden.
- **Nieuws:** 31 artikelen met dezelfde URL's.
  - Tags en categorieën zijn weg.
  - YouTube (ook de ingesloten video in "Hulpverleningsoefening in de kerk") is een gewone link geworden.
  - De twee kaartjes zijn links naar OpenStreetMap geworden.
  - De tweets en de Facebook-post zijn weggehaald.
  - Links naar de eigen site wijzen direct naar het nieuwe adres.
  - Fotocredits staan in de tekst en zijn behouden.
- **Foto's:** 159 oude paden krijgen een 301 naar de nieuwe versie (`data/afbeeldingen-oud.csv`).
  - Nieuwsfoto's hebben een algemene alt-tekst ("Foto 2 van 6 bij: ..."). Die kan later per foto beter.
  - `standard_news_image.jpeg` stond ten onrechte op 410; het is de banner van "Zeer grote brand Krommenie" en krijgt nu een 301.
- **Posten Kennemerland:** tabel met 19 posten, elk met een link naar OpenStreetMap en de website uit de oude kaart. Of alle posten en links nog kloppen, controleert Sven.
- **Over ons:** tekst letterlijk overgenomen, met onderaan een nieuw stukje "Aanmelden" met de VRK-vacature en het mailadres. De verouderde feiten (24 vrijwilligers, voertuigen, eisen) staan er nog in; Sven komt erop terug.
- **Disclaimer en privacyverklaring:** opnieuw geschreven volgens de AVG (besluit 27-09-2026). Contactformulier en de oude privacyparagraaf in de disclaimer zijn weg.
- **Controle:** `check.py` staat nu strikt (`MIGRATIE_KLAAR = True`). Alle 473 oude URL's geven de vastgelegde 200, 301 of 410.

## 6. Wat vervalt

- Hugo, hugo-universal-theme, AppVeyor (`appveyor.yml`, `deploy.sh`), `minify.sh`, `file_sizes.sh` (de 300 kB-regel gaat naar `check.py`).
- Tag- en categoriepagina's en hun feeds (301 naar `/nieuws/`). Tags en categorieën verdwijnen ook bij de artikelen (besluit 27-09-2026).
- Zoekwidget, carousel-JS (Owl), PhotoSwipe, Leaflet, Google Maps (incl. API-key), Font Awesome, jQuery, Bootstrap.
- Contactformulier via Formspree.
- Embeds van Twitter, Facebook en YouTube.
- Features en testimonials (stonden al uit).
- Social-meta voor Facebook (`facebook_app_id` e.d.).
- Forestry-configuratie (`.forestry/`).

## 7. Publiceren (uploadplan)

Besluit 27-09-2026: publiceren via GitHub Actions naar een nieuwe FTP-server. Alleen een push van Sven naar `master` werkt de website bij.

### Hoe het werkt

- `.github/workflows/build.yml` bouwt en controleert de site bij elke push en pull request. Daarbij zijn geen FTP-gegevens beschikbaar.
- Publiceren gebeurt alleen als alles klopt:
  - de push of handmatige start is op `master`;
  - hij komt van `SvenKortekaas`, ook bij opnieuw starten;
  - het is de officiële repo, geen fork;
  - de controles zijn geslaagd.
- De FTP-gegevens staan in de GitHub-omgeving `productie` en niet in de repo. Pull requests en forks kunnen er nooit bij.
- `tools/deploy.py` gebruikt altijd FTP met TLS (FTPS) en controleert het certificaat. Onversleuteld FTP weigert het. Het oude `curl -k` over plain FTP vervalt. De nieuwe server ondersteunt FTPS (Sven, 27-09-2026).
- Bij elke update worden alleen gewijzigde bestanden geüpload. Wat niet meer in de site staat, wordt verwijderd. Op de server houdt `.deploy-manifest.json` bij wat er geplaatst is; dat bestand is via de website niet op te vragen.
- `.htaccess` gaat altijd als laatste omhoog. Pas dan is de nieuwe versie actief.

### Eenmalig instellen in GitHub (Sven)

1. **Omgeving:** Settings, Environments, New environment `productie`.
   - Bij Deployment branches kies je "Selected branches" met alleen `master`.
   - Geen required reviewers (besluit Sven 28-09-2026, het plan van 27-09-2026 vervalt): elke push van Sven naar `v2` of `master` publiceert meteen, zonder te vragen.
2. **Secrets in die omgeving** (Environment secrets, niet Repository secrets):
   - `FTP_SERVER`, bijv. ftp.jouwhost.nl
   - `FTP_POORT`, meestal 21
   - `FTP_GEBRUIKER`
   - `FTP_WACHTWOORD`
   - optioneel `FTP_MAP`: de webmap op de server als dat niet de map is waarin je na inloggen staat, bijv. `public_html`
3. **Wie mag pushen:** Settings, Collaborators. Controleer dat niemand anders schrijfrechten heeft.
4. **Actions:** Settings, Actions, General.
   - Zet "Workflow permissions" op "Read repository contents".
   - Zet bij fork pull requests "Require approval for all external contributors" aan.
5. **Branch protection voor `master` (aanbevolen):** Settings, Branches, Add rule. Kies "Require status checks to pass" (job `bouwen`) en "Do not allow force pushes".
6. **AppVeyor uitschakelen** voordat v2 naar `master` gaat. Verwijder daar ook de oude FTP-gegevens.
7. **Oude FTP-wachtwoord wijzigen.** Het ging jarenlang onversleuteld over het internet.

### Testfase op v2.brandweeruitgeest.nl (28-09-2026)

- De FTP-gegevens in GitHub wijzen naar de map van v2.brandweeruitgeest.nl. Zo kun je alles testen zonder de echte site te raken.
- Tijdens de testfase mag branch `v2` publiceren. Zet daarvoor in de omgeving `productie` bij Deployment branches naast `master` ook `v2`. Elke publicatie wacht op jouw klik.
- Op v2.brandweeruitgeest.nl stuurt de site `X-Robots-Tag: noindex`, zodat zoekmachines de testsite niet oppakken. Op het hoofddomein gebeurt dat niet.
- De eerste publicatie naar de testmap: Run workflow op `v2` met `OPRUIMEN`, eerst droog.
- Livegang: laat bij de hosting het hoofddomein naar dezelfde map wijzen. FTP-gegevens blijven gelijk. Daarna haal ik `v2` weer uit de workflow en loopt publiceren alleen via `master`.

### Livegang: stappenplan (28-09-2026, bijgewerkt)

Besluit Sven 28-09-2026: twee FTP-accounts op dezelfde server en poort. `FTP_GEBRUIKER` en `FTP_WACHTWOORD` komen uit in de map van v2.brandweeruitgeest.nl (testsite), `FTP_GEBRUIKER_PROD` en `FTP_WACHTWOORD_PROD` (of `FTP_PASSWORD_PROD`) in de map van de echte site. `master` publiceert naar de echte site, `v2` naar de testsite. De echte site krijgt een verse start: de map wordt leeggemaakt, alleen `.cagefs`, `.cl.selector` en `.well-known` blijven.

1. **Sven (gedaan 28-09-2026):** AppVeyor uit, oud FTP-wachtwoord gewijzigd, backup gemaakt, `_PROD`-secrets aangemaakt.
2. **Claude:** livegang-commit op `v2`: test- en livebouw (`BOUW_OMGEVING`), keuze FTP-gegevens per branch (`tools/publiceer.py`), beschermde mappen, runners vast op `ubuntu-24.04`.
3. **Claude:** pull request `v2` naar `master` (akkoord Sven 28-09-2026).
4. **Sven:** pull request samenvoegen. De eerste publicatie naar de echte map stopt bewust: daar staat nog geen manifest.
5. **Claude:** "Bouwen en publiceren" op `master` met `OPRUIMEN`, eerst droog. De lijst nakijken; staat er iets onverwachts (bijv. mail of logs, of blijkt de FTP-map de thuismap in plaats van de webmap), dan eerst Sven vragen.
6. **Claude:** dezelfde run echt. De oude bestanden en de tijdelijke doorverwijzing verdwijnen, de nieuwe `.htaccess` gaat als laatste omhoog. Dat is het moment van livegang.
7. **Claude:** "Site controleren" op `https://brandweeruitgeest.nl` (oude URL's, www, http, headers) en Lighthouse.
8. **P2000 omzetten:** Claude zet in Home Assistant `ref` op `master`. De omgeving `p2000` heeft de `_PROD`-secrets nodig (Sven).

**Terugdraaien:** "Bouwen en publiceren" op `master` met `TERUGDRAAIEN` (zet alleen de tijdelijke doorverwijzing terug in de map van de echte site), of de backup terugzetten.

### Eerste livegang (oude site opruimen) (vervallen, zie hierboven)

1. **Backup:** download de volledige inhoud van de server met een FTP-programma (bijv. FileZilla) en bewaar die buiten GitHub.
2. **Samenvoegen:** v2 gaat naar `master` (na akkoord, via pull request).
   - De eerste automatische publicatie stopt dan bewust met de melding "geen manifest op de server". Er verandert nog niets.
3. **Droog opruimen:** Actions, "Bouwen en publiceren", Run workflow op `master`.
   - Vul bij opruimen `OPRUIMEN` in en laat droog aangevinkt.
   - In het log staat welke bestanden omhoog gaan en welke oude bestanden weg gaan.
4. **Controleren:** kijk de lijst na.
   - Alles op de server mag weg (Sven, 27-09-2026). Alleen `.well-known` blijft staan, die is nodig om het HTTPS-certificaat te vernieuwen.
5. **Echt opruimen:** start opnieuw met `OPRUIMEN` en droog uit.
   - Oude Hugo-bestanden en de tijdelijke doorverwijzing naar brandweer.nl verdwijnen.
   - De nieuwe `.htaccess` gaat als laatste omhoog. Dat is het moment van livegang.
6. **Daarna:** elke push van Sven naar `master` werkt de site automatisch bij.

### Terugdraaien

De `.htaccess` die nu (27-09-2026) op de server staat, stuurt alle bezoekers tijdelijk door naar brandweer.nl:

```
RewriteEngine On
RewriteRule ^(.*)$ https://www.brandweer.nl/kazerne/uitgeest/ [R=302,L]
```

Dit bestand staat ook in de repo als `tools/htaccess-terugdraaien`. Zo zet je het terug:

- **Via GitHub:** Actions, "Bouwen en publiceren", Run workflow op `master`. Vul bij terugdraaien `TERUGDRAAIEN` in en zet droog uit.
  - Alleen de `.htaccess` wordt vervangen. De site verwijst dan meteen weer door naar brandweer.nl.
  - De volgende gewone publicatie zet de nieuwe `.htaccess` automatisch terug.
- **Handmatig:** upload met FileZilla een `.htaccess` met de twee regels hierboven.
- **Alles terug:** zet de backup van vóór de livegang terug met FileZilla.

## 8. Livegang-checklist (fase 5)

- [x] GitHub-omgeving `productie` met secrets ingesteld (ook `_PROD`), AppVeyor uit, oud FTP-wachtwoord gewijzigd (Sven, 28-09-2026).
- [x] Backup van de server gemaakt (Sven, 28-09-2026).
- [ ] Droog opruimen nagekeken.
- [ ] Alle URL's uit `data/legacy-urls.csv` getest: 200, 301 of 410 (`tools/controleer_live.py`, workflow "Site controleren"). Testsite 28-09-2026: alle 473 goed, 69 pagina's uit de sitemap 200. Na livegang herhalen op het hoofddomein.
- [ ] Securityheaders gecontroleerd. Testsite 28-09-2026: alle headers precies goed, caching goed, eigen 404, manifest niet op te vragen. Na livegang herhalen (ook www en http).
- [ ] Lighthouse gedraaid. Testsite 28-09-2026: performance 98 tot 100, toegankelijkheid 100, best practices 96 (logo te klein voor scherpe schermen, groter logo nodig), SEO 69 alleen door `noindex` op v2. Na livegang herhalen.
- [ ] Tijdelijke doorverwijzing naar brandweer.nl weg.
- [ ] P2000-publicatie omzetten van de testsite naar de echte site: in Home Assistant `ref` van `v2` naar `master`, omgeving `p2000` alleen nog `master` (besluit Sven 28-09-2026, zie `PLAN-P2000.md`).
- [ ] ~~`v2` uit de workflows halen~~ vervallen: `v2` blijft de testsite (besluit Sven 28-09-2026).
- [ ] Geen verwijzing naar het testadres in de gebouwde echte site (`tools/check.py` en `grep`).

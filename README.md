# Brandweer Uitgeest website

We betalen allemaal door middel van gemeentebelasting en andere bijdragen aan de brandweer van Nederland. Maar waarom mogen wij als burgers dan geen invloed hebben op de website? Dat vond ik nu ook. Daarom heb ik de website van brandweer Uitgeest hier op GitHub geplaatst. Iedereen mag en kan zijn eigen bijdrage leveren aan de website. Maar voordat het online komt bekijk ik het wel even en pas ik het zonodig aan. Dit is niet om censuur of iets dergelijks toe te passen maar om te zorgen dat het mag en past op de website van brandweer Uitgeest.

Wil je graag een pagina toevoegen? Of iets verbeteren?
Voel je vrij om dat te doen! Doe een pull-request, wij beoordelen hem en voegen hem toe aan de website.

## Issues

Voel je vrij om issues in te dienen. Weet je een verbetering voor de website en weet je niet goed hoe je dat zelf moet ontwikkelen? Open een issue.

## De site

Een snelle, statische website zonder cookies, trackers of externe verzoeken. Alles wordt gebouwd met een klein Python-script.

| map | inhoud |
|---|---|
| `content/` | pagina's, voertuigen en nieuwsarchief in Markdown |
| `data/uitrukken/` | alle uitrukken, één CSV-bestand per jaar |
| `data/site.yaml` | naam, adres, menu, social media en werving |
| `afbeeldingen/` | foto's; de build maakt er WebP- en AVIF-versies van |
| `templates/` | HTML-sjablonen (Jinja2) |
| `static/` | stylesheet, favicons en andere vaste bestanden |
| `build.py` | bouwt de site naar `public/` |
| `tools/check.py` | controles: geen externe resources, geen dode links, privacy, budgetten |

## Hoe draai/test je de site

Je hebt alleen Python 3.11 of nieuwer nodig. Dit werkt op Windows, macOS en Linux.

```
python -m venv .venv
.venv\Scripts\activate          (Windows)
source .venv/bin/activate       (macOS en Linux)
pip install -r requirements.txt
python build.py
python tools/check.py
python -m http.server -d public 8000
```

Surf daarna naar `http://localhost:8000`.

Zie [CONTRIBUTING.md](CONTRIBUTING.md) voor hoe je een bijdrage levert.

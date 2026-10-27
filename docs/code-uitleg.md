# De code begrijpen en uitleggen

## 1. Welke bestanden doen wat?

| Bestand | Wat het doet |
|---|---|
| `algorithm/portfolio.py` | Alle berekeningen: gewichten, rendement, volatiliteit, Sharpe ratio, optimale weging, leaderboard. Gewone Python, geen Flask. |
| `main.py` | Het algoritme testen in de terminal, met de testpersonen uit `test_data.json`. |
| `app.py` | Maakt de Flask-app, koppelt de database en de routes. |
| `models.py` | Eén Python-klasse per tabel uit `database/ddl.sql`. |
| `routes/main.py` | Startpagina: invoeren, berekenen, publiceren, leaderboard. |
| `routes/community.py` | Portefeuille bekijken, paywall (ontgrendelen) en commentaar. |
| `templates/` | De HTML-pagina's: `index.html` (start) en `portfolio.html` (één portefeuille). |
| `static/js/portfolio.js` | Rijen toevoegen/verwijderen en automatisch herberekenen tijdens het typen. |
| `seed_db.py` | Zet de testpersonen in de database. |
| `tests/` | Automatische controles van de berekeningen en de website. |

## 2. De weg van de gegevens

1. De browser opent `/`. Flask voert `home()` in `routes/main.py` uit.
2. `render_template("index.html", ...)` maakt de HTML-pagina. Jinja vult de
   waarden in tussen `{{ ... }}` en voert `{% for %}` en `{% if %}` uit.
3. De gebruiker drukt op een knop. Het formulier komt binnen als POST.
4. `read_rows()` leest de velden met `request.form.getlist(...)`.
   Elke aandelenrij heeft dezelfde veldnamen, dus `getlist("name")` geeft
   een lijst met alle namen.
5. `rows_to_stocks()` zet tekst om naar getallen. 10 (%) wordt 0.10.
6. `amounts_to_weights()` maakt van bedragen gewichten: 600 van 1000 euro is 0.60.
7. `calculate_portfolio()` en `optimal_weights()` rekenen.
8. Bij "Berekenen en publiceren" slaat `publish_portfolio()` alles op in de database.

## 3. Lijsten en dictionaries

Een aandeel is een dictionary, een portefeuille een lijst van dictionaries:

```python
stocks = [
    {"name": "A", "return": 0.10, "volatility": 0.20, "amount": 600, "weight": 0.60},
    {"name": "B", "return": 0.06, "volatility": 0.10, "amount": 400, "weight": 0.40},
]
```

`test_data.json` is een lijst van personen; elke persoon is een dictionary
met daarin weer een lijst `stocks`. Dat is een geneste structuur:
`users[0]["stocks"][1]["name"]` is de naam van het tweede aandeel van de eerste persoon.

## 4. De Sharpe ratio stap voor stap

Alle waarden zijn jaarlijks. Voor 600 euro in A (rendement 10%, volatiliteit 20%)
en 400 euro in B (rendement 6%, volatiliteit 10%), risk-free rate 2%:

```text
Gewichten     = 600/1000 = 0.60 en 400/1000 = 0.40
Rendement     = 0.60 * 0.10 + 0.40 * 0.06 = 0.084 = 8.40%
Variantie     = (0.60 * 0.20)² + (0.40 * 0.10)² = 0.016
Volatiliteit  = wortel(0.016) = 12.65%
Sharpe ratio  = (0.084 - 0.02) / 0.1265 = 0.5060
```

**Beperking die je moet kunnen uitleggen:** we veronderstellen dat de correlatie
tussen aandelen nul is. Daardoor vallen de covariantietermen weg uit de variantie.
Bij positief gecorreleerde aandelen onderschat dat het risico. De gebruiker geeft
zelf verwachte rendementen en volatiliteiten in; er worden geen koersen opgehaald.

## 5. De optimale weging

Bij nulcorrelaties is het gewicht met de hoogste Sharpe ratio evenredig met

```text
score = (rendement - risk-free rate) / volatiliteit²
```

Aandelen die niet meer opbrengen dan de risk-free rate krijgen score 0. Daarna
delen we elke score door de som van alle scores, zodat de gewichten samen 1 zijn.
Voor A: 0.08 / 0.04 = 2, voor B: 0.04 / 0.01 = 4. Optimaal is dus 2/6 = 33% A en
4/6 = 67% B, met Sharpe ratio 0.5657 in plaats van 0.5060.

## 6. Invoer controleren

`check_number()` weigert alles wat geen gewoon getal is: tekst, `True`/`False`,
oneindig en `nan`. Verder worden geweigerd: een negatief bedrag of een
negatieve volatiliteit, een totaal bedrag van 0, een lege naam, en een
portefeuille zonder risico (want dan deel je door 0).

Een fout maken we met `raise ValueError("...")`. De route vangt die op met
`try` / `except ValueError` en toont de tekst bovenaan de pagina. De browser
controleert ook al, maar dat kan je omzeilen; daarom controleert Python opnieuw.

## 7. De database

`database/ddl.sql` maakt de tabellen; `models.py` heeft per tabel een klasse met
dezelfde kolommen. Zo werk je met de database via Python in plaats van SQL:

| Python | Betekent in SQL ongeveer |
|---|---|
| `db.session.add(User(username="Jan", ...))` | `INSERT INTO User ...` |
| `db.session.commit()` | Bewaar alles definitief |
| `User.query.filter_by(username="Jan").first()` | `SELECT * FROM User WHERE username = 'Jan' LIMIT 1` |
| `db.session.get(User, 3)` | `SELECT * FROM User WHERE user_id = 3` |

Bij publiceren (`publish_portfolio`) worden deze rijen gemaakt:

| Tabel | Wat erin komt |
|---|---|
| `User` | De gebruikersnaam (er is geen login: e-mail en wachtwoord krijgen een vaste invulwaarde) |
| `Portfolio` | Eén portefeuille van die gebruiker |
| `Asset` | Elk aandeel, als het nog niet bestond |
| `PortfolioHolding` | Per aandeel: bedrag, rendement, volatiliteit, jouw gewicht en het optimale gewicht |
| `PortfolioAnalysis` | Het resultaat: rendement, volatiliteit, Sharpe ratio (gewoon en optimaal) |
| `OptimizedHolding` | Het optimale gewicht per aandeel bij die analyse |
| `LeaderboardEntry` | De plaats op het leaderboard |

`db.session.flush()` stuurt een nieuwe rij al naar de database zodat we haar
nummer (bv. `user.user_id`) kennen voor de volgende tabel. Pas bij `commit()`
wordt alles samen definitief opgeslagen.

Bij ontgrendelen komt er een rij in `PortfolioUnlock` (wie, welke portefeuille,
5 euro). Bij commentaar een rij in `Comment`. De tabel `Subscription` wordt nog
niet gebruikt.

## 8. Flask-begrippen

| Begrip | Betekenis |
|---|---|
| `@bp.route("/")` | Deze functie hoort bij dit adres |
| `Blueprint` | Een groep routes; elk bestand in `routes/` is er één |
| `request.form.get(...)` | Eén ingevuld veld |
| `request.form.getlist(...)` | Alle waarden van een veld dat meerdere keren voorkomt |
| `session` | Onthoudt per browser wie je bent (na publiceren). Geen echte login |
| `flash(...)` | Een melding die op de volgende pagina bovenaan verschijnt |
| `redirect(url_for(...))` | Stuur de browser door naar een andere pagina |
| `render_template(...)` | Combineer een HTML-bestand met Python-gegevens |

## 9. Bewuste beperkingen

- Nulcorrelaties tussen aandelen.
- Geen login: wie publiceert, wordt in die browser onthouden.
- De betaling van 5 euro is een simulatie.
- Rendement en volatiliteit zijn verwachtingen van de gebruiker zelf.

## 10. Testen

```text
python main.py                              het algoritme in de terminal
python -m unittest discover -s tests -v     alle automatische tests
```

De websitetests gebruiken een tijdelijke database in het geheugen (SQLite),
zodat ze ook zonder verbinding met de groepsdatabase werken.

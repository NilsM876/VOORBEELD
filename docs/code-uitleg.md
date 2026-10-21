# De code begrijpen en verdedigen

## 1. Welke weg leggen de gegevens af?

1. `app.py` maakt de Flask-app en registreert de routes.
2. De browser vraagt `/` op. Flask voert `home()` in `routes/main.py` uit.
3. `templates/index.html` toont het formulier. HTML beschrijft de pagina;
   Jinja vult waarden in tussen `{{ ... }}` en verwerkt `{% ... %}`.
4. Bij verzenden komen de velden binnen via `request.form`.
5. De route zet tekst en percentages om naar getallen en fracties.
6. `algorithm/portfolio.py` controleert de invoer en berekent de resultaten.
7. `render_template()` geeft het resultaat aan de HTML-pagina.

GET vraagt een pagina op. POST verstuurt formuliergegevens. Het veld `action`
geeft aan welke knop werd gebruikt: berekenen, publiceren, ontgrendelen of reageren.
De Python-berekeningen werken ook zonder Flask, via `main.py` in de terminal.

## 2. Waarom lijsten, dictionaries en tuples?

Een aandeel is een dictionary met benoemde gegevens:

```python
stock = {"name": "A", "return": 0.10, "volatility": 0.20, "weight": 0.60}
```

Een portefeuille bevat een lijst van zulke dictionaries. Een lijst laat toe
meerdere aandelen in volgorde te doorlopen met een `for`-lus.

In de community gebruiken we drie dictionaries:

| Variabele | Sleutel | Waarde |
|---|---|---|
| `self._users` | Gebruikersnaam | Dictionary met naam, aandelen en risicovrije rente |
| `self._unlocks` | Tuple `(bezoeker, eigenaar)` | `True` als toegang verleend is |
| `self._comments` | Eigenaar | Lijst van reacties, elk een dictionary |

Een tuple kan als dictionarysleutel dienen omdat hij niet wijzigbaar is.
`("persoon A", "persoon B")` en `("persoon B", "persoon A")` zijn verschillende sleutels:
toegang is persoonlijk en werkt maar in één richting.

## 3. Waarom staat er toch een class?

`PortfolioCommunity` is een bundel van bij elkaar horende gegevens en functies.
Bij `community = PortfolioCommunity(users)` wordt `__init__` uitgevoerd.
Die functie maakt de drie dictionaries en voegt de voorbeeldgebruikers toe.

`self` betekent telkens 'dit community-object'. Bij
`community.add_user(...)` geeft Python dit object automatisch mee als `self`.
Een naam met `_` betekent volgens Python-gebruik: bedoeld voor intern gebruik.
Dat is een afspraak, geen beveiliging.

De class blijft behouden omdat de terminal, Flask en de bestaande tests deze
gemeenschappelijke interface gebruiken. De inhoud werkt met gewone dictionaries
en lussen. Er zijn geen overerving of ingewikkelde objectstructuren nodig.

## 4. De Sharpe-ratio stap voor stap

Alle getallen zijn jaarlijkse waarden. De Python-functies verwachten fracties:
10% wordt `0.10`. De website en terminal delen de invoer daarom door 100.

Voor elk aandeel berekenen we `weight * return`. De som is het verwachte
portefeuillerendement. Voor de variantie tellen we `(weight * volatility) ** 2`
op. De vierkantswortel van de variantie is de portefeuillevolatiliteit.

Daarna geldt:

```text
Sharpe = (verwacht portefeuillerendement - risicovrije rente) / volatiliteit
```

Voor 60% in A met rendement 10% en volatiliteit 20%, en 40% in B met rendement
6% en volatiliteit 10%, bij een risicovrije rente van 2%:

```text
Rendement = 0.60 * 0.10 + 0.40 * 0.06 = 0.084 = 8.40%
Variantie = (0.60 * 0.20)^2 + (0.40 * 0.10)^2 = 0.016
Volatiliteit = wortel(0.016) = ongeveer 12.65%
Sharpe = (0.084 - 0.02) / wortel(0.016) = ongeveer 0.5060
```

**Te verdedigen beperking:** we veronderstellen nulcorrelaties tussen aandelen.
Daarom ontbreken de covariantietermen. Dit is een vereenvoudigd model;
bij positieve correlaties kan het risico worden onderschat. De formule bewijst
ook geen werkelijk behaald rendement: de gebruiker voert verwachtingen in.
Er gebeurt geen automatische annualisering of ophalen van beurskoersen.

## 5. Waarom invoer controleren?

Negatieve gewichten worden geweigerd omdat dit model geen shortposities bevat.
Volatiliteit mag niet negatief zijn. Gewichten moeten samen 1 vormen.
De tolerantie `1e-8` betekent `0.00000001`: zo vermijden we dat normale
afrondingsverschillen van kommagetallen als fout worden gezien.

`fsum()` uit de standaardbibliotheek telt kommagetallen nauwkeurig op.
`finite_number()` weigert ook oneindig en NaN ('geen getal'). Nulvolatiliteit
wordt geweigerd omdat delen door nul geen geldige Sharpe-ratio oplevert.
Negatieve rendementen en negatieve Sharpe-ratio's zijn wel toegestaan.

`raise ValueError(...)` stopt een functie bij ongeldige invoer.
`raise PermissionError(...)` stopt bij ontbrekende toegang. De route vangt
deze fouten op met `try/except` en toont een melding. Controle in Python blijft
nodig: controles in de browser kunnen worden omzeild.

## 6. Leaderboard, paywall en reacties

Het leaderboard berekent per gebruiker de Sharpe-ratio. `sorted()` sorteert
de lijst. `key=sharpe_score` vertelt welk veld gebruikt wordt; `reverse=True`
zet de hoogste score bovenaan. Gelijke scores behouden hun oorspronkelijke
volgorde. Alleen naam en score worden teruggegeven, geen aandelen.

Voor ontgrendelen controleren we eerst of beide gebruikers bestaan. Eigen
portefeuilles en eerder ontgrendelde portefeuilles zijn gratis toegankelijk.
Anders moet het gesimuleerde bedrag exact 5 zijn. Daarna slaan we het paar
op in de toegangs-dictionary. Dit is geen echte betaling: de webroute geeft
zelf 5 door. Voor een echte paywall is bevestiging door een betaalprovider nodig.

Een reactie bevat een auteur en een bericht. Alleen wie de portefeuille
ontgrendeld heeft, mag reageren. `strip()` verwijdert spaties aan het begin
en einde; een lege reactie wordt geweigerd. De eigenaar mag de eigen portefeuille
en reacties lezen, maar kan in de huidige versie niet zelf reageren.

`deepcopy()` maakt een volledige kopie, ook van dictionaries binnen lijsten.
Zonder die kopie zou iemand een teruggegeven portefeuille kunnen wijzigen
en daarmee ongemerkt de gegevens binnen de community aanpassen.

## 7. Wat doet Flask dat je nog niet uit basis-Python kent?

| Begrip | Betekenis in dit project |
|---|---|
| `@bp.route(...)` | Registreert welke functie hoort bij een webadres |
| `Blueprint` | Groepeert routes zodat `app.py` overzichtelijk blijft |
| `request.form.get(...)` | Haalt één ingevuld formulierveld op |
| `request.form.getlist(...)` | Haalt alle waarden van een herhaald veld op |
| `session` | Onthoudt de actieve gebruikersnaam voor de browser |
| `current_app.extensions` | Bewaart de community bij de huidige Flask-app |
| `render_template(...)` | Combineert HTML met Python-resultaten |

De sessie is geen volwaardig account: er is geen wachtwoord of echte login.
De community zit alleen in het servergeheugen en verdwijnt bij een herstart.
De databasebestanden bevatten nog geen uitgewerkt gegevensmodel.

## 8. JavaScript en de andere bestanden

`static/js/portfolio.js` voegt aandelenrijen toe, verwijdert rijen en telt
gewichten op. Bij geldige invoer wacht het script 350 milliseconden voordat het
de berekening aanvraagt. Zo volgt niet bij elke toetsaanslag onmiddellijk een
verzoek. `fetch()` verstuurt het formulier zonder de hele pagina te verversen.
`async/await` wacht op het antwoord; `AbortController` annuleert een vorige
aanvraag zodat een oud antwoord een nieuw resultaat niet overschrijft.
Alle inhoudelijke berekeningen blijven in Python.

`config.py` leest instellingen uit omgevingsvariabelen en `.env`.
`models.py` bereidt SQLAlchemy voor, maar bevat nog geen eigen databasetabellen.
De bestaande tests controleren voorbeelden van berekeningen, invoerfouten,
toegangsregels en formulieracties. Tests zijn controlecode, geen gebruikersflow.

## 9. Zo kun je de aanpak verantwoorden

"Ik houd de berekeningen apart van Flask, zodat ik ze ook in de terminal
kan gebruiken en afzonderlijk kan testen. Een aandeel is een dictionary en
een portefeuille een lijst van aandelen. Ik gebruik expliciete lussen om elke
berekeningsstap te kunnen volgen. Toegang registreer ik per bezoeker en eigenaar.
De huidige website is een demonstratie: nulcorrelaties, zelf ingevoerde cijfers,
betalingssimulatie en tijdelijke opslag zijn bewuste beperkingen die ik benoem."

Controleer de bestaande tests met `python -B -m unittest discover -v` zodra
Python en de dependencies uit `requirements.txt` beschikbaar zijn.

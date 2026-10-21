# Sharpe-ratio in gewone Python

De volledige kernlogica staat in deze map:

- `portfolio.py`: invoervalidatie, rendement, volatiliteit, Sharpe ratio en leaderboard.
- `community.py`: gebruikers, gesimuleerde paywall, toegang en commentaren.
- `__init__.py`: importeert de publieke API; bestaande imports blijven werken.

Deze modules gebruiken alleen de standaardbibliotheek, zonder Flask.
`main.py` verzorgt interactieve terminalinvoer.

Start vanuit de projectmap, zonder extra bibliotheken:

```text
python main.py
python main.py --community
python -m unittest discover -s tests -v
```

Met `python main.py` voer je een gebruikersnaam, het aantal aandelen,
de gegevens per aandeel en de risk-free rate in. Daarna verschijnen de
resultaten en het leaderboard, met fictieve vergelijkingsgegevens uit
`test_data.json`. Met `--community` kun je na de berekening optioneel een
andere portefeuille ontgrendelen en commentaar plaatsen.
De terminal gebruikt percentages: 10 betekent 10%. De Python-API en het
JSON-bestand gebruiken fracties: 0.10 betekent 10%.
Rendement, standaarddeviatie en risk-free rate zijn jaarlijks.

## Berekening

Voor gewichten w, rendementen r en standaarddeviaties s:

- Verwacht rendement = som(w * r).
- Volatiliteit = wortel(som((w * s) ** 2)).
- Sharpe ratio = (verwacht rendement - risk-free rate) / volatiliteit.

Alle correlaties tussen aandelen worden voorlopig als nul verondersteld.
Dit kan de volatiliteit en Sharpe ratio vertekenen tegenover een echte
portefeuille. Er wordt niet automatisch geannualiseerd.
Gewichten moeten niet-negatief zijn en samen 1 vormen (tolerantie 1e-8).
Negatieve standaarddeviaties, niet-eindige getallen en lege namen worden
geweigerd. Bij nul volatiliteit is de Sharpe ratio ongedefinieerd en volgt
een ValueError. Negatieve rendementen en Sharpe ratio's zijn toegestaan.

## Community-API

`PortfolioCommunity` biedt:

- `add_user(username, stocks, risk_free_rate)`: valideert en registreert.
- `leaderboard()`: alleen gebruikersnamen en Sharpe ratio's, aflopend.
  Bij gelijke scores blijft de registratievolgorde behouden.
- `unlock_portfolio(viewer, owner, payment_eur)`: exact 5 euro simuleren.
  Toegang geldt alleen voor dit paar gebruikers. Herhaalde toegang is gratis.
- `get_portfolio(viewer, owner)`: volledige portefeuille inclusief risk-free rate.
  Eigen portefeuilles zijn direct toegankelijk.
- `add_comment(author, owner, message)`: vereist een eerdere ontgrendeling
  door deze auteur van deze portefeuille. Lege commentaren worden geweigerd.
- `get_comments(viewer, owner)`: vereist toegang tot de portefeuille.

`calculate_portfolio(stocks, risk_free_rate)` en `leaderboard(users)` zijn ook
los beschikbaar. Een aandeel heeft `name`, `return`, `volatility` en `weight`.

Alles blijft in het geheugen en verdwijnt bij afsluiten. Er zijn geen echte
betalingen, authenticatie of database. Een latere website moet de identiteit
van de gebruiker vaststellen en betalingen verifiëren voor ze toegang verleent.

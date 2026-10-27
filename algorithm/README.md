# algorithm/

De berekeningen van Sharply, in gewone Python zonder Flask. Alles staat in
`portfolio.py`:

- `amounts_to_weights(stocks)`: bedragen in euro omzetten naar gewichten.
- `calculate_portfolio(stocks, risk_free_rate)`: rendement, volatiliteit en Sharpe ratio.
- `optimal_weights(stocks, risk_free_rate)`: de weging met de hoogste Sharpe ratio.
- `leaderboard(users)`: gebruikers gerangschikt van hoogste naar laagste Sharpe ratio.

Een aandeel is een dictionary met `name`, `return`, `volatility` en `amount`
(of `weight`). Percentages zijn fracties: 0.10 betekent 10%. Alles is jaarlijks.

## Berekening

Voor gewichten w, rendementen r en standaarddeviaties s:

- Verwacht rendement = som(w * r)
- Volatiliteit = wortel(som((w * s)²))
- Sharpe ratio = (verwacht rendement - risk-free rate) / volatiliteit

Alle correlaties tussen aandelen worden als nul verondersteld. Daardoor kan de
volatiliteit afwijken van die van een echte portefeuille.

## Testen op de testdata

```text
python main.py
python -m unittest discover -s tests -v
```

`main.py` vraagt een portefeuille en vergelijkt ze met de fictieve personen uit
`test_data.json`. De terminal gebruikt percentages: 10 betekent 10%.

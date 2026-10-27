"""De berekeningen van Sharply, in gewone Python zonder Flask.

Een aandeel is een dictionary, een portefeuille een lijst van aandelen:

    {"name": "A", "return": 0.10, "volatility": 0.20, "weight": 0.60}

Alle percentages zijn fracties: 0.10 betekent 10%.
"""

from math import isfinite, sqrt


CORRELATION_LIMITATION = (
    "Alle correlaties tussen aandelen worden als nul verondersteld. "
    "De berekende volatiliteit en Sharpe ratio kunnen daardoor afwijken "
    "van die van een echte portefeuille."
)


def check_number(value, label):
    """Geef een fout als value geen gewoon, eindig getal is."""
    # True en False tellen in Python als 1 en 0; die weigeren we.
    # isfinite weigert "oneindig" en "nan" (not a number).
    if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(value):
        raise ValueError(f"{label} moet een geldig getal zijn")


def amounts_to_weights(stocks):
    """Voeg aan elk aandeel een gewicht toe: zijn bedrag gedeeld door het totaal."""
    total_amount = 0
    for stock in stocks:
        check_number(stock["amount"], "Het bedrag")
        if stock["amount"] < 0:
            raise ValueError("Een bedrag mag niet negatief zijn")
        total_amount += stock["amount"]

    if total_amount <= 0:
        raise ValueError("Het totale bedrag moet groter dan 0 zijn")

    for stock in stocks:
        # Voorbeeld: 600 euro van 1000 euro geeft gewicht 0.60.
        stock["weight"] = stock["amount"] / total_amount
    return total_amount


def calculate_portfolio(stocks, risk_free_rate):
    """Bereken rendement, volatiliteit en Sharpe ratio van een portefeuille."""
    check_number(risk_free_rate, "De risk-free rate")
    if len(stocks) == 0:
        raise ValueError("Voeg minstens één aandeel toe")

    for stock in stocks:
        if not isinstance(stock.get("name"), str) or stock["name"].strip() == "":
            raise ValueError("Elk aandeel heeft een naam nodig")
        check_number(stock.get("return"), "Het rendement")
        check_number(stock.get("volatility"), "De volatiliteit")
        check_number(stock.get("weight"), "Het gewicht")
        if stock["weight"] < 0 or stock["volatility"] < 0:
            raise ValueError("Gewicht en volatiliteit mogen niet negatief zijn")

    total_weight = 0
    for stock in stocks:
        total_weight += stock["weight"]
    # Kommagetallen geven kleine afrondingsfouten, daarom een kleine marge.
    if abs(total_weight - 1) > 0.00000001:
        raise ValueError("De gewichten moeten samen 100% zijn")

    expected_return = 0
    variance = 0
    for stock in stocks:
        expected_return += stock["weight"] * stock["return"]
        # Bij nulcorrelaties tellen we alleen (gewicht * volatiliteit)² op.
        variance += (stock["weight"] * stock["volatility"]) ** 2
    volatility = sqrt(variance)

    if volatility == 0:
        raise ValueError("De volatiliteit van de portefeuille moet groter dan 0 zijn")

    sharpe = (expected_return - risk_free_rate) / volatility
    return {"return": expected_return, "volatility": volatility, "sharpe": sharpe}


def optimal_weights(stocks, risk_free_rate):
    """Zoek de gewichten met de hoogste Sharpe ratio bij nulcorrelaties.

    Elk gewicht is evenredig met (rendement - risk-free rate) / volatiliteit².
    Aandelen die niet meer opbrengen dan de risk-free rate krijgen gewicht 0.
    """
    # Stap 1: geef elk aandeel een score.
    scores = []
    for stock in stocks:
        extra_return = stock["return"] - risk_free_rate
        if extra_return <= 0:
            scores.append(0)
        elif stock["volatility"] == 0:
            # Meer rendement zonder risico zou een oneindige Sharpe ratio geven.
            raise ValueError("elk aandeel heeft een volatiliteit boven 0 nodig")
        else:
            scores.append(extra_return / stock["volatility"] ** 2)

    total_score = sum(scores)
    if total_score == 0:
        raise ValueError("geen enkel aandeel brengt meer op dan de risk-free rate")

    # Stap 2: deel elke score door het totaal, zodat de gewichten samen 1 zijn.
    optimal_stocks = []
    for index in range(len(stocks)):
        optimal_stocks.append({
            "name": stocks[index]["name"],
            "return": stocks[index]["return"],
            "volatility": stocks[index]["volatility"],
            "weight": scores[index] / total_score,
        })

    # Stap 3: bereken rendement, volatiliteit en Sharpe ratio van die weging.
    result = calculate_portfolio(optimal_stocks, risk_free_rate)
    result["stocks"] = optimal_stocks
    return result


def sharpe_of(entry):
    """Geef sorted() het getal waarop het moet sorteren."""
    return entry["sharpe"]


def leaderboard(users):
    """Rangschik gebruikers van hoogste naar laagste Sharpe ratio."""
    ranking = []
    for user in users:
        result = calculate_portfolio(user["stocks"], user["risk_free_rate"])
        ranking.append({"username": user["username"], "sharpe": result["sharpe"]})
    return sorted(ranking, key=sharpe_of, reverse=True)

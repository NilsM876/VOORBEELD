from math import fsum, isfinite, sqrt


CORRELATION_LIMITATION = (
    "Alle correlaties tussen aandelen worden als nul verondersteld. "
    "De berekende volatiliteit en Sharpe ratio kunnen daardoor afwijken "
    "van die van een echte portefeuille."
)


def finite_number(value, label):
    """Weiger invoer die geen bruikbaar getal is."""
    # Python behandelt True en False als getallen; hier aanvaarden we die niet.
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be a finite number")
    try:
        valid = isfinite(value)
    except OverflowError:
        valid = False
    if not valid:
        raise ValueError(f"{label} must be a finite number")
    return value


def calculate_portfolio(stocks, risk_free_rate):
    """Bereken rendement, risico en Sharpe bij veronderstelde nulcorrelaties."""

    if not stocks:
        raise ValueError("Portfolio cannot be empty")

    finite_number(risk_free_rate, "Risk-free rate")
    for stock in stocks:
        if not isinstance(stock.get("name"), str) or not stock["name"].strip():
            raise ValueError("Stock name cannot be empty")
        for key in ("return", "volatility", "weight"):
            finite_number(stock.get(key), key)
        if stock["weight"] < 0 or stock["volatility"] < 0:
            raise ValueError("Weight and volatility must be nonnegative")

    weights = []
    for stock in stocks:
        weights.append(stock["weight"])
    # fsum telt kommagetallen nauwkeurig op.
    total_weight = fsum(weights)

    # De tolerantie vangt kleine afrondingsfouten op.
    if abs(total_weight - 1.0) > 1e-8:
        raise ValueError("Portfolio weights must sum to 1")

    return_contributions = []
    portfolio_variance = 0
    for stock in stocks:
        weight = stock["weight"]
        stock_return = stock["return"]
        stock_volatility = stock["volatility"]
        return_contributions.append(weight * stock_return)
        # Bij nulcorrelaties vallen de covariantietermen weg.
        portfolio_variance += (weight * stock_volatility) ** 2

    expected_return = fsum(return_contributions)
    portfolio_volatility = sqrt(portfolio_variance)

    if portfolio_volatility == 0:
        raise ValueError("Portfolio volatility must be positive")

    sharpe_ratio = (
        expected_return - risk_free_rate
    ) / portfolio_volatility

    finite_number(sharpe_ratio, "Sharpe ratio")

    return {
        "return": expected_return,
        "volatility": portfolio_volatility,
        "sharpe": sharpe_ratio
    }


def optimal_weights(stocks, risk_free_rate):
    """Zoek de gewichten met de hoogste Sharpe ratio bij nulcorrelaties.

    Elk gewicht is evenredig met (rendement - risk-free rate) / volatiliteit².
    Aandelen die niet meer opbrengen dan de risk-free rate krijgen gewicht 0.
    """

    # Stap 1: geef elk aandeel een score.
    scores = []
    for stock in stocks:
        extra_return = stock["return"] - risk_free_rate
        variance = stock["volatility"] ** 2
        if extra_return <= 0:
            scores.append(0)
        elif variance == 0:
            # Geen risico en toch meer rendement geeft een oneindige Sharpe ratio.
            raise ValueError("Every stock needs a volatility above 0 to calculate optimal weights")
        else:
            scores.append(extra_return / variance)

    total_score = sum(scores)
    if total_score == 0:
        raise ValueError("No stock returns more than the risk-free rate, so there are no optimal weights")

    # Stap 2: deel elke score door het totaal, zodat de gewichten samen 1 zijn.
    optimal_stocks = []
    for index in range(len(stocks)):
        stock = stocks[index]
        optimal_stocks.append({
            "name": stock["name"],
            "return": stock["return"],
            "volatility": stock["volatility"],
            "weight": scores[index] / total_score,
        })

    # Stap 3: bereken rendement, volatiliteit en Sharpe ratio van de optimale weging.
    result = calculate_portfolio(optimal_stocks, risk_free_rate)
    result["stocks"] = optimal_stocks
    return result


def sharpe_score(entry):
    """Geef sorted het veld waarmee het moet sorteren."""
    return entry["sharpe"]


def leaderboard(users):
    """Rank users from highest to lowest Sharpe ratio."""

    ranking = []

    for user in users:
        result = calculate_portfolio(
            user["stocks"],
            user["risk_free_rate"]
        )

        ranking.append({
            "username": user["username"],
            "sharpe": result["sharpe"]
        })

    return sorted(
        ranking,
        key=sharpe_score,
        reverse=True
    )

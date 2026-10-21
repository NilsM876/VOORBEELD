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

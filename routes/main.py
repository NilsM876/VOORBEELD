"""De startpagina: portefeuille invoeren, berekenen, publiceren en het leaderboard."""

from datetime import datetime

from flask import Blueprint, flash, render_template, request, session

from algorithm import (
    CORRELATION_LIMITATION, amounts_to_weights, calculate_portfolio, optimal_weights, sharpe_of,
)
from models import (
    Asset, LeaderboardEntry, OptimizedHolding, Portfolio, PortfolioAnalysis, PortfolioHolding, User, db,
)

bp = Blueprint("main", __name__)


def to_number(text, label):
    """Zet tekst uit het formulier om naar een getal. 10,5 en 10.5 mogen allebei."""
    try:
        return float(text.replace(",", "."))
    except ValueError:
        raise ValueError(f"{label} moet een getal zijn")


def read_rows():
    """Lees de aandelen uit het formulier, als tekst zoals de gebruiker ze typte.

    Elke aandelenrij gebruikt dezelfde veldnamen. getlist("name") geeft daarom
    een lijst met alle namen, getlist("return") alle rendementen, enzovoort.
    """
    names = request.form.getlist("name")
    returns = request.form.getlist("return")
    volatilities = request.form.getlist("volatility")
    amounts = request.form.getlist("amount")
    if not len(names) == len(returns) == len(volatilities) == len(amounts):
        raise ValueError("Er ontbreken velden in het formulier")

    rows = []
    for index in range(len(names)):
        rows.append({
            "name": names[index],
            "return": returns[index],
            "volatility": volatilities[index],
            "amount": amounts[index],
        })
    return rows


def rows_to_stocks(rows):
    """Zet de tekst om naar getallen. De gebruiker typt 10 voor 10%, wij rekenen met 0.10."""
    stocks = []
    for row in rows:
        stocks.append({
            "name": row["name"].strip(),
            "return": to_number(row["return"], "Het rendement") / 100,
            "volatility": to_number(row["volatility"], "De volatiliteit") / 100,
            "amount": to_number(row["amount"], "Het bedrag"),
        })
    return stocks


def find_or_create_asset(ticker):
    """Zoek het aandeel in de tabel Asset; bestaat het nog niet, maak het dan aan."""
    asset = Asset.query.filter_by(ticker=ticker).first()
    if asset is None:
        asset = Asset(ticker=ticker)
        db.session.add(asset)
        # flush stuurt de nieuwe rij al naar de database, zodat asset.asset_id gekend is.
        db.session.flush()
    return asset


def publish_portfolio(username, stocks, risk_free_rate):
    """Sla gebruiker, portefeuille en berekening op en zet ze op het leaderboard.

    stocks moet al gewichten hebben (zie amounts_to_weights).
    Geeft de nieuwe gebruiker terug.
    """
    username = username.strip()
    if username == "":
        raise ValueError("Vul een gebruikersnaam in om te publiceren")
    if len(username) > 100:
        raise ValueError("De gebruikersnaam mag hoogstens 100 tekens hebben")
    if User.query.filter_by(username=username).first() is not None:
        raise ValueError("Deze gebruikersnaam bestaat al, kies een andere")

    # Elk aandeel mag maar één keer in een portefeuille staan (zo staat het in de DDL).
    names = []
    for stock in stocks:
        if len(stock["name"]) > 30:
            raise ValueError("Een naam of ticker mag hoogstens 30 tekens hebben")
        if stock["name"].lower() in names:
            raise ValueError(f"{stock['name']} staat twee keer in je portefeuille")
        names.append(stock["name"].lower())

    result = calculate_portfolio(stocks, risk_free_rate)
    try:
        optimal = optimal_weights(stocks, risk_free_rate)
    except ValueError:
        optimal = None
    now = datetime.now()

    # Er is geen login, maar email en password_hash zijn verplichte kolommen.
    user = User(username=username, email=f"{username}@sharply.local",
                password_hash="geen login", created_at=now)
    db.session.add(user)
    db.session.flush()

    portfolio = Portfolio(user_id=user.user_id, portfolio_name=f"Portefeuille van {username}",
                          is_public=True, created_at=now)
    db.session.add(portfolio)
    db.session.flush()

    analysis = PortfolioAnalysis(
        portfolio_id=portfolio.portfolio_id,
        risk_free_rate=risk_free_rate,
        annual_return=result["return"],
        annual_volatility=result["volatility"],
        sharpe_ratio=result["sharpe"],
        optimization_method="Hoogste Sharpe ratio bij nulcorrelaties",
        calculation_version="1",
        calculated_at=now,
    )
    if optimal is not None:
        analysis.optimized_return = optimal["return"]
        analysis.optimized_volatility = optimal["volatility"]
        analysis.optimized_sharpe = optimal["sharpe"]
    db.session.add(analysis)
    db.session.flush()

    # Eén rij per aandeel in PortfolioHolding, en de optimale weging in OptimizedHolding.
    for index in range(len(stocks)):
        stock = stocks[index]
        asset = find_or_create_asset(stock["name"])
        holding = PortfolioHolding(
            portfolio_id=portfolio.portfolio_id,
            asset_id=asset.asset_id,
            amount=stock["amount"],
            expected_return=stock["return"],
            volatility=stock["volatility"],
            input_weight=stock["weight"],
        )
        if optimal is not None:
            optimal_weight = optimal["stocks"][index]["weight"]
            holding.optimized_weight = optimal_weight
            db.session.add(OptimizedHolding(analysis_id=analysis.analysis_id,
                                            asset_id=asset.asset_id, weight=optimal_weight))
        db.session.add(holding)

    db.session.add(LeaderboardEntry(analysis_id=analysis.analysis_id, user_id=user.user_id,
                                    published_at=now, is_visible=True))
    # Pas bij commit wordt alles echt opgeslagen, allemaal samen.
    db.session.commit()
    return user


def get_leaderboard():
    """Alle gepubliceerde portefeuilles, de hoogste Sharpe ratio eerst."""
    ranking = []
    for entry in LeaderboardEntry.query.filter_by(is_visible=True).all():
        analysis = db.session.get(PortfolioAnalysis, entry.analysis_id)
        user = db.session.get(User, entry.user_id)
        ranking.append({
            "username": user.username,
            # De database geeft een Decimal terug; float maakt er een gewoon getal van.
            "sharpe": float(analysis.sharpe_ratio),
            "portfolio_id": analysis.portfolio_id,
        })
    return sorted(ranking, key=sharpe_of, reverse=True)


# GET: de pagina openen. POST: op een knop van het formulier drukken.
@bp.route("/", methods=["GET", "POST"])
def home():
    rows = [{"name": "", "return": "", "volatility": "", "amount": ""}]
    rate = request.form.get("risk_free_rate", "2")
    username = request.form.get("username", "")
    stocks = []
    total_amount = 0
    result = None
    optimal = None
    optimal_error = None
    error = None
    status = 200

    if request.method == "POST":
        try:
            rows = read_rows()
            stocks = rows_to_stocks(rows)
            total_amount = amounts_to_weights(stocks)
            risk_free_rate = to_number(rate, "De risk-free rate") / 100
            result = calculate_portfolio(stocks, risk_free_rate)
            # Lukt de optimale weging niet, dan tonen we toch het gewone resultaat.
            try:
                optimal = optimal_weights(stocks, risk_free_rate)
            except ValueError as exc:
                optimal_error = str(exc)

            # De knop "Berekenen en publiceren" stuurt action=publish mee.
            if request.form.get("action") == "publish":
                user = publish_portfolio(username, stocks, risk_free_rate)
                # De sessie onthoudt in deze browser wie je bent. Dit is geen login.
                session["user_id"] = user.user_id
                session["username"] = user.username
                flash(f"Je portefeuille staat op het leaderboard als {user.username}.")
        except ValueError as exc:
            error = str(exc)
            # 400 betekent: de invoer van de gebruiker klopt niet.
            status = 400

    return render_template(
        "index.html", rows=rows, rate=rate, username=username, stocks=stocks,
        total_amount=total_amount, result=result, optimal=optimal, optimal_error=optimal_error,
        error=error, limitation=CORRELATION_LIMITATION, ranking=get_leaderboard(),
        viewer=session.get("username"),
    ), status

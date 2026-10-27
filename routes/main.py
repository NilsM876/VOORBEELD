"""Portfolio form and simulated community, using the existing algorithm API."""
import json
from pathlib import Path

from flask import Blueprint, current_app, render_template, request, session

from algorithm import CORRELATION_LIMITATION, PortfolioCommunity, calculate_portfolio, optimal_weights

# Een Blueprint groepeert routes. app.py koppelt deze groep aan Flask.
bp = Blueprint("main", __name__)


def get_community():
    # Bewaar één community per Flask-app, niet een nieuwe per webrequest.
    if "portfolio_community" not in current_app.extensions:
        project_folder = Path(__file__).resolve().parent.parent
        data_file = project_folder / "test_data.json"
        text = data_file.read_text(encoding="utf-8")
        users = json.loads(text)
        current_app.extensions["portfolio_community"] = PortfolioCommunity(users)
    return current_app.extensions["portfolio_community"]


@bp.route("/", methods=["GET", "POST"])
def home():
    community = get_community()
    result = None
    optimal = None
    optimal_error = None
    stocks = []
    total_amount = 0
    error = None
    opened = None
    comments = []
    owner = request.form.get("owner", "")
    rows = [{"name": "", "return": "", "volatility": "", "amount": ""}]
    rate = request.form.get("risk_free_rate", "2")
    username = request.form.get("username", "")
    # De sessie onthoudt de actieve naam voor deze browser. Dit is geen login.
    viewer = session.get("portfolio_viewer")
    status = 200
    if request.method == "POST":
        try:
            action = request.form.get("action", "calculate")
            if action in ("calculate", "publish"):
                # HTML herhaalt dezelfde veldnamen voor elke aandelenrij.
                # getlist haalt alle waarden van één veldnaam in rijvolgorde op.
                field_names = ("name", "return", "volatility", "amount")
                fields = {}
                for field_name in field_names:
                    fields[field_name] = request.form.getlist(field_name)

                number_of_stocks = len(fields["name"])
                for field_name in field_names:
                    if len(fields[field_name]) != number_of_stocks:
                        raise ValueError("De aandelenvelden zijn onvolledig.")

                rows = []
                for index in range(number_of_stocks):
                    row = {}
                    for field_name in field_names:
                        row[field_name] = fields[field_name][index]
                    rows.append(row)

                # rows bewaart tekst voor het formulier; stocks bevat getallen.
                # De gebruiker voert 10 in voor 10%; de berekening gebruikt 0.10.
                stocks = []
                amounts = []
                for row in rows:
                    stock = {"name": row["name"].strip()}
                    for field_name in ("return", "volatility"):
                        text = row[field_name].replace(",", ".")
                        stock[field_name] = float(text) / 100
                    stocks.append(stock)
                    amounts.append(float(row["amount"].replace(",", ".")))

                # De gebruiker voert bedragen in euro in; de berekening gebruikt gewichten.
                # Gewicht = bedrag van het aandeel / totaal bedrag, bv. 600 / 1000 = 0.60.
                total_amount = sum(amounts)
                if total_amount <= 0:
                    raise ValueError("Het totale bedrag moet groter dan 0 zijn")
                for index in range(len(stocks)):
                    stocks[index]["weight"] = amounts[index] / total_amount
                risk_free_rate = float(rate.replace(",", ".")) / 100
                result = calculate_portfolio(stocks, risk_free_rate)
                # Lukt de optimale weging niet, dan tonen we toch het gewone resultaat.
                try:
                    optimal = optimal_weights(stocks, risk_free_rate)
                except ValueError as exc:
                    optimal_error = str(exc)
                if action == "publish":
                    community.add_user(username, stocks, risk_free_rate)
                    session["portfolio_viewer"] = username.strip()
                    viewer = username.strip()
            elif action in ("unlock", "comment"):
                if not viewer:
                    raise ValueError("Publiceer eerst een portefeuille met een unieke gebruikersnaam.")
                if action == "unlock":
                    # Simulatie: hier wordt geen echte betaling gecontroleerd.
                    community.unlock_portfolio(viewer, owner, 5)
                else:
                    community.add_comment(viewer, owner, request.form.get("message", ""))
                opened = community.get_portfolio(viewer, owner)
                comments = community.get_comments(viewer, owner)
            else:
                raise ValueError("Onbekende actie.")
        except (ValueError, PermissionError, OverflowError) as exc:
            error = f"Controleer je invoer: {exc}. Bedragen mogen niet negatief zijn; gebruik geldige getallen en een positieve portefeuillevolatiliteit."
            status = 400
    return render_template("index.html", rows=rows, rate=rate, username=username,
                           result=result, optimal=optimal, optimal_error=optimal_error,
                           stocks=stocks, total_amount=total_amount, error=error, limitation=CORRELATION_LIMITATION,
                           ranking=community.leaderboard(), viewer=viewer,
                           opened=opened, comments=comments), status

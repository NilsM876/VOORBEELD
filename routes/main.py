"""Portfolio form and simulated community, using the existing algorithm API."""
import json
from pathlib import Path

from flask import Blueprint, current_app, render_template, request, session

from algorithm import CORRELATION_LIMITATION, PortfolioCommunity, calculate_portfolio

bp = Blueprint("main", __name__)


def get_community():
    if "portfolio_community" not in current_app.extensions:
        users = json.loads((Path(__file__).resolve().parents[1] / "test_data.json").read_text(encoding="utf-8"))
        current_app.extensions["portfolio_community"] = PortfolioCommunity(users)
    return current_app.extensions["portfolio_community"]


@bp.route("/", methods=["GET", "POST"])
def home():
    community = get_community()
    result = error = opened = None
    comments = []
    owner = request.form.get("owner", "")
    rows = [{"name": "", "return": "", "volatility": "", "weight": ""}]
    rate = request.form.get("risk_free_rate", "2")
    username = request.form.get("username", "")
    viewer = session.get("portfolio_viewer")
    status = 200
    if request.method == "POST":
        try:
            action = request.form.get("action", "calculate")
            if action in ("calculate", "publish"):
                fields = {key: request.form.getlist(key) for key in rows[0]}
                if len({len(values) for values in fields.values()}) != 1:
                    raise ValueError("De aandelenvelden zijn onvolledig.")
                rows = [dict(zip(fields, values)) for values in zip(*fields.values())]
                stocks = [{key: value.strip() if key == "name" else float(value.replace(",", ".")) / 100
                           for key, value in row.items()} for row in rows]
                risk_free_rate = float(rate.replace(",", ".")) / 100
                result = calculate_portfolio(stocks, risk_free_rate)
                if action == "publish":
                    community.add_user(username, stocks, risk_free_rate)
                    session["portfolio_viewer"] = username.strip()
                    viewer = username.strip()
            elif action in ("unlock", "comment"):
                if not viewer:
                    raise ValueError("Publiceer eerst een portefeuille met een unieke gebruikersnaam.")
                if action == "unlock":
                    community.unlock_portfolio(viewer, owner, 5)
                else:
                    community.add_comment(viewer, owner, request.form.get("message", ""))
                opened = community.get_portfolio(viewer, owner)
                comments = community.get_comments(viewer, owner)
            else:
                raise ValueError("Onbekende actie.")
        except (ValueError, PermissionError, OverflowError) as exc:
            error = f"Controleer je invoer: {exc}. Gewichten moeten samen 100% zijn; gebruik geldige getallen en een positieve portefeuillevolatiliteit."
            status = 400
    return render_template("index.html", rows=rows, rate=rate, username=username,
                           result=result, error=error, limitation=CORRELATION_LIMITATION,
                           ranking=community.leaderboard(), viewer=viewer,
                           opened=opened, comments=comments), status

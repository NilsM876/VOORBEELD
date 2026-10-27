"""Een portefeuille van iemand anders bekijken: paywall, ontgrendelen en commentaar."""

from datetime import datetime

from flask import Blueprint, flash, redirect, render_template, request, session, url_for

from models import Asset, Comment, Portfolio, PortfolioAnalysis, PortfolioHolding, PortfolioUnlock, User, db

bp = Blueprint("community", __name__)

UNLOCK_PRICE_EUR = 5


def current_user():
    """De gebruiker die in deze browser publiceerde, of None. Dit is geen login."""
    user_id = session.get("user_id")
    if user_id is None:
        return None
    return db.session.get(User, user_id)


def has_access(user, portfolio):
    """De eigenaar en wie de portefeuille ontgrendeld heeft, mogen ze zien."""
    if user is None:
        return False
    if user.user_id == portfolio.user_id:
        return True
    # De sleutel van PortfolioUnlock bestaat uit twee kolommen: (user_id, portfolio_id).
    unlock = db.session.get(PortfolioUnlock, (user.user_id, portfolio.portfolio_id))
    return unlock is not None


# <int:portfolio_id> haalt het nummer uit het adres, bv. /portfolio/3 geeft 3.
@bp.route("/portfolio/<int:portfolio_id>")
def show(portfolio_id):
    # get_or_404 toont de 404-pagina als de portefeuille niet bestaat.
    portfolio = db.get_or_404(Portfolio, portfolio_id)
    owner = db.session.get(User, portfolio.user_id)
    analysis = PortfolioAnalysis.query.filter_by(portfolio_id=portfolio_id).first()
    user = current_user()
    access = has_access(user, portfolio)

    # De aandelen en het commentaar halen we alleen op voor wie toegang heeft.
    stocks = []
    comments = []
    if access:
        for holding in PortfolioHolding.query.filter_by(portfolio_id=portfolio_id).all():
            asset = db.session.get(Asset, holding.asset_id)
            stocks.append({
                "name": asset.ticker,
                "return": float(holding.expected_return),
                "volatility": float(holding.volatility),
                "amount": float(holding.amount),
                "weight": float(holding.input_weight),
            })
        for comment in Comment.query.filter_by(portfolio_id=portfolio_id).order_by(Comment.comment_id).all():
            author = db.session.get(User, comment.user_id)
            comments.append({"author": author.username, "content": comment.content})

    return render_template("portfolio.html", portfolio=portfolio, owner=owner, analysis=analysis,
                           user=user, access=access, stocks=stocks, comments=comments,
                           price=UNLOCK_PRICE_EUR)


@bp.route("/portfolio/<int:portfolio_id>/unlock", methods=["POST"])
def unlock(portfolio_id):
    portfolio = db.get_or_404(Portfolio, portfolio_id)
    user = current_user()
    if user is None:
        flash("Publiceer eerst je eigen portefeuille, daarna kun je andere ontgrendelen.")
    elif not has_access(user, portfolio):
        # Simulatie: er wordt geen echt geld aangerekend.
        db.session.add(PortfolioUnlock(user_id=user.user_id, portfolio_id=portfolio_id,
                                       amount_eur=UNLOCK_PRICE_EUR, unlocked_at=datetime.now()))
        db.session.commit()
        flash(f"Gesimuleerde betaling van €{UNLOCK_PRICE_EUR} gelukt. Opnieuw bekijken is gratis.")
    # Na een POST sturen we de browser terug naar de gewone pagina (GET).
    return redirect(url_for("community.show", portfolio_id=portfolio_id))


@bp.route("/portfolio/<int:portfolio_id>/comment", methods=["POST"])
def comment(portfolio_id):
    portfolio = db.get_or_404(Portfolio, portfolio_id)
    user = current_user()
    content = request.form.get("content", "").strip()
    if not has_access(user, portfolio):
        flash("Ontgrendel deze portefeuille eerst.")
    elif content == "":
        flash("Een leeg commentaar kan niet geplaatst worden.")
    else:
        db.session.add(Comment(portfolio_id=portfolio_id, user_id=user.user_id,
                               content=content, created_at=datetime.now()))
        db.session.commit()
    return redirect(url_for("community.show", portfolio_id=portfolio_id))

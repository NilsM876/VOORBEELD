"""The model: one class per table in your DDL.

Every column here is a column in database/ddl.sql, with the same name and type.
The DDL is the truth: change the table first, then the class, and tell your group.
"""

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


# Er is nog geen login: email en password_hash krijgen bij publiceren een
# vaste invulwaarde, omdat de kolommen verplicht zijn.
class User(db.Model):
    __tablename__ = "User"
    user_id       = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(100), nullable=False, unique=True)
    email         = db.Column(db.String(255), nullable=False, unique=True)
    password_hash = db.Column(db.String(255), nullable=False)
    created_at    = db.Column(db.DateTime, nullable=False)


class Asset(db.Model):
    __tablename__ = "Asset"
    asset_id   = db.Column(db.Integer, primary_key=True)
    ticker     = db.Column(db.String(30), nullable=False)
    exchange   = db.Column(db.String(30))
    asset_name = db.Column(db.String(200))
    currency   = db.Column(db.String(10))


class Portfolio(db.Model):
    __tablename__ = "Portfolio"
    portfolio_id   = db.Column(db.Integer, primary_key=True)
    user_id        = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    portfolio_name = db.Column(db.String(150), nullable=False)
    is_public      = db.Column(db.Boolean, nullable=False)
    created_at     = db.Column(db.DateTime, nullable=False)


class Subscription(db.Model):
    __tablename__ = "Subscription"
    subscription_id     = db.Column(db.Integer, primary_key=True)
    user_id             = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    payment_provider_id = db.Column(db.String(255), unique=True)
    subscription_status = db.Column(db.String(30), nullable=False)
    start_date          = db.Column(db.DateTime)
    end_date            = db.Column(db.DateTime)


# De sleutel bestaat uit twee kolommen: portfolio_id en asset_id.
class PortfolioHolding(db.Model):
    __tablename__ = "PortfolioHolding"
    portfolio_id     = db.Column(db.Integer, db.ForeignKey("Portfolio.portfolio_id"), primary_key=True)
    asset_id         = db.Column(db.Integer, db.ForeignKey("Asset.asset_id"), primary_key=True)
    amount           = db.Column(db.Numeric(18, 2), nullable=False)
    expected_return  = db.Column(db.Numeric(12, 8), nullable=False)
    volatility       = db.Column(db.Numeric(12, 8), nullable=False)
    price            = db.Column(db.Numeric(18, 6))
    input_weight     = db.Column(db.Numeric(10, 8))
    optimized_weight = db.Column(db.Numeric(10, 8))


class PortfolioAnalysis(db.Model):
    __tablename__ = "PortfolioAnalysis"
    analysis_id          = db.Column(db.Integer, primary_key=True)
    portfolio_id         = db.Column(db.Integer, db.ForeignKey("Portfolio.portfolio_id"), nullable=False)
    start_date           = db.Column(db.Date)
    end_date             = db.Column(db.Date)
    risk_free_rate       = db.Column(db.Numeric(12, 8))
    annual_return        = db.Column(db.Numeric(12, 8))
    annual_volatility    = db.Column(db.Numeric(12, 8))
    sharpe_ratio         = db.Column(db.Numeric(12, 8))
    optimized_return     = db.Column(db.Numeric(12, 8))
    optimized_volatility = db.Column(db.Numeric(12, 8))
    optimized_sharpe     = db.Column(db.Numeric(12, 8))
    optimization_method  = db.Column(db.String(100))
    calculation_version  = db.Column(db.String(30))
    calculated_at        = db.Column(db.DateTime, nullable=False)


# De sleutel bestaat uit twee kolommen: analysis_id en asset_id.
class OptimizedHolding(db.Model):
    __tablename__ = "OptimizedHolding"
    analysis_id = db.Column(db.Integer, db.ForeignKey("PortfolioAnalysis.analysis_id"), primary_key=True)
    asset_id    = db.Column(db.Integer, db.ForeignKey("Asset.asset_id"), primary_key=True)
    weight      = db.Column(db.Numeric(10, 8), nullable=False)


class LeaderboardEntry(db.Model):
    __tablename__ = "LeaderboardEntry"
    entry_id     = db.Column(db.Integer, primary_key=True)
    analysis_id  = db.Column(db.Integer, db.ForeignKey("PortfolioAnalysis.analysis_id"),
                             nullable=False, unique=True)
    user_id      = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False)
    is_visible   = db.Column(db.Boolean, nullable=False)


# De sleutel bestaat uit twee kolommen: user_id en portfolio_id.
class PortfolioUnlock(db.Model):
    __tablename__ = "PortfolioUnlock"
    user_id      = db.Column(db.Integer, db.ForeignKey("User.user_id"), primary_key=True)
    portfolio_id = db.Column(db.Integer, db.ForeignKey("Portfolio.portfolio_id"), primary_key=True)
    amount_eur   = db.Column(db.Numeric(6, 2), nullable=False)
    unlocked_at  = db.Column(db.DateTime, nullable=False)


class Comment(db.Model):
    __tablename__ = "Comment"
    comment_id        = db.Column(db.Integer, primary_key=True)
    portfolio_id      = db.Column(db.Integer, db.ForeignKey("Portfolio.portfolio_id"), nullable=False)
    user_id           = db.Column(db.Integer, db.ForeignKey("User.user_id"), nullable=False)
    content           = db.Column(db.Text, nullable=False)
    created_at        = db.Column(db.DateTime, nullable=False)
    # Leeg bij een gewone reactie, anders de reactie waarop geantwoord wordt.
    parent_comment_id = db.Column(db.Integer, db.ForeignKey("Comment.comment_id"))

-- The DDL of your group's database. This file is the truth:
-- change a table here first, run it, then change the class in models.py.
--
-- Run it against your group database from the client you use for Database Systems.
--
-- Overgenomen uit het dbdiagram van de groep. De tabellen staan in een volgorde
-- waarin elke foreign key naar een tabel verwijst die al bestaat.

CREATE TABLE `User` (
    user_id        INT AUTO_INCREMENT PRIMARY KEY,
    username       VARCHAR(100) NOT NULL UNIQUE,
    email          VARCHAR(255) NOT NULL UNIQUE,
    password_hash  VARCHAR(255) NOT NULL,
    created_at     TIMESTAMP    NOT NULL
);

CREATE TABLE Asset (
    asset_id    INT AUTO_INCREMENT PRIMARY KEY,
    ticker      VARCHAR(30)  NOT NULL,
    exchange    VARCHAR(30)  NOT NULL,
    asset_name  VARCHAR(200),
    currency    VARCHAR(10)
);

CREATE TABLE Portfolio (
    portfolio_id    INT AUTO_INCREMENT PRIMARY KEY,
    user_id         INT          NOT NULL,
    portfolio_name  VARCHAR(150) NOT NULL,
    is_public       BOOLEAN      NOT NULL,
    created_at      TIMESTAMP    NOT NULL,
    FOREIGN KEY (user_id) REFERENCES `User` (user_id)
);

CREATE TABLE Subscription (
    subscription_id      INT AUTO_INCREMENT PRIMARY KEY,
    user_id              INT          NOT NULL,
    payment_provider_id  VARCHAR(255) UNIQUE,
    subscription_status  VARCHAR(30)  NOT NULL,
    start_date           TIMESTAMP    NULL,
    end_date             TIMESTAMP    NULL,
    FOREIGN KEY (user_id) REFERENCES `User` (user_id)
);

-- Eén slotkoers per aandeel per dag.
CREATE TABLE AssetPrice (
    asset_id        INT            NOT NULL,
    price_date      DATE           NOT NULL,
    adjusted_close  DECIMAL(18, 6) NOT NULL,
    PRIMARY KEY (asset_id, price_date),
    FOREIGN KEY (asset_id) REFERENCES Asset (asset_id)
);

-- Eén rij per aandeel in een portefeuille.
CREATE TABLE PortfolioHolding (
    portfolio_id      INT            NOT NULL,
    asset_id          INT            NOT NULL,
    input_weight      DECIMAL(10, 8),
    optimized_weight  DECIMAL(10, 8),
    PRIMARY KEY (portfolio_id, asset_id),
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio (portfolio_id),
    FOREIGN KEY (asset_id) REFERENCES Asset (asset_id)
);

CREATE TABLE PortfolioAnalysis (
    analysis_id           INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id          INT            NOT NULL,
    start_date            DATE           NOT NULL,
    end_date              DATE           NOT NULL,
    risk_free_rate        DECIMAL(12, 8),
    annual_return         DECIMAL(12, 8),
    annual_volatility     DECIMAL(12, 8),
    sharpe_ratio          DECIMAL(12, 8),
    optimized_return      DECIMAL(12, 8),
    optimized_volatility  DECIMAL(12, 8),
    optimized_sharpe      DECIMAL(12, 8),
    optimization_method   VARCHAR(100),
    calculation_version   VARCHAR(30),
    calculated_at         TIMESTAMP      NOT NULL,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio (portfolio_id)
);

-- De optimale weging per aandeel, bij één analyse.
CREATE TABLE OptimizedHolding (
    analysis_id  INT            NOT NULL,
    asset_id     INT            NOT NULL,
    weight       DECIMAL(10, 8) NOT NULL,
    PRIMARY KEY (analysis_id, asset_id),
    FOREIGN KEY (analysis_id) REFERENCES PortfolioAnalysis (analysis_id),
    FOREIGN KEY (asset_id) REFERENCES Asset (asset_id)
);

-- analysis_id is uniek: een analyse staat hoogstens één keer op het leaderboard.
CREATE TABLE LeaderboardEntry (
    entry_id      INT AUTO_INCREMENT PRIMARY KEY,
    analysis_id   INT       NOT NULL UNIQUE,
    user_id       INT       NOT NULL,
    published_at  TIMESTAMP NOT NULL,
    is_visible    BOOLEAN   NOT NULL,
    FOREIGN KEY (analysis_id) REFERENCES PortfolioAnalysis (analysis_id),
    FOREIGN KEY (user_id) REFERENCES `User` (user_id)
);

-- parent_comment_id is leeg bij een gewone reactie en verwijst anders naar
-- de reactie waarop geantwoord wordt.
CREATE TABLE Comment (
    comment_id         INT AUTO_INCREMENT PRIMARY KEY,
    portfolio_id       INT       NOT NULL,
    user_id            INT       NOT NULL,
    content            TEXT      NOT NULL,
    created_at         TIMESTAMP NOT NULL,
    parent_comment_id  INT,
    FOREIGN KEY (portfolio_id) REFERENCES Portfolio (portfolio_id),
    FOREIGN KEY (user_id) REFERENCES `User` (user_id),
    FOREIGN KEY (parent_comment_id) REFERENCES Comment (comment_id)
);

"""Voer een portefeuille in; gebruik --community voor paywall en commentaar."""

import argparse
import json
from pathlib import Path

from algorithm import (
    CORRELATION_LIMITATION, PortfolioCommunity, calculate_portfolio, finite_number,
)


def read_number(prompt, minimum=None, maximum=None):
    while True:
        try:
            value = float(input(prompt).replace(",", "."))
            finite_number(value, "Invoer")
            if minimum is not None and value < minimum:
                raise ValueError
            if maximum is not None and value > maximum:
                raise ValueError
            return value
        except ValueError:
            print("Voer een geldig, eindig getal binnen de aangegeven grenzen in.")


def read_text(prompt):
    while True:
        value = input(prompt).strip()
        if value:
            return value
        print("Deze waarde mag niet leeg zijn.")


def total_weight(stocks):
    """Tel de gewichten van alle aandelen op."""
    total = 0
    for stock in stocks:
        total += stock["weight"]
    return total


def has_portfolio_risk(stocks):
    """Er moet minstens één aandeel met positief gewicht en risico zijn."""
    for stock in stocks:
        if stock["weight"] * stock["volatility"] > 0:
            return True
    return False


def enter_portfolio(community):
    print("Voer percentages in als 10 voor 10%. Gewichten moeten samen 100% zijn.")
    existing_names = []
    for user in community.leaderboard():
        existing_names.append(user["username"])
    while True:
        username = read_text("Gebruikersnaam: ")
        if username not in existing_names:
            break
        print("Deze gebruikersnaam bestaat al. Kies een andere naam.")
    while True:
        try:
            count = int(input("Aantal aandelen (minimaal 1): "))
            if count > 0:
                break
        except ValueError:
            pass
        print("Voer een positief geheel getal in.")
    stocks = []
    for index in range(count):
        print(f"\nAandeel {index + 1} van {count}")
        name = read_text("Naam aandeel: ")
        stocks.append({
            "name": name,
            "return": read_number("Verwacht jaarlijks rendement (%): ") / 100,
            "volatility": read_number("Jaarlijkse standaarddeviatie (%, minimaal 0): ", 0) / 100,
            "weight": read_number("Gewicht (%, 0 tot 100): ", 0, 100) / 100,
        })
    while abs(total_weight(stocks) - 1) > 1e-8:
        print("De gewichten moeten samen 100% zijn. Voer de gewichten opnieuw in.")
        for stock in stocks:
            stock["weight"] = read_number(f"Gewicht {stock['name']} (%, 0 tot 100): ", 0, 100) / 100
    while not has_portfolio_risk(stocks):
        print("De portefeuillevolatiliteit moet positief zijn om de Sharpe ratio te berekenen.")
        for stock in stocks:
            stock["volatility"] = read_number(
                f"Jaarlijkse standaarddeviatie {stock['name']} (%, minimaal 0): ", 0
            ) / 100
    rate = read_number("Jaarlijkse risk-free rate (%): ") / 100
    community.add_user(username, stocks, rate)
    result = calculate_portfolio(stocks, rate)
    print(f"\nResultaten voor {username}")
    print(f"Verwacht rendement: {result['return']:.2%}")
    print(f"Volatiliteit: {result['volatility']:.2%}")
    print(f"Sharpe ratio: {result['sharpe']:.4f}")
    return username


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--interactive", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--community", action="store_true",
                        help="Open na de berekening de gesimuleerde paywall en commentaarfunctie")
    args = parser.parse_args()
    users = json.loads(Path(__file__).with_name("test_data.json").read_text(encoding="utf-8"))
    community = PortfolioCommunity(users)
    print(CORRELATION_LIMITATION)
    print("Het leaderboard bevat fictieve voorbeeldgebruikers. Alles blijft alleen in het geheugen.")
    try:
        viewer = enter_portfolio(community)
        print("\nLeaderboard (hoogste Sharpe ratio eerst):")
        for position, user in enumerate(community.leaderboard(), start=1):
            print(f"{position}. {user['username']}: Sharpe {user['sharpe']:.4f}")
        if args.community:
            print("Betalingen zijn simulaties.")
            owner = input("Portefeuille ontgrendelen van (leeg om te stoppen): ").strip()
            if owner:
                payment = read_number("Gesimuleerde betaling in euro (5): ")
                print(community.unlock_portfolio(viewer, owner, payment))
                message = input("Commentaar (leeg om over te slaan): ").strip()
                if message:
                    community.add_comment(viewer, owner, message)
                    print(community.get_comments(viewer, owner))
    except (ValueError, PermissionError) as exc:
        print(f"Ongeldige invoer: {exc}")
    except (EOFError, KeyboardInterrupt):
        print("\nInvoer afgesloten.")


if __name__ == "__main__":
    main()

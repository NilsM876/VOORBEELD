"""Sharply in de terminal: het algoritme testen op testdata, zonder website.

    python main.py

Je voert een portefeuille in, ziet het resultaat en de optimale weging, en
vergelijkt je Sharpe ratio met de fictieve testpersonen uit test_data.json.
"""

import json
from pathlib import Path

from algorithm import (
    CORRELATION_LIMITATION, amounts_to_weights, calculate_portfolio, leaderboard, optimal_weights,
)


def read_number(question):
    """Blijf vragen tot de gebruiker een getal typt. 10,5 en 10.5 mogen allebei."""
    while True:
        text = input(question).replace(",", ".")
        try:
            return float(text)
        except ValueError:
            print("Dat is geen getal, probeer opnieuw.")


def read_portfolio():
    """Vraag de aandelen en de risk-free rate. De gebruiker typt 10 voor 10%."""
    stocks = []
    count = int(read_number("Aantal aandelen: "))
    for number in range(1, count + 1):
        print(f"\nAandeel {number}")
        stocks.append({
            "name": input("Naam of ticker: ").strip(),
            "return": read_number("Verwacht jaarlijks rendement (%): ") / 100,
            "volatility": read_number("Jaarlijkse standaarddeviatie (%): ") / 100,
            "amount": read_number("Bedrag (euro): "),
        })
    risk_free_rate = read_number("\nJaarlijkse risk-free rate (%): ") / 100
    return stocks, risk_free_rate


def main():
    print(CORRELATION_LIMITATION)
    username = input("\nGebruikersnaam: ").strip()

    # Blijf vragen tot de portefeuille berekend kan worden.
    while True:
        stocks, risk_free_rate = read_portfolio()
        try:
            amounts_to_weights(stocks)
            result = calculate_portfolio(stocks, risk_free_rate)
            break
        except ValueError as error:
            print(f"\n{error}. Voer de portefeuille opnieuw in.\n")

    print(f"\nResultaten voor {username}")
    # :.2% toont 0.084 als 8.40%; :.4f toont 4 cijfers na de komma.
    print(f"Verwacht rendement: {result['return']:.2%}")
    print(f"Volatiliteit:       {result['volatility']:.2%}")
    print(f"Sharpe ratio:       {result['sharpe']:.4f}")

    print("\nOptimale weging:")
    try:
        optimal = optimal_weights(stocks, risk_free_rate)
        for stock in optimal["stocks"]:
            print(f"  {stock['name']}: {stock['weight']:.2%}")
        print(f"  Sharpe ratio: {optimal['sharpe']:.4f}")
    except ValueError as error:
        print(f"  Niet mogelijk: {error}")

    # test_data.json staat in dezelfde map als dit bestand.
    data_file = Path(__file__).with_name("test_data.json")
    with open(data_file, encoding="utf-8") as file:
        users = json.load(file)
    for user in users:
        amounts_to_weights(user["stocks"])
    users.append({"username": username, "stocks": stocks, "risk_free_rate": risk_free_rate})

    print("\nLeaderboard (hoogste Sharpe ratio eerst):")
    position = 1
    for entry in leaderboard(users):
        print(f"{position}. {entry['username']}: {entry['sharpe']:.4f}")
        position += 1


# Alleen als je dit bestand zelf start (python main.py), niet bij een import.
if __name__ == "__main__":
    main()

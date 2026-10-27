"""Test de berekeningen op de testpersonen uit test_data.json.

    python -m unittest discover -s tests -v
"""

import json
import math
import unittest
from pathlib import Path

from algorithm import amounts_to_weights, calculate_portfolio, leaderboard, optimal_weights

DATA_FILE = Path(__file__).parent.parent / "test_data.json"


class AlgorithmTests(unittest.TestCase):
    def setUp(self):
        with open(DATA_FILE, encoding="utf-8") as file:
            self.users = json.load(file)
        for user in self.users:
            amounts_to_weights(user["stocks"])
        self.stocks = self.users[0]["stocks"]

    def test_amounts_to_weights(self):
        # persoon A: 600 en 400 euro geeft 60% en 40%.
        self.assertAlmostEqual(self.stocks[0]["weight"], 0.60)
        self.assertAlmostEqual(self.stocks[1]["weight"], 0.40)
        for amounts in ([0, 0], [-100, 200]):
            stocks = [{"amount": amount} for amount in amounts]
            with self.subTest(amounts=amounts), self.assertRaises(ValueError):
                amounts_to_weights(stocks)

    def test_known_calculation(self):
        result = calculate_portfolio(self.stocks, 0.02)
        self.assertAlmostEqual(result["return"], 0.084)
        self.assertAlmostEqual(result["volatility"], math.sqrt(0.016))
        self.assertAlmostEqual(result["sharpe"], 0.064 / math.sqrt(0.016))

    def test_negative_and_zero_sharpe(self):
        stocks = self.users[2]["stocks"]
        self.assertAlmostEqual(calculate_portfolio(stocks, 0.02)["sharpe"], -0.1)
        self.assertEqual(calculate_portfolio(stocks, 0.01)["sharpe"], 0)

    def test_invalid_stock_inputs(self):
        for key, value in [("weight", -1), ("weight", 0.2), ("volatility", -0.1),
                           ("return", float("nan")), ("weight", float("inf")),
                           ("return", True), ("volatility", "0.2"), ("name", " ")]:
            with self.subTest(key=key, value=value):
                stocks = [dict(stock) for stock in self.stocks]
                stocks[0][key] = value
                with self.assertRaises(ValueError):
                    calculate_portfolio(stocks, 0.02)

    def test_invalid_rate_empty_and_zero_volatility(self):
        for rate in [float("nan"), float("inf"), None, True]:
            with self.subTest(rate=rate), self.assertRaises(ValueError):
                calculate_portfolio(self.stocks, rate)
        with self.assertRaises(ValueError):
            calculate_portfolio([], 0.02)
        with self.assertRaises(ValueError):
            calculate_portfolio([{"name": "A", "return": 0.1, "volatility": 0, "weight": 1}], 0)

    def test_optimal_weights(self):
        # Scores: A = 0.08 / 0.04 = 2, B = 0.04 / 0.01 = 4, dus 1/3 en 2/3.
        optimal = optimal_weights(self.stocks, 0.02)
        self.assertAlmostEqual(optimal["stocks"][0]["weight"], 1 / 3)
        self.assertAlmostEqual(optimal["stocks"][1]["weight"], 2 / 3)
        self.assertGreater(optimal["sharpe"], calculate_portfolio(self.stocks, 0.02)["sharpe"])

    def test_optimal_weights_skips_stocks_below_risk_free_rate(self):
        stocks = self.stocks + [{"name": "C", "return": 0.01, "volatility": 0, "weight": 0}]
        self.assertEqual(optimal_weights(stocks, 0.02)["stocks"][2]["weight"], 0)

    def test_optimal_weights_errors(self):
        no_risk = [{"name": "A", "return": 0.10, "volatility": 0, "weight": 1}]
        too_low = [{"name": "A", "return": 0.01, "volatility": 0.10, "weight": 1}]
        for stocks in (no_risk, too_low):
            with self.subTest(stocks=stocks), self.assertRaises(ValueError):
                optimal_weights(stocks, 0.02)

    def test_leaderboard(self):
        ranking = leaderboard(self.users)
        self.assertEqual([entry["username"] for entry in ranking], ["persoon A", "persoon B", "persoon C"])
        self.assertEqual(leaderboard([]), [])


if __name__ == "__main__":
    unittest.main()

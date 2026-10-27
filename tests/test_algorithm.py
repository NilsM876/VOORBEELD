import json
import math
from pathlib import Path
import unittest

from algorithm import PortfolioCommunity, calculate_portfolio, leaderboard, optimal_weights
from algorithm import portfolio


class AlgorithmTests(unittest.TestCase):
    def test_public_api_reexports_portfolio_functions(self):
        self.assertIs(calculate_portfolio, portfolio.calculate_portfolio)
        self.assertIs(leaderboard, portfolio.leaderboard)

    def setUp(self):
        self.users = json.loads((Path(__file__).resolve().parents[1] / "test_data.json").read_text())
        self.stocks = self.users[0]["stocks"]
        self.community = PortfolioCommunity(self.users)

    def test_known_calculation(self):
        result = calculate_portfolio(self.stocks, 0.02)
        self.assertAlmostEqual(result["return"], 0.084)
        self.assertAlmostEqual(result["volatility"], math.sqrt(0.016))
        self.assertAlmostEqual(result["sharpe"], 0.064 / math.sqrt(0.016))

    def test_single_stock_negative_and_zero_sharpe(self):
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
        optimal = optimal_weights(stocks, 0.02)
        self.assertEqual(optimal["stocks"][2]["weight"], 0)

    def test_optimal_weights_errors(self):
        no_risk = [{"name": "A", "return": 0.10, "volatility": 0, "weight": 1}]
        with self.assertRaises(ValueError):
            optimal_weights(no_risk, 0.02)
        too_low = [{"name": "A", "return": 0.01, "volatility": 0.10, "weight": 1}]
        with self.assertRaises(ValueError):
            optimal_weights(too_low, 0.02)

    def test_ranking_and_privacy(self):
        ranking = self.community.leaderboard()
        self.assertEqual([r["username"] for r in ranking], ["persoon A", "persoon B", "persoon C"])
        self.assertTrue(all(set(r) == {"username", "sharpe"} for r in ranking))
        self.assertEqual(leaderboard([]), [])
        self.users[1]["stocks"] = self.stocks
        self.assertEqual([r["username"] for r in leaderboard(self.users)][:2], ["persoon A", "persoon B"])

    def test_payment_validation(self):
        for payment in [0, 4.99, 6, float("nan"), float("inf"), True, "5"]:
            with self.subTest(payment=payment), self.assertRaises(ValueError):
                self.community.unlock_portfolio("persoon A", "persoon B", payment)
        with self.assertRaises(PermissionError):
            self.community.get_portfolio("persoon A", "persoon B")

    def test_access_scoped_to_viewer_and_owner(self):
        unlocked = self.community.unlock_portfolio("persoon A", "persoon B", 5)
        self.assertEqual(unlocked, self.users[1])
        self.assertEqual(self.community.unlock_portfolio("persoon A", "persoon B", 0), unlocked)
        for viewer, owner in [("persoon C", "persoon B"), ("persoon A", "persoon C"), ("persoon B", "persoon A")]:
            with self.subTest(viewer=viewer, owner=owner), self.assertRaises(PermissionError):
                self.community.get_portfolio(viewer, owner)

    def test_comments(self):
        with self.assertRaises(PermissionError):
            self.community.add_comment("persoon A", "persoon B", "Hallo")
        self.community.unlock_portfolio("persoon A", "persoon B", 5)
        for message in ["", "  ", None]:
            with self.assertRaises(ValueError):
                self.community.add_comment("persoon A", "persoon B", message)
        self.community.add_comment("persoon A", "persoon B", "  Interessant!  ")
        self.assertEqual(self.community.get_comments("persoon A", "persoon B"),
                         [{"author": "persoon A", "message": "Interessant!"}])
        with self.assertRaises(PermissionError):
            self.community.add_comment("persoon C", "persoon B", "Hallo")
        with self.assertRaises(PermissionError):
            self.community.get_comments("persoon C", "persoon B")

    def test_ownership_and_user_validation(self):
        self.assertEqual(self.community.get_portfolio("persoon A", "persoon A"), self.users[0])
        for viewer, owner in [("onbekende persoon", "persoon A"), ("persoon A", "onbekende persoon")]:
            with self.assertRaises(ValueError):
                self.community.unlock_portfolio(viewer, owner, 5)
        for username in ["persoon A", " "]:
            with self.assertRaises(ValueError):
                self.community.add_user(username, self.stocks, 0.02)

    def test_defensive_copies(self):
        self.users[0]["stocks"][0]["return"] = 999
        self.assertEqual(self.community.get_portfolio("persoon A", "persoon A")["stocks"][0]["return"], 0.1)
        unlocked = self.community.unlock_portfolio("persoon A", "persoon B", 5)
        unlocked["stocks"].clear()
        self.assertTrue(self.community.get_portfolio("persoon A", "persoon B")["stocks"])
        self.community.add_comment("persoon A", "persoon B", "Hallo")
        self.community.get_comments("persoon A", "persoon B").clear()
        self.assertEqual(len(self.community.get_comments("persoon A", "persoon B")), 1)


if __name__ == "__main__":
    unittest.main()

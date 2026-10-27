"""Test de website met een tijdelijke SQLite-database in het geheugen, zonder MySQL."""

import unittest

from flask import Flask
from werkzeug.datastructures import MultiDict

from models import Comment, LeaderboardEntry, OptimizedHolding, PortfolioHolding, PortfolioUnlock, db
from routes.community import bp as community_bp
from routes.main import bp as main_bp


class WebsiteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder="../templates", static_folder="../static")
        self.app.config.update(TESTING=True, SECRET_KEY="test",
                               SQLALCHEMY_DATABASE_URI="sqlite:///:memory:")
        db.init_app(self.app)
        self.app.register_blueprint(main_bp)
        self.app.register_blueprint(community_bp)
        with self.app.app_context():
            db.create_all()
        self.client = self.app.test_client()
        self.data = MultiDict([
            ("name", "A"), ("return", "10"), ("volatility", "20"), ("amount", "600"),
            ("name", "B"), ("return", "6"), ("volatility", "10"), ("amount", "400"),
            ("risk_free_rate", "2"), ("username", "persoon D"), ("action", "calculate"),
        ])

    def publish(self, client, username):
        data = self.data.copy()
        data["username"] = username
        data["action"] = "publish"
        return client.post("/", data=data)

    def test_calculation(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        response = self.client.post("/", data=self.data)
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        for expected in ("8.40%", "12.65%", "0.5060", "als nul verondersteld",
                         "Optimale weging", "33.33", "66.67", "333.33"):
            self.assertIn(expected, text)

    def test_invalid_input(self):
        for field, value in [("amount", "0"), ("amount", "-1"), ("volatility", "-1"),
                             ("return", "nan"), ("risk_free_rate", "inf"), ("name", ""),
                             ("return", "abc")]:
            with self.subTest(field=field, value=value):
                data = self.data.copy()
                data.setlist(field, [value] * len(data.getlist(field)))
                self.assertEqual(self.client.post("/", data=data).status_code, 400)
        self.assertEqual(self.client.post("/", data={"action": "calculate"}).status_code, 400)

    def test_publish_saves_to_database(self):
        self.assertEqual(self.publish(self.client, "persoon D").status_code, 200)
        self.assertIn("persoon D", self.client.get("/").get_data(as_text=True))
        with self.app.app_context():
            self.assertEqual(LeaderboardEntry.query.count(), 1)
            self.assertEqual(PortfolioHolding.query.count(), 2)
            self.assertEqual(OptimizedHolding.query.count(), 2)
        # Dezelfde naam of hetzelfde aandeel twee keer wordt geweigerd.
        self.assertEqual(self.publish(self.app.test_client(), "persoon D").status_code, 400)
        data = self.data.copy()
        data.setlist("name", ["A", "a"])
        data["action"] = "publish"
        data["username"] = "persoon E"
        self.assertEqual(self.client.post("/", data=data).status_code, 400)

    def test_paywall_unlock_and_comment(self):
        owner = self.app.test_client()
        self.publish(owner, "persoon B")
        url = "/portfolio/1"
        # Eigenaar ziet alles; een bezoeker zonder publicatie kan niet ontgrendelen.
        self.assertIn("Commentaar", owner.get(url).get_data(as_text=True))
        self.client.post(url + "/unlock")
        self.assertIn("Publiceer eerst", self.client.get(url).get_data(as_text=True))

        self.publish(self.client, "persoon D")
        self.assertIn("Ontgrendelen voor", self.client.get(url).get_data(as_text=True))
        self.client.post(url + "/comment", data={"content": "Te vroeg"})
        self.client.post(url + "/unlock")
        self.client.post(url + "/unlock")  # opnieuw ontgrendelen kost niets extra
        self.client.post(url + "/comment", data={"content": "   "})
        self.client.post(url + "/comment", data={"content": "Interessant!"})
        text = self.client.get(url).get_data(as_text=True)
        self.assertIn("Interessant!", text)
        self.assertIn("Standaarddeviatie", text)
        with self.app.app_context():
            self.assertEqual(PortfolioUnlock.query.count(), 1)
            self.assertEqual(Comment.query.count(), 1)
        self.assertEqual(self.client.get("/portfolio/99").status_code, 404)


if __name__ == "__main__":
    unittest.main()

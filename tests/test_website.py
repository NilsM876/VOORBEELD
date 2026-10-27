"""Exercise the website without requiring a database connection."""
import unittest

from flask import Flask
from werkzeug.datastructures import MultiDict

from routes.main import bp


class WebsiteTests(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__, template_folder="../templates", static_folder="../static")
        self.app.config.update(TESTING=True, SECRET_KEY="test-key")
        self.app.register_blueprint(bp)
        self.client = self.app.test_client()
        self.data = MultiDict([
            ("name", "A"), ("return", "10"), ("volatility", "20"), ("amount", "600"),
            ("name", "B"), ("return", "6"), ("volatility", "10"), ("amount", "400"),
            ("risk_free_rate", "2"), ("username", "persoon D"), ("action", "calculate"),
        ])

    def test_form_and_percentage_conversion(self):
        self.assertEqual(self.client.get("/").status_code, 200)
        response = self.client.post("/", data=self.data)
        self.assertEqual(response.status_code, 200)
        text = response.get_data(as_text=True)
        for expected in ("8.40%", "12.65%", "0.5060", "als nul verondersteld",
                         "Optimale weging", "33.33", "66.67", "333.33"):
            self.assertIn(expected, text)

    def test_invalid_input(self):
        for field, value in [("amount", "0"), ("amount", "-1"), ("volatility", "-1"),
                             ("return", "nan"), ("risk_free_rate", "inf"), ("name", "")]:
            with self.subTest(field=field):
                data = self.data.copy()
                data.setlist(field, [value] * len(data.getlist(field)))
                self.assertEqual(self.client.post("/", data=data).status_code, 400)
        self.assertEqual(self.client.post("/", data={"action": "calculate"}).status_code, 400)

    def test_publish_unlock_and_comment(self):
        self.data["action"] = "publish"
        self.assertEqual(self.client.post("/", data=self.data).status_code, 200)
        self.assertIn("persoon D", self.client.get("/").get_data(as_text=True))
        action = {"owner": "persoon B", "action": "comment", "message": "Interessant!"}
        self.assertEqual(self.client.post("/", data=action).status_code, 400)
        self.assertEqual(self.client.post("/", data={"owner": "persoon B", "action": "unlock"}).status_code, 200)
        response = self.client.post("/", data=action)
        self.assertEqual(response.status_code, 200)
        self.assertIn("Interessant!", response.get_data(as_text=True))
        other_client = self.app.test_client()
        self.assertEqual(other_client.post("/", data=action).status_code, 400)

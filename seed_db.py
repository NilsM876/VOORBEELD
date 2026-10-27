"""Zet de fictieve testpersonen uit test_data.json in de database.

    python seed_db.py

Voer eerst database/ddl.sql uit. Wie al in de database staat, wordt overgeslagen.
"""

import json

from algorithm import amounts_to_weights
from app import app
from models import User
from routes.main import publish_portfolio

with open("test_data.json", encoding="utf-8") as file:
    users = json.load(file)

# Buiten een webrequest heeft de database een "app context" nodig.
with app.app_context():
    for user in users:
        if User.query.filter_by(username=user["username"]).first() is not None:
            print(f"{user['username']} staat al in de database")
            continue
        amounts_to_weights(user["stocks"])
        publish_portfolio(user["username"], user["stocks"], user["risk_free_rate"])
        print(f"{user['username']} toegevoegd")

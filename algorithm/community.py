"""In-memory community and simulated payments; no actual money is charged."""

from copy import deepcopy

from .portfolio import calculate_portfolio, finite_number, leaderboard


class PortfolioCommunity:
    """Bundel de gegevens en functies van één community.

    self verwijst naar deze community. De gegevens bestaan zolang dit object
    bestaat, dus over meerdere webrequests heen, tot de server stopt.
    """

    UNLOCK_PRICE_EUR = 5

    def __init__(self, users=()):
        # __init__ wordt uitgevoerd bij PortfolioCommunity(users).
        # Dictionary: gebruikersnaam -> portefeuille.
        self._users = {}
        # Dictionary: tuple (bezoeker, eigenaar) -> True.
        # ('persoon A', 'persoon B') geeft persoon A toegang tot persoon B, niet omgekeerd.
        self._unlocks = {}
        # Dictionary: eigenaar -> lijst met reacties.
        self._comments = {}
        for user in users:
            self.add_user(user["username"], user["stocks"], user["risk_free_rate"])

    def add_user(self, username, stocks, risk_free_rate):
        if not isinstance(username, str) or not username.strip():
            raise ValueError("Username cannot be empty")
        username = username.strip()
        if username in self._users:
            raise ValueError("Username already exists")
        # Controleer de invoer voordat deze wordt opgeslagen.
        calculate_portfolio(stocks, risk_free_rate)
        # deepcopy kopieert ook de lijsten en dictionaries binnenin.
        # Zo kan de aanroeper onze opgeslagen gegevens niet achteraf wijzigen.
        self._users[username] = deepcopy({
            "username": username, "stocks": stocks, "risk_free_rate": risk_free_rate
        })

    def _require_user(self, username):
        if username not in self._users:
            raise ValueError("User not found")

    def leaderboard(self):
        return leaderboard(self._users.values())

    def unlock_portfolio(self, viewer, owner, payment_eur):
        """Accept a simulated payment of exactly EUR 5; repeated access is free."""
        self._require_user(viewer)
        self._require_user(owner)
        if viewer == owner or (viewer, owner) in self._unlocks:
            return self.get_portfolio(viewer, owner)
        finite_number(payment_eur, "Payment")
        if payment_eur != self.UNLOCK_PRICE_EUR:
            raise ValueError("Simulated payment must be exactly EUR 5")
        self._unlocks[(viewer, owner)] = True
        return self.get_portfolio(viewer, owner)

    def get_portfolio(self, viewer, owner):
        self._require_user(viewer)
        self._require_user(owner)
        if viewer != owner and (viewer, owner) not in self._unlocks:
            raise PermissionError("Unlock this portfolio first")
        return deepcopy(self._users[owner])

    def add_comment(self, author, owner, message):
        self._require_user(author)
        self._require_user(owner)
        if (author, owner) not in self._unlocks:
            raise PermissionError("Unlock this portfolio before commenting")
        if not isinstance(message, str) or not message.strip():
            raise ValueError("Comment cannot be empty")
        comment = {"author": author, "message": message.strip()}
        if owner not in self._comments:
            self._comments[owner] = []
        self._comments[owner].append(comment)
        return deepcopy(comment)

    def get_comments(self, viewer, owner):
        self.get_portfolio(viewer, owner)
        return deepcopy(self._comments.get(owner, []))

"""Voer een portefeuille in; gebruik --community voor paywall en commentaar."""
# Een tekst tussen drie aanhalingstekens bovenaan een bestand heet een "docstring".
# Het is een beschrijving van het bestand. Hier wordt hij ook gebruikt als helptekst
# wanneer je "python main.py --help" typt.
#
# Alles wat na een # staat, is commentaar: uitleg voor mensen. Python slaat het over.
#
# WAT DOET DIT BESTAND?
# Dit is de terminalversie van de app: dezelfde berekeningen als de website, maar
# zonder browser. Je typt alles in de terminal. Starten doe je zo:
#     python main.py              -> portefeuille invoeren en resultaat zien
#     python main.py --community  -> daarna ook een portefeuille ontgrendelen en reageren
#
# Let op: hier voer je nog GEWICHTEN in procent in, geen bedragen in euro zoals op
# de website.

# "import" haalt code binnen die iemand anders al geschreven heeft.
# argparse: leest extra woorden achter het commando, zoals --community.
import argparse
# json: om een .json-bestand (een tekstbestand met gegevens) te lezen.
import json
# Path: om met bestandsnamen en mappen te werken.
from pathlib import Path

# Uit onze eigen map algorithm/ halen we:
# - CORRELATION_LIMITATION: een waarschuwingstekst over de berekening.
# - PortfolioCommunity: bewaart alle gebruikers, ontgrendelingen en commentaren.
# - calculate_portfolio: berekent rendement, volatiliteit en Sharpe ratio.
# - finite_number: controleert of iets een geldig, gewoon getal is.
# De haakjes ( ) zorgen ervoor dat de import over meerdere regels mag lopen.
from algorithm import (
    CORRELATION_LIMITATION, PortfolioCommunity, calculate_portfolio, finite_number,
)


# "def" maakt een functie: een stuk code met een naam dat je later kunt oproepen.
# Deze functie vraagt een getal aan de gebruiker en blijft vragen tot het klopt.
# prompt is de vraag die op het scherm komt.
# minimum en maximum zijn grenzen. "=None" betekent: als je ze niet meegeeft,
# is er geen grens.
def read_number(prompt, minimum=None, maximum=None):
    # "while True" is een lus die altijd blijft herhalen, tot er een "return" komt.
    while True:
        # "try": probeer dit. Loopt er iets mis, dan springt Python naar "except".
        try:
            # input(prompt) toont de vraag en wacht tot de gebruiker iets typt.
            # .replace(",", ".") maakt van 10,5 de Python-schrijfwijze 10.5.
            # float() maakt van de tekst een kommagetal. Lukt dat niet (bv. bij
            # "abc"), dan ontstaat een ValueError.
            value = float(input(prompt).replace(",", "."))
            # Weiger "oneindig" en "geen getal" (die bestaan in Python).
            finite_number(value, "Invoer")
            # Is er een minimum en ligt het getal eronder? Dan is het fout.
            # "raise" maakt zelf een fout aan, zodat we naar "except" springen.
            if minimum is not None and value < minimum:
                raise ValueError
            # Hetzelfde voor het maximum.
            if maximum is not None and value > maximum:
                raise ValueError
            # Alles klopt: geef het getal terug. "return" stopt ook de lus.
            return value
        # Bij een fout tonen we een melding. Daarna begint de lus opnieuw.
        except ValueError:
            print("Voer een geldig, eindig getal binnen de aangegeven grenzen in.")


# Deze functie vraagt een tekst en blijft vragen tot die niet leeg is.
def read_text(prompt):
    while True:
        # .strip() haalt spaties vooraan en achteraan weg.
        value = input(prompt).strip()
        # Een niet-lege tekst telt als "waar". Dan geven we hem terug.
        if value:
            return value
        # Anders tonen we een melding en vragen we opnieuw.
        print("Deze waarde mag niet leeg zijn.")


def total_weight(stocks):
    """Tel de gewichten van alle aandelen op."""
    # We beginnen bij 0.
    total = 0
    # stocks is een lijst van aandelen. De for-lus gaat ze één voor één af.
    for stock in stocks:
        # += betekent "tel erbij op": total = total + stock["weight"].
        total += stock["weight"]
    # Geef de som terug.
    return total


def has_portfolio_risk(stocks):
    """Er moet minstens één aandeel met positief gewicht en risico zijn."""
    # Zonder risico is de volatiliteit 0. Dan kun je de Sharpe ratio niet
    # berekenen, want je zou door 0 delen.
    for stock in stocks:
        # Gewicht maal volatiliteit groter dan 0? Dan is er risico.
        if stock["weight"] * stock["volatility"] > 0:
            # True betekent "waar". We hebben er één gevonden, dus we stoppen.
            return True
    # De lus is helemaal doorlopen zonder iets te vinden: "niet waar".
    return False


# Deze functie laat de gebruiker een volledige portefeuille invoeren,
# zet ze in de community en toont het resultaat.
def enter_portfolio(community):
    # print() toont tekst in de terminal.
    print("Voer percentages in als 10 voor 10%. Gewichten moeten samen 100% zijn.")

    # --- Stap 1: een unieke gebruikersnaam vragen ---
    # Eerst maken we een lijst met alle namen die al bestaan.
    existing_names = []
    for user in community.leaderboard():
        # Elk item op het leaderboard is een dictionary met o.a. "username".
        existing_names.append(user["username"])
    # Blijf vragen tot de naam nog niet bestaat.
    while True:
        username = read_text("Gebruikersnaam: ")
        # "not in" is waar als de naam NIET in de lijst staat.
        if username not in existing_names:
            # "break" stopt de while-lus meteen.
            break
        print("Deze gebruikersnaam bestaat al. Kies een andere naam.")

    # --- Stap 2: vragen hoeveel aandelen er zijn ---
    while True:
        try:
            # int() maakt van tekst een geheel getal. "2.5" of "abc" geven een fout.
            count = int(input("Aantal aandelen (minimaal 1): "))
            # Het aantal moet groter dan 0 zijn.
            if count > 0:
                break
        except ValueError:
            # "pass" betekent "doe niets". De melding hieronder volgt toch.
            pass
        print("Voer een positief geheel getal in.")

    # --- Stap 3: de gegevens van elk aandeel vragen ---
    # Een lege lijst waarin we de aandelen verzamelen.
    stocks = []
    # range(count) geeft 0, 1, 2, ... tot count - 1: één keer per aandeel.
    for index in range(count):
        # "\n" is een nieuwe regel. In een f-string (f"...") komen de variabelen
        # tussen { } in de tekst. index + 1 omdat mensen vanaf 1 tellen, Python vanaf 0.
        print(f"\nAandeel {index + 1} van {count}")
        name = read_text("Naam aandeel: ")
        # Voeg een dictionary toe met de gegevens van dit aandeel.
        # Delen door 100 maakt van een percentage een fractie: 10 wordt 0.10.
        stocks.append({
            "name": name,
            # Het rendement mag ook negatief zijn, dus geen grenzen.
            "return": read_number("Verwacht jaarlijks rendement (%): ") / 100,
            # De standaarddeviatie (volatiliteit) moet minstens 0 zijn.
            "volatility": read_number("Jaarlijkse standaarddeviatie (%, minimaal 0): ", 0) / 100,
            # Het gewicht ligt tussen 0 en 100 procent.
            "weight": read_number("Gewicht (%, 0 tot 100): ", 0, 100) / 100,
        })

    # --- Stap 4: controleren of de gewichten samen 100% zijn ---
    # abs() geeft de afstand tot 0, zonder minteken. Is het verschil tussen het
    # totaal en 1 (= 100%) groter dan een piepklein getal (1e-8 = 0.00000001)?
    # Dan klopt het niet. Dat piepkleine getal vangt kleine afrondingsfouten op.
    while abs(total_weight(stocks) - 1) > 1e-8:
        print("De gewichten moeten samen 100% zijn. Voer de gewichten opnieuw in.")
        # Vraag voor elk aandeel opnieuw het gewicht.
        for stock in stocks:
            stock["weight"] = read_number(f"Gewicht {stock['name']} (%, 0 tot 100): ", 0, 100) / 100

    # --- Stap 5: controleren of er risico in de portefeuille zit ---
    # "while not ..." herhaalt zolang het NIET waar is.
    while not has_portfolio_risk(stocks):
        print("De portefeuillevolatiliteit moet positief zijn om de Sharpe ratio te berekenen.")
        # Vraag voor elk aandeel opnieuw de standaarddeviatie.
        for stock in stocks:
            stock["volatility"] = read_number(
                f"Jaarlijkse standaarddeviatie {stock['name']} (%, minimaal 0): ", 0
            ) / 100

    # --- Stap 6: de risk-free rate vragen ---
    rate = read_number("Jaarlijkse risk-free rate (%): ") / 100

    # --- Stap 7: opslaan en berekenen ---
    # Zet de gebruiker met zijn portefeuille in de community (en dus op het leaderboard).
    community.add_user(username, stocks, rate)
    # Bereken rendement, volatiliteit en Sharpe ratio.
    result = calculate_portfolio(stocks, rate)

    # --- Stap 8: het resultaat tonen ---
    print(f"\nResultaten voor {username}")
    # :.2% toont een fractie als percentage met 2 cijfers na de komma: 0.084 -> 8.40%.
    print(f"Verwacht rendement: {result['return']:.2%}")
    print(f"Volatiliteit: {result['volatility']:.2%}")
    # :.4f toont een getal met 4 cijfers na de komma: 0.50596 -> 0.5060.
    print(f"Sharpe ratio: {result['sharpe']:.4f}")
    # Geef de gebruikersnaam terug, zodat main() weet wie er aan het werk is.
    return username


# Dit is de hoofdfunctie: hier begint het programma.
def main():
    # --- Extra woorden achter het commando lezen ---
    # Een ArgumentParser leest wat je achter "python main.py" typt.
    # description=__doc__ gebruikt de docstring bovenaan als helptekst.
    parser = argparse.ArgumentParser(description=__doc__)
    # --interactive: een oude optie die niets meer doet. SUPPRESS verbergt ze in de help.
    parser.add_argument("--interactive", action="store_true", help=argparse.SUPPRESS)
    # --community: als je dit toevoegt, wordt args.community True.
    # "store_true" betekent: staat het woord erbij, dan True, anders False.
    parser.add_argument("--community", action="store_true",
                        help="Open na de berekening de gesimuleerde paywall en commentaarfunctie")
    # Lees nu echt wat er getypt werd.
    args = parser.parse_args()

    # --- De fictieve testgebruikers inladen ---
    # Path(__file__) is het pad van dit bestand. .with_name("test_data.json") geeft
    # het bestand test_data.json in dezelfde map. read_text leest het als tekst,
    # json.loads zet die tekst om naar een lijst met gebruikers.
    users = json.loads(Path(__file__).with_name("test_data.json").read_text(encoding="utf-8"))
    # Maak de community met die gebruikers.
    community = PortfolioCommunity(users)
    # Toon de waarschuwing en wat uitleg.
    print(CORRELATION_LIMITATION)
    print("Het leaderboard bevat fictieve voorbeeldgebruikers. Alles blijft alleen in het geheugen.")

    try:
        # --- De gebruiker zijn portefeuille laten invoeren ---
        # viewer is de naam van de gebruiker die nu aan het werk is.
        viewer = enter_portfolio(community)

        # --- Het leaderboard tonen ---
        print("\nLeaderboard (hoogste Sharpe ratio eerst):")
        # enumerate() geeft bij elk item ook een volgnummer. start=1 laat de
        # nummering bij 1 beginnen in plaats van bij 0.
        for position, user in enumerate(community.leaderboard(), start=1):
            print(f"{position}. {user['username']}: Sharpe {user['sharpe']:.4f}")

        # --- Alleen met --community: ontgrendelen en commentaar ---
        if args.community:
            print("Betalingen zijn simulaties.")
            # Vraag wiens portefeuille de gebruiker wil zien.
            owner = input("Portefeuille ontgrendelen van (leeg om te stoppen): ").strip()
            # Lege tekst telt als "niet waar". Dan slaan we dit over.
            if owner:
                # "Betaal" (in simulatie) het gevraagde bedrag. Het moet precies 5 zijn.
                payment = read_number("Gesimuleerde betaling in euro (5): ")
                # Ontgrendel en toon de portefeuille van de ander.
                print(community.unlock_portfolio(viewer, owner, payment))
                # Vraag een commentaar. Leeg laten mag.
                message = input("Commentaar (leeg om over te slaan): ").strip()
                if message:
                    # Plaats het commentaar en toon alle commentaren.
                    community.add_comment(viewer, owner, message)
                    print(community.get_comments(viewer, owner))

    # Een ongeldige waarde of iets wat niet mag (bv. een onbekende naam of een
    # verkeerde betaling): toon de foutmelding.
    except (ValueError, PermissionError) as exc:
        print(f"Ongeldige invoer: {exc}")
    # EOFError: de invoer stopte onverwacht. KeyboardInterrupt: de gebruiker
    # drukte op Ctrl+C. In beide gevallen stoppen we netjes.
    except (EOFError, KeyboardInterrupt):
        print("\nInvoer afgesloten.")


# __name__ is "__main__" als je dit bestand rechtstreeks start met "python main.py".
# Wordt het bestand door een ander bestand geïmporteerd, dan is __name__ anders
# en start main() niet vanzelf.
if __name__ == "__main__":
    main()

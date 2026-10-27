"""Portfolio form and simulated community, using the existing algorithm API."""
# Een tekst tussen drie aanhalingstekens bovenaan een bestand heet een "docstring".
# Het is gewoon een beschrijving van wat dit bestand doet. Python voert er niets mee uit.
#
# Alles wat na een # staat, is commentaar: uitleg voor mensen. Python slaat het over.
#
# WAT DOET DIT BESTAND?
# Dit bestand bevat de code van de website. Als iemand de website opent of op een
# knop drukt, komt Python hier terecht. De code leest wat de gebruiker heeft ingevuld,
# laat de berekeningen doen en stuurt een HTML-pagina terug naar de browser.

# "import" haalt code binnen die iemand anders al geschreven heeft.
# json: om een .json-bestand (een tekstbestand met gegevens) te lezen.
import json
# Path: om met mappen en bestandsnamen te werken, bijvoorbeeld "zoek test_data.json".
from pathlib import Path

# Uit Flask (de bibliotheek waarmee we de website maken) halen we:
# - Blueprint: een groep van pagina's (routes) die we later aan de app koppelen.
# - current_app: de Flask-app die op dit moment draait.
# - render_template: maakt een HTML-pagina uit een bestand in de map templates/.
# - request: alles wat de browser naar ons stuurt, bijvoorbeeld de ingevulde velden.
# - session: een klein geheugen per browser, zodat de website je naam onthoudt.
from flask import Blueprint, current_app, render_template, request, session

# Uit onze eigen map algorithm/ halen we de rekenfuncties:
# - CORRELATION_LIMITATION: een waarschuwingstekst die we op de pagina tonen.
# - PortfolioCommunity: bewaart alle gebruikers, ontgrendelingen en commentaren.
# - calculate_portfolio: berekent rendement, volatiliteit en Sharpe ratio.
# - optimal_weights: zoekt de verdeling met de hoogste Sharpe ratio.
from algorithm import CORRELATION_LIMITATION, PortfolioCommunity, calculate_portfolio, optimal_weights

# Een Blueprint groepeert routes. app.py koppelt deze groep aan Flask.
# "main" is de naam van de groep. __name__ is de naam van dit bestand; Flask
# gebruikt dat om te weten waar de code staat.
bp = Blueprint("main", __name__)


# "def" maakt een functie: een stuk code met een naam dat je later kunt oproepen.
# Deze functie geeft de community terug: de "databank in het geheugen" met alle gebruikers.
def get_community():
    # Bewaar één community per Flask-app, niet een nieuwe per webrequest.
    # current_app.extensions is een dictionary (een lijst van sleutel -> waarde)
    # waarin Flask dingen kan bewaren zolang de server draait.
    # Staat de community er nog niet in? Dan maken we ze nu één keer aan.
    if "portfolio_community" not in current_app.extensions:
        # __file__ is het pad van dit bestand (routes/main.py).
        # .parent gaat één map omhoog (naar routes/), nog eens .parent gaat
        # naar de projectmap zelf.
        project_folder = Path(__file__).resolve().parent.parent
        # Met / plak je een bestandsnaam achter een map: projectmap/test_data.json.
        data_file = project_folder / "test_data.json"
        # Lees het hele bestand in als tekst.
        text = data_file.read_text(encoding="utf-8")
        # Zet die tekst om naar Python-gegevens: een lijst met gebruikers.
        users = json.loads(text)
        # Maak een nieuwe community met die gebruikers en bewaar ze.
        current_app.extensions["portfolio_community"] = PortfolioCommunity(users)
    # Geef de (nieuwe of al bestaande) community terug aan wie deze functie oproept.
    return current_app.extensions["portfolio_community"]


# Dit is een "route": het koppelt een adres op de website aan een functie.
# "/" is de startpagina (http://127.0.0.1:5000/).
# GET = de browser vraagt gewoon de pagina op (bv. als je de website opent).
# POST = de browser stuurt ingevulde gegevens mee (bv. als je op een knop drukt).
@bp.route("/", methods=["GET", "POST"])
def home():
    # Haal de community op met alle gebruikers.
    community = get_community()

    # --- Beginwaarden ---
    # We geven eerst elke variabele een lege beginwaarde.
    # None betekent "nog niets". Later vullen we ze in als dat nodig is.
    # De resultaten van de berekening (rendement, volatiliteit, Sharpe ratio).
    result = None
    # De optimale weging, als die berekend kon worden.
    optimal = None
    # De foutmelding als de optimale weging niet berekend kon worden.
    optimal_error = None
    # De lijst met aandelen als getallen ([] is een lege lijst).
    stocks = []
    # Het totaal van alle ingevulde bedragen in euro.
    total_amount = 0
    # De foutmelding als er iets mis is met de invoer.
    error = None
    # De portefeuille van iemand anders die je hebt ontgrendeld.
    opened = None
    # De commentaren bij die portefeuille.
    comments = []
    # De naam van de eigenaar van de portefeuille die je wilt ontgrendelen.
    # request.form.get("owner", "") betekent: neem het veld "owner" uit het
    # formulier, en als het er niet is, neem dan "" (lege tekst).
    owner = request.form.get("owner", "")
    # rows zijn de rijen van het formulier, zoals de gebruiker ze typte (als tekst).
    # We beginnen met één lege rij, zodat er altijd minstens één aandeel te zien is.
    rows = [{"name": "", "return": "", "volatility": "", "amount": ""}]
    # De risk-free rate uit het formulier. Is die er niet, dan nemen we "2" (2%).
    rate = request.form.get("risk_free_rate", "2")
    # De gebruikersnaam die werd ingevuld om te publiceren.
    username = request.form.get("username", "")
    # De sessie onthoudt de actieve naam voor deze browser. Dit is geen login.
    # viewer is dus "wie kijkt er nu", of None als je nog niets publiceerde.
    viewer = session.get("portfolio_viewer")
    # 200 is de code voor "alles oké". Bij een fout veranderen we dit naar 400.
    status = 200

    # --- De gebruiker heeft op een knop gedrukt ---
    # Alleen bij POST (er werd een formulier verstuurd) moeten we iets doen.
    if request.method == "POST":
        # "try" betekent: probeer de code hieronder. Loopt er iets mis (een "fout"
        # of "exception"), dan springt Python meteen naar het "except"-deel onderaan.
        try:
            # Elke knop stuurt een veld "action" mee dat zegt welke knop het was:
            # "calculate", "publish", "unlock" of "comment".
            action = request.form.get("action", "calculate")

            # --- Knop "Berekenen" of "Berekenen en publiceren" ---
            if action in ("calculate", "publish"):
                # HTML herhaalt dezelfde veldnamen voor elke aandelenrij.
                # getlist haalt alle waarden van één veldnaam in rijvolgorde op.
                # Voorbeeld: bij twee aandelen geeft getlist("name") ["A", "B"].
                # field_names is een tuple: een lijst die je niet kunt veranderen.
                field_names = ("name", "return", "volatility", "amount")
                # fields wordt een dictionary: veldnaam -> lijst met alle waarden.
                fields = {}
                # Loop over elke veldnaam en haal alle waarden ervan op.
                for field_name in field_names:
                    fields[field_name] = request.form.getlist(field_name)

                # Het aantal aandelen = het aantal namen dat werd ingevuld.
                # len() geeft de lengte van een lijst.
                number_of_stocks = len(fields["name"])
                # Controle: elk veld moet evenveel waarden hebben als er namen zijn.
                # Anders ontbreekt er ergens iets.
                for field_name in field_names:
                    if len(fields[field_name]) != number_of_stocks:
                        # "raise" maakt zelf een fout aan. Python springt dan naar "except".
                        raise ValueError("De aandelenvelden zijn onvolledig.")

                # Nu zetten we de gegevens om naar één dictionary per aandeel.
                # Van {"name": ["A", "B"], ...} naar [{"name": "A", ...}, {"name": "B", ...}].
                rows = []
                # range(3) geeft 0, 1, 2: zo lopen we over elk aandeel.
                for index in range(number_of_stocks):
                    # Een lege dictionary voor dit ene aandeel.
                    row = {}
                    # Vul elk veld in met de waarde op plaats "index".
                    for field_name in field_names:
                        row[field_name] = fields[field_name][index]
                    # Voeg deze rij toe aan de lijst met rijen.
                    rows.append(row)

                # rows bewaart tekst voor het formulier; stocks bevat getallen.
                # De gebruiker voert 10 in voor 10%; de berekening gebruikt 0.10.
                stocks = []
                # In amounts komen de bedragen in euro, in dezelfde volgorde als stocks.
                amounts = []
                for row in rows:
                    # .strip() haalt spaties vooraan en achteraan weg: " A " wordt "A".
                    stock = {"name": row["name"].strip()}
                    # Rendement en volatiliteit zetten we om van tekst naar getal.
                    for field_name in ("return", "volatility"):
                        # Een Belg typt soms 10,5 in plaats van 10.5. Python kent
                        # alleen de punt, dus vervangen we de komma door een punt.
                        text = row[field_name].replace(",", ".")
                        # float() maakt van tekst een kommagetal. Delen door 100
                        # maakt van een percentage een fractie: 10 wordt 0.10.
                        # Lukt float() niet (bv. bij "abc"), dan ontstaat een ValueError.
                        stock[field_name] = float(text) / 100
                    # Voeg het aandeel toe aan de lijst.
                    stocks.append(stock)
                    # Het bedrag is in euro, dus daar delen we niet door 100.
                    amounts.append(float(row["amount"].replace(",", ".")))

                # De gebruiker voert bedragen in euro in; de berekening gebruikt gewichten.
                # Gewicht = bedrag van het aandeel / totaal bedrag, bv. 600 / 1000 = 0.60.
                # sum() telt alle getallen in een lijst op.
                total_amount = sum(amounts)
                # Is het totaal 0 of minder, dan kunnen we niet delen. Dat is een fout.
                if total_amount <= 0:
                    raise ValueError("Het totale bedrag moet groter dan 0 zijn")
                # Geef elk aandeel een gewicht: zijn bedrag gedeeld door het totaal.
                for index in range(len(stocks)):
                    stocks[index]["weight"] = amounts[index] / total_amount
                # Ook de risk-free rate gaat van percentage naar fractie: 2 wordt 0.02.
                risk_free_rate = float(rate.replace(",", ".")) / 100
                # Laat de rekenfunctie het rendement, de volatiliteit en de
                # Sharpe ratio berekenen. Klopt de invoer niet, dan geeft ze een fout.
                result = calculate_portfolio(stocks, risk_free_rate)
                # Lukt de optimale weging niet, dan tonen we toch het gewone resultaat.
                # Daarom staat hier een aparte try: een fout hier mag de rest niet stoppen.
                try:
                    optimal = optimal_weights(stocks, risk_free_rate)
                # "as exc" bewaart de fout in de variabele exc, zodat we de tekst kunnen tonen.
                except ValueError as exc:
                    # str() maakt van de fout een gewone tekst.
                    optimal_error = str(exc)
                # Werd op "Berekenen en publiceren" gedrukt? Dan zetten we de
                # portefeuille ook op het leaderboard.
                if action == "publish":
                    # Voeg de gebruiker toe aan de community. Bestaat de naam al,
                    # dan geeft add_user een fout.
                    community.add_user(username, stocks, risk_free_rate)
                    # Onthoud in de sessie wie deze browser gebruikt.
                    session["portfolio_viewer"] = username.strip()
                    # En gebruik die naam meteen ook voor deze pagina.
                    viewer = username.strip()

            # --- Knop "Ontgrendelen" of "Plaatsen" (commentaar) ---
            # "elif" betekent "anders, als ...": deze test gebeurt alleen als de
            # vorige "if" niet waar was.
            elif action in ("unlock", "comment"):
                # Wie nog niets publiceerde, heeft geen naam en mag dit niet.
                # "not viewer" is waar als viewer None of leeg is.
                if not viewer:
                    raise ValueError("Publiceer eerst een portefeuille met een unieke gebruikersnaam.")
                if action == "unlock":
                    # Simulatie: hier wordt geen echte betaling gecontroleerd.
                    # We "betalen" gewoon 5 euro voor de portefeuille van owner.
                    community.unlock_portfolio(viewer, owner, 5)
                # "else" betekent "in alle andere gevallen": hier is dat "comment".
                else:
                    # Plaats het commentaar uit het tekstvak "message".
                    community.add_comment(viewer, owner, request.form.get("message", ""))
                # Haal de ontgrendelde portefeuille op om ze te tonen.
                opened = community.get_portfolio(viewer, owner)
                # Haal ook alle commentaren bij die portefeuille op.
                comments = community.get_comments(viewer, owner)

            # --- Een onbekende knop ---
            # Kan normaal niet gebeuren, maar zo zijn we zeker.
            else:
                raise ValueError("Onbekende actie.")

        # Hier komen we als er hierboven ergens een fout ontstond.
        # ValueError: een ongeldige waarde (bv. tekst in plaats van een getal).
        # PermissionError: iets wat niet mag (bv. commentaar zonder te ontgrendelen).
        # OverflowError: een getal dat te groot is om mee te rekenen.
        except (ValueError, PermissionError, OverflowError) as exc:
            # Een f-string (f"...") laat je variabelen tussen { } in een tekst zetten.
            # De foutmelding wordt bovenaan de pagina getoond.
            error = f"Controleer je invoer: {exc}. Bedragen mogen niet negatief zijn; gebruik geldige getallen en een positieve portefeuillevolatiliteit."
            # 400 is de code voor "de invoer van de gebruiker klopt niet".
            status = 400

    # --- De pagina terugsturen ---
    # render_template maakt de HTML-pagina uit templates/index.html.
    # Alles na de bestandsnaam (rows=rows, ...) zijn de gegevens die de pagina
    # mag gebruiken. Links van = staat de naam in de HTML, rechts de variabele hier.
    # ranking=community.leaderboard() geeft de lijst van het leaderboard mee.
    # Na de komma op het einde sturen we ook de statuscode mee (200 of 400).
    return render_template("index.html", rows=rows, rate=rate, username=username,
                           result=result, optimal=optimal, optimal_error=optimal_error,
                           stocks=stocks, total_amount=total_amount, error=error, limitation=CORRELATION_LIMITATION,
                           ranking=community.leaderboard(), viewer=viewer,
                           opened=opened, comments=comments), status

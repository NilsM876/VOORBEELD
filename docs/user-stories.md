# User stories

The final version of your user stories, as they stand at the deadline.
During the sprints they live on your board as issues; copy them here at the end.

Most important first.

## Must have

### 1. Portefeuille invoeren
Als belegger wil ik aandelen (tickers) en mijn bedrag of aantal per aandeel invoeren, zodat mijn portefeuille in de applicatie staat.

Acceptance criteria:
- Ik kan meerdere aandelen toevoegen en verwijderen, elk met een ticker en een bedrag of aantal.
- Lege of ongeldige invoer wordt geweigerd met een duidelijke foutmelding.

### 2. Rendement en volatiliteit zien
Als belegger wil ik het gemiddelde rendement en de volatiliteit van mijn portefeuille zien, zodat ik begrijp hoeveel risico ik loop voor mijn rendement.

Acceptance criteria:
- Na het berekenen zie ik het rendement, de volatiliteit en de Sharpe ratio van mijn portefeuille.
- Rendement en volatiliteit worden als percentage getoond.

### 3. Optimale weging vergelijken
Als belegger wil ik in een tabel de optimale weging (hoogste Sharpe ratio) naast mijn huidige weging zien, zodat ik weet hoe ik mijn portefeuille moet herverdelen.

Acceptance criteria:
- De tabel toont per aandeel mijn huidige gewicht en het optimale gewicht.
- De Sharpe ratio van de optimale weging is minstens even hoog als die van mijn huidige weging.

### 4. Publiceren op het leaderboard
Als belegger wil ik mijn Sharpe ratio onder mijn gebruikersnaam op het leaderboard zetten, zodat ik me kan vergelijken met andere beleggers.

Acceptance criteria:
- Na het publiceren staat mijn gebruikersnaam met mijn Sharpe ratio op het leaderboard.
- Een gebruikersnaam die al bestaat, wordt geweigerd.

### 5. Leaderboard bekijken
Als bezoeker wil ik onderaan de website een leaderboard zien met de hoogste Sharpe ratio bovenaan, zodat ik meteen zie wie de best presterende beleggers zijn.

Acceptance criteria:
- Het leaderboard is zichtbaar zonder dat ik zelf iets publiceer.
- Het leaderboard is gesorteerd van hoogste naar laagste Sharpe ratio.

## Should have

### 6. Paywall
Als app-operator wil ik dat gebruikers via een paywall moeten betalen voordat ze de portefeuille van een ander kunnen bekijken, zodat de applicatie inkomsten genereert en lucratief wordt.

Acceptance criteria:
- De portefeuille van een ander is pas zichtbaar na een (gesimuleerde) betaling van €5.
- Een portefeuille die ik al ontgrendeld heb, kan ik gratis opnieuw bekijken.

### 7. Portefeuille bekijken en commentaar geven
Als betalende gebruiker wil ik na de paywall de volledige portefeuille van een andere gebruiker zien en er commentaar bij plaatsen, zodat ik kan leren van hun keuzes en erover kan discussiëren.

Acceptance criteria:
- Na het ontgrendelen zie ik alle aandelen met hun gewicht.
- Ik kan commentaar plaatsen en zie het commentaar van andere gebruikers.
- Lege commentaren worden geweigerd.

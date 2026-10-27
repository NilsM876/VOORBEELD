# Sharply

Sharply lets you build a stock portfolio, calculates its Sharpe ratio and ranks it on a leaderboard against other users. For anyone who invests.

**Group:** PR2627-25  
**Client:** none, we test with fellow students

## Team

Everyone adds their own line, in their own commit.

| Name | GitHub account | Works on |
|---|---|---|
| Nils Matthijs | NilsM876 | website |
| Alexander Smet | AlexanderSmet | website |
| Stef Hoegaerts | stefhoegaerts | website | 
| Brent Vandevyvere | Brenttt-code | website |
| Senne Van Vaerenberg | sennevanvae | website |

## Install and run

You need Python, set up as on 23 September, and your group's database details from Ufora.

```
git clone <the URL of this repository>
cd <this folder>
```

| What | macOS, Linux | Windows |
|---|---|---|
| Make the environment | `python3 -m venv venv` | `py -m venv venv` |
| Activate it | `source venv/bin/activate` | `venv\Scripts\activate` |
| Install | `pip install -r requirements.txt` | `pip install -r requirements.txt` |

Then copy `.env.example` to `.env`, fill in the database details, and check the connection:

```
python check_db.py
```

The first time, run `database/ddl.sql` against your group database (from the client you
use for Database Systems), then put the test persons in it and start the website:

```
python seed_db.py
flask --app app run --debug
```

Open http://127.0.0.1:5000.

## Links

- User interface prototype: 
- Board: 
- Anything else we want you to see: 

## Contribution table

Per part of the application, who wrote it. The commit history has to agree with this table.

| Part | Written by |
|---|---|
| routes/... | |
| templates/... | |
| models.py | |
| database/ddl.sql | |
| Algorithm: ... | |

## What the repository contains by 18 December

- [ ] The Flask application
- [ ] The DDL for your tables, in `database/ddl.sql`
- [ ] Screenshots or images of the user interface prototype, in `docs/prototype/`
- [ ] The final version of the user stories, in `docs/user-stories.md`
- [ ] A database dump (mysqldump), in `database/dump.sql`
- [ ] This README: how to install and run, the links, the contribution table
- [ ] The peer review, submitted by each of you on Ufora

## Project structure

```
app.py              creates the application and registers the routes
config.py           reads .env
models.py           one class per table
routes/             one file per part of the application
templates/          base.html and one template per page
static/css/         your own styles, on top of Bootstrap
static/js/          adds stock rows and recalculates while you type
algorithm/          the core logic of your algorithm, without Flask
database/           ddl.sql and, at the end, dump.sql
docs/               user stories, prototype screenshots, code-uitleg.md
tests/              automatic tests (python -m unittest discover -s tests -v)
main.py             the algorithm in the terminal, on test_data.json
test_data.json      fictional test persons
seed_db.py          puts the test persons in the database
check_db.py         tests the database connection on its own
.env.example        what your .env looks like, without the passwords
```

juomabot
========

:cocktail: Slack-based office drink tracker

Configuration
-------------

Juomabot is configured via environment variables.

* Use `DATABASE_URL` to declare a SQLAlchemy database URL for `dataset` to use
* Use `ADMIN_PASSWORD` to set the admin password required for administrative commands (the default is `hackme`)

Setup
-----

* Have the `juomabot.wsgi` WSGI application running on a server however you like.
  For the sake of example, let's say it's running on `http://juoma.example.com/`
* Create a new slash command integration in Slack and point it to `http://juoma.example.com/slack`.
  For the sake of example, let's say the command is `/juoma` and the admin password is still `hackme`.
* Set up a selection of drinks with the admin commands:
  * Add a drink: `/juoma -p hackme -a --price 10 Coca-Cola`
  * Set a drink's price: `/juoma -p hackme -e --price 15 Coca-Cola`
  * Toggle a drink's availability: `/juoma -p hackme -t Coca-Cola`
  
Billing
-------

* Use `--billing-stats` to get a CSV report of unbilled drinks.
* Save the CSV and send it over to whoever is responsible for billing the drinks.
* Invoke the `--bill somehashhere` command in the billing-stats response.
* You're done! Until next time, that is. (If you rerun `--billing-stats`, it should now come up as empty.)

Development
-----------

* Use `py.test --cov .` to run tests.
* Use `python runserver.py` and ngrok or something similar to test the slash command in Slack.

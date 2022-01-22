# Tsoha-keskustelu
Tämä repositorio sisältää yksinkertaisen keskustelupalstasivuston. Sivustolla on keskusteluaiheita, joiden sisälle voi luoda keskusteluketjuja, joihin voi lähettää viestejä. Viesteissä voi olla mukana liitetiedostoja. Sivustolle on kirjauduttava, jotta voi luoda keskusteluketjuja ja lähettää viestejä. Käyttäjä voi poistaa itse lähettämiään viestejä ja ylläpitäjät voivat poistaa kaikkien viestejä, keskusteluketjuja sekä keskusteluaiheita.

Sovellusta voi kokeilla [Heroku-palvelussa](https://glacial-retreat-70819.herokuapp.com/).


## Asennus
Olettaen että sinulla on asennettuna Python ja PostgreSQL, voit asentaa sovelluksen komennoilla:
`pip install poetry`
`poetry install`

Ennen sovelluksen suorittamista sinun on luotava tiedosto nimeltä `.env`, jonka sisältö on muotoa:

    FLASK_APP=src/app.py
    DATABASE_URL=<url>
    SECRET_KEY=<avain>

Missä <url> on PostgreSQL tietokannan osoite ja <avain> on jokin satunnainen merkkijono.

Sinun täytyy myös luoda PostgreSQL tietokantaan tarvittavat taulut komennolla `psql < schema.sql`

Sovelluksen voi tämän jälkeen suorittaa paikallisesti komennolla:
`poetry run flask run`



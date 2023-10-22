# Opetussovellus

Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

## Sovelluksen ominaisuudet
### Perusominaisuudet:
* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Opiskelija näkee listan kursseista ja voi liittyä kurssille.
* Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
* Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
* Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
* Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla monivalinta tai esseetehtävä.
* Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

### Muita ominaisuuksia:
* Opiskelija saa ratkomistaan kurssien tehtävistä arvosanan
    * Opettaja arvioi esseetehtävät
    * Monivalintatehtävät arvioidaan automaattisesti
* Opettaja pystyy katsomaan ja arvioimaan opiskelijoiden vastauksia
* Opettaja näkee opiskelijoiden tehtävistä saamat pisteet
* Kursseja voi hakea nimen ja kuvauksen mukaan. Kurssihakua voi myös rajata käyttäjän omiin kursseihin sekä kursseihin joihin käyttäjä on osallistunut.

## Sovelluksen tilanne
Kaikki yllä mainitut sovelluksen ominaisuudet on toteutettu.

## Sovelluksen testaaminen
1. Luo sovellusta varten uusi tietokanta psql-tulkissa:
    ```sql
    CREATE DATABASE tsoha_opetussovellus;
    ```
2. Kloonaa sovellus:
    ```shell
    git clone "https://github.com/0442/tsoha-opetussovellus"
    cd tsoha-opetussovellus
    ```
3. Luo tiedosto `.env` ja määrittele tiedostoon ympäristömuuttujat `DATABASE_URL` ja `SECRET_KEY`:
    ```.env
    DATABASE_URL=postgresql:///tsoha_opetussovellus
    SECRET_KEY=some_secure_secret_key
    ```
4. Luo tarvittavat tietokantataulut:
    ```shell
    psql -d tsoha_opetussovellus < schema.sql
    ```
5. Luo sovellukselle virtuaaliympäristö ja asenna riippuvuudet:
    ```shell
    python3 -m venv venv
    source venv/bin/activate
    pip install -r requirements.txt
    ```

6. Uudelleenaktivoi virtuaaliympäristö:
    ```shell
    deactivate
    source venv/bin/activate
    ```

7. Käynnistä sovelluksen backend:
    ```shell
    cd app
    flask run
    ```

8. Avaa sovellus menemällä osoitteeseen <http://localhost:5000>

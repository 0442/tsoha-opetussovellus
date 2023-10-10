# Opetussovellus

Sovelluksen avulla voidaan järjestää verkkokursseja, joissa on tekstimateriaalia ja automaattisesti tarkastettavia tehtäviä. Jokainen käyttäjä on opettaja tai opiskelija.

Sovelluksen ominaisuuksia:

* Käyttäjä voi kirjautua sisään ja ulos sekä luoda uuden tunnuksen.
* Opiskelija näkee listan kursseista ja voi liittyä kurssille.
* Opiskelija voi lukea kurssin tekstimateriaalia sekä ratkoa kurssin tehtäviä.
* Opiskelija pystyy näkemään tilaston, mitkä kurssin tehtävät hän on ratkonut.
* Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
* Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä voi olla ainakin monivalinta tai tekstikenttä, johon tulee kirjoittaa oikea vastaus.
* Opettaja pystyy näkemään kurssistaan tilaston, keitä opiskelijoita on kurssilla ja mitkä kurssin tehtävät kukin on ratkonut.

## Sovelluksen testaaminen
1. Luo sovellusta varten uusi tietokanta psql-tulkissa: <code>CREATE DATABASE tsoha_opetussovellus</code>
1. Kloonaa sovellus: <code>$ git clone https://github.com/0442/tsoha-opetussovellus</code>
1. Luo tiedosto <code>.env</code> ja määrittele tiedostoon ympäristömuuttujat <code>DATABASE_URL</code>  ja <code>SECRET_KEY</code>. <code>DATABASE_URL</code> on muotoa <code>postgresql:///tsoha_opetussovellus</code>
1. Luo tarvittavat tietokantataulut: <code>$ psql -d tsoha_opetussovellus < schema.sql</code>
1. Luo sovelluksen kansioon virtuaaliympäristö: <code>$ python3 -m venv venv</code>
1. Ota virtuaaliympäristö käyttöön: <code>$ source venv/bin/activate</code>
1. Asenna riippuvuudet: <code>$ pip install -r requirements.txt</code>
1. Restarttaa virtuaaliympäristö <code>$ deactivate && source venv/bin/activate</code>
1. Käynnistä sovelluksen backend: <code>$ flask run</code>
1. Mene osoitteeseen localhost:5000

## Sovelluksen nykytilanne
### Mitä on jo toteutettu:
- Käyttäjä voi kirjautu sisään, ulos, luoda uuden tunnuksen (opiskelija tai opettaja), sekä poistaa omat tunnuksensa.
- Opiskelija näkee listan luoduista kursseista ja voi liittyä kursseille.
- Opiskelija voi lukea kurssin tekstimateriaalia.
- Opettaja pystyy luomaan uuden kurssin, muuttamaan olemassa olevaa kurssia ja poistamaan kurssin.
- Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä on tekstikenttä, johon tulee kirjoittaa oikea vastaus.
- Opetaaja pystyy lisäämään kurssille monivalintatehtäviä.
- Opettaja näkee listan opiskelijoiden ratkaisemista tehtävistä.
- Opiskelijan lähettämät monivalintatehtävien vastaukset tarkastetaan.
- Opiskelija voi katsoa mitä tehtäviä hän on suorittanut, sekä suoritettujen tehtävien omat ja oikeat vastaukset.

### Mitä ei ole vielä toteutettu:
- Opettaja ei pysty näkemään listaa kurssin osallistujista

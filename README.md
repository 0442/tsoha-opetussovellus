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
1. Kloonaa sovellus: <code>$ git clone https://github.com/0442/tsoha-opetussovellus</code>
2. Luo tiedosto <code>.env</code> ja määrittele tiedostoon ympäristömuuttujat DATABASE_URL ja SECRET_KEY.
3. Luo tarvittavat tietokantataulut: <code>$ psql < schema.sql</code>
4. Luo sovelluksen kansioon virtuaaliympäristö: <code>$ python3 -m venv venv</code>
5. Ota virtuaaliympäristö käyttöön: <code>$ source venv/bin/activate</code>
6. Asenna riippuvuudet: <code>$ pip install -r requirements.txt</code>
7. Restarttaa virtuaaliympäristö <code>$ deactivate && source venv/bin/activate</code>
8. Käynnistä sovelluksen backend: <code>$ flask run</code>
9. Mene osoitteeseen <a>localhost:5000</a>

## Sovelluksen nykytilanne
### Mitä on jo toteutettu:
- Käyttäjä voi kirjautu sisään, ulos, luoda uuden tunnuksen (opiskelija tai opettaja), sekä poistaa omat tunnuksensa.
- Opiskelija näkee listan luoduista kursseista ja voi liittyä kursseille.
- Opiskelija voi lukea kurssin tekstimateriaalia.
- Opettaja pystyy luomaan uuden kurssin ja muuttamaan omaa olemassa olevaa kurssia.
- Opettaja pystyy lisäämään kurssille tekstimateriaalia ja tehtäviä. Tehtävä on tekstikenttä, johon tulee kirjoittaa oikea vastaus.

### Mitä ei ole vielä toteutettu:
- Salasanojen tallentaminen hajautusarvoina.
- Opiskelijan lähettämiä vastauksia ei tallenneta eikä tarkasteta. Opiskelija ei siis voi vielä ratkoa kurssin tehtäviä.
- Opiskelija ei pysty näkemään mitään kurssitilastoja.
- Opettaja ei voi poistaa kurssia.
- Opetaaja ei pysty lisäämään kurssille monivalintatehtäviä
- Opettaja ei voi nähdä kurssistaan mitään tilastoja.

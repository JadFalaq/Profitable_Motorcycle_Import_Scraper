# Web Scrapping des Motos Rentables

Ce projet automatise le scraping de motocyclettes disponibles à la vente au Maroc et analyse leur rentabilité.

## Fonctionnalités

- **Scraping LeParking Moto**: Récupère les annonces de motos avec prix et kilométrage
- **Calcul de la valeur taxable**: Utilise l'API douanière marocaine pour obtenir les valeurs taxables
- **Analyse Avito**: Scrape les prix moyens sur Avito pour comparaison
- **Analyse de rentabilité**: Calcule les marges et pourcentages de rentabilité
- **Visualisation**: Crée des graphiques candlestick pour visualiser les marges

## Prérequis

- Python 3.x
- Selenium WebDriver
- ChromeDriver
- Pandas, Matplotlib, NumPy

## Installation

```bash
pip install selenium pandas matplotlib numpy tqdm
```

Téléchargez ChromeDriver depuis: https://chromedriver.chromium.org/

## Utilisation

```bash
python import_moto.py
```

Vous serez invité à entrer:

- La marque de la moto (ex: yamaha)
- Le modèle de la moto (ex: mt 07)
- Le nombre de pages à scraper
- Le pays souhaité

## Résultats

Le script génère:

- `resultats_motos_[marque-modele].csv`: Résultats du scraping LeParking
- `resultats_avec_prix_maroc.csv`: Résultats finaux avec prix Avito et marges
- `marge_candlestick_annonces.png`: Graphique de visualisation des marges

## Auteur

Jad Falaq

## License

MIT

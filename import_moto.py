from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import pandas as pd
import time
import re
import datetime
from datetime import datetime as dt
from tqdm import tqdm
from difflib import get_close_matches
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
import traceback
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from datetime import date, timedelta



# ==== CONFIGURATION SELENIUM ====
options = Options()
options.add_argument("--window-sizenk-features=AutomationControlled")
options.add_argument("--ignore-certificate-errors")
options.add_argument("--ignore-ssl-errors")
options.add_argument("--allow-insecure-localhost")
options.add_argument("--allow-running-insecure-content")
options.add_argument("--disable-web-security")
options.add_argument("--no-sandbox")
options.add_argument("--disable-dev-shm-usage")
options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/135.0.0.0 Safari/537.36")
options.add_experimental_option("prefs", {
    "profile.default_content_setting_values.geolocation": 2
})

df_modeles = pd.read_csv("C:/Users/falaq/OneDrive/Desktop/Jad Falaq/ENSIAS 1A/tutp/tous_les_modeles.csv")

def normalize(text):
    return re.sub(r"[^\w]", "", text.lower())

def trouver_modele_proche(modele_scrape, marque_scrape, df_modeles):
    modele_norm = normalize(modele_scrape)
    subset = df_modeles[df_modeles["Marque"].str.lower() == marque_scrape.lower()]
    modeles_dispo = subset["Modèle"].dropna().unique()

    # Correspondance manuelle partielle
    for modele in modeles_dispo:
        if normalize(modele_norm) in normalize(modele):
            return modele
        if normalize(modele) in normalize(modele_norm):
            return modele

    return None

def get_valeur_taxable_total(marque, modele, date_str):
    # === CONFIGURATION ===
    service = Service(r"C:\chromedriver-win64\chromedriver.exe")
    options = Options()
    options.add_argument("--start-maximized")
    driver = webdriver.Chrome(service=service, options=options)
    wait = WebDriverWait(driver, 15)

    try:
        jour, mois, annee = date_str.split("/")
        mois_map = {
            "01": "JANV.", "02": "FÉVR.", "03": "MARS", "04": "AVR.", "05": "MAI",
            "06": "JUIN", "07": "JUIL.", "08": "AOÛT", "09": "SEPT.",
            "10": "OCT.", "11": "NOV.", "12": "DÉC."
        }
        mois_nom = mois_map[mois]

        driver.get("https://www2.douane.gov.ma/mcv/#/view?pageId=2")
        time.sleep(2)

        # Clic sur "Calcul des droits"
        onglets = wait.until(EC.presence_of_all_elements_located(
            (By.CSS_SELECTOR, "div.b-detail__main-info-characteristics-one.calculator"))
        )
        for onglet in onglets:
            if "CALCUL DES DROITS" in onglet.text.upper():
                driver.execute_script("arguments[0].click();", onglet)
                break
        time.sleep(1.5)

        # Clic sur "Motocycle"
        moto_svg = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "label[for='type1']")))
        driver.execute_script("arguments[0].click();", moto_svg)
        time.sleep(1.5)

        # Sélection de la marque
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='marque']"))).click()
        time.sleep(1)
        marques = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "mat-option span")))
        for m in marques:
            if m.text.strip().upper() == marque.upper():
                m.click()
                break
        time.sleep(1)

        # Sélection du modèle
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='modele']"))).click()
        time.sleep(1)
        modeles = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "mat-option span")))
        for mod in modeles:
            if modele.lower() in mod.text.strip().lower():
                mod.click()
                break
        time.sleep(1)

        # Calendrier
        # 6. Ouvrir le calendrier
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[aria-label='Open calendar']"))).click()
        time.sleep(1)

        # 7. Aller à la sélection de l’année
        wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mat-calendar-period-button"))).click()
        time.sleep(1)

        # 8. Naviguer si nécessaire et cliquer sur l’année
        while True:
            try:
                xpath_annee = f"//span[text()=' {annee} ' or text()='{annee}']"
                annee_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_annee)))
                driver.execute_script("arguments[0].click();", annee_element)
                break
            except:
                prev = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button.mat-calendar-previous-button")))
                prev.click()
                time.sleep(0.5)

        # 9. Cliquer sur le mois

        while True:
                xpath_mois = f"//span[text()=' {mois_nom} ' or text()='{mois_nom}']"
                mois_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_mois)))
                driver.execute_script("arguments[0].click();", mois_element)
                break

        while True:
            xpath_jour = f"//span[text()=' {jour} ' or text()='{jour}']"
            jour_element = wait.until(EC.element_to_be_clickable((By.XPATH, xpath_jour)))
            driver.execute_script("arguments[0].click();", jour_element)
            break


        # Clic sur Valider
        valider_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit'].m-btn-next")))
        driver.execute_script("arguments[0].click();", valider_btn)
        time.sleep(2)

        # Extraction de la valeur
        elements = driver.find_elements(By.CSS_SELECTOR, "div.b-compare__block-inside-value")
        montant = None
        for el in reversed(elements):
            texte = el.text.strip()
            if "DH" in texte:
                montant_str = re.sub(r"[^\d]", "", texte)
                if montant_str:
                    montant = int(montant_str)
                    break

        return montant

    except Exception as e:
        print(" Erreur :", repr(e))
        traceback.print_exc()
        return None

    finally:
        time.sleep(3)
        driver.quit()


# ==== CHROME DRIVER ====
service = Service(r"C:\chromedriver-win64\chromedriver.exe")
driver = webdriver.Chrome(service=service, options=options)

# ==== DEMANDER LA MOTO ET PAGES ====
marque = input("Entrez la marque de la moto (ex: yamaha) : ").strip().lower()
modele = input("Entrez le modèle de la moto (ex: mt 07) : ").strip().lower()
moto = marque +" "+ modele 
moto_url = moto.replace(" ", "-")
nb_pages = int(input("Combien de pages veux-tu scraper ? : "))

pays=input("Entrer le pays voulue :").strip().lower()

url = f"https://www.leparking-moto.ma/moto-occasion/{pays}/{moto_url}.html"
print(f"Navigation vers : {url}")

driver.get(url)
time.sleep(3)


data = []
page_count = 0

# ==== DATE LIMITE (aujourd'hui - 5 ans) ====
date_limite = datetime.date.today() - datetime.timedelta(days=5*365)

# ==== SCRAPER ====
while page_count < nb_pages:
    try:
        annonces = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "li.li-result"))
        )

        for annonce in tqdm(annonces, desc =f"Scraping page {page_count + 1}/{nb_pages}"):
            try:
                # === PRIX ===
                prix_elements = annonce.find_elements(By.CSS_SELECTOR, "div.price-block p.prix")
                prix_brut = None
                for prix_element in prix_elements:
                    texte = prix_element.text.strip()
                    if texte:
                        prix_brut = texte
                        break

                if not prix_brut:
                    continue

                prix_nettoye = re.sub(r"[^\d]", "", prix_brut)
                if prix_nettoye:
                    prix_num = int(prix_nettoye)
                else:
                    continue

                # === TITRE ===
                try:
                    modele_ = annonce.find_element(By.CSS_SELECTOR, "span.sub-title.title-block span.nowrap.title-block").text.strip()
                    modele__= trouver_modele_proche(modele_,marque.upper(), df_modeles)
                    titre = f"{marque} {modele_}"
                except:
                     titre = "Non précisé"

                # === LIEN ===
                try:
                    lien = annonce.find_element(By.CSS_SELECTOR, "a.external.btn-plus").get_attribute("href")
                    if lien.startswith("/"):
                        lien = "https://www.leparking-moto.fr" + lien
                except:
                    lien = "Non précisé"

                # === KILOMÉTRAGE ET ANNÉE ===
                kilometre = None
                annee_moto = None
                try:
                    infos = annonce.find_elements(By.CSS_SELECTOR, "div.upper")
                    for info in infos:
                        txt = info.text.lower()
                        if "km" in txt:
                            kilometre = int(re.sub(r"[^\d]", "", txt))
                        elif txt.isdigit() and len(txt) == 4:
                            annee_moto = int(txt)
                except:
                    pass

                if not annee_moto:
                    continue

                # === LIEU ===
                try:
                    lieu = annonce.find_element(By.CSS_SELECTOR, "div.location span.upper").text.strip()
                    if lieu != pays.upper():
                        continue
                except:
                    lieu = "Non précisé"

                # === DATE DE PUBLICATION (Jour et Mois) ===
                try:
                    date_publi_text = annonce.find_element(By.CSS_SELECTOR, "p.btn-publication").text.strip()
                    jour_publi, mois_publi = map(int, date_publi_text.split('/')[:2])
                except:
                    continue 

                # === CONSTRUIRE DATE COMPLETE ===
                try:
                    date_complete = datetime.date(annee_moto, mois_publi, jour_publi)
                except:
                    continue  

                # === FILTRE : vérifier si la date complète est récente ===
                if date_complete < date_limite:
                    continue
                date_circulation = date_complete.strftime("%d/%m/%Y")
                
                try:
                    valeur_taxable = get_valeur_taxable_total(marque, modele__, date_circulation)
                    if valeur_taxable is None:
                        continue  
                except Exception as e:
                    print(f"Erreur lors de l'obtention de la valeur taxable : {e}")
                    continue
                # === Ajouter dans la liste ===


                data.append({
                    "Titre": titre,
                    "Kilométrage (km)": kilometre,
                    "Lieu": lieu,
                    "Lien": lien,
                    "Date complète (jour/mois/année)": date_circulation,
                    "Prix (DH)": prix_num,
                    "Valeur taxable": valeur_taxable ,
                    "Prix brut": valeur_taxable + prix_num + 500,

                })

            except Exception as e:
                print(f"Erreur sur une annonce : {e}")

        # ==== PAGE SUIVANTE ====
        try:
            next_button = driver.find_element(By.CSS_SELECTOR, "li.btn-next a")
            driver.execute_script("arguments[0].click();", next_button)
            time.sleep(3)
            page_count += 1
        except Exception as e:
            print("Pas de bouton suivant ou clic impossible :", e)
            break


    except Exception as e:
        print(f"Erreur pendant le scraping : {e}")
        break

for d in data:
    d["Lien"] = d["Lien"].strip().lower()  # Enlever espaces et normaliser


# Supprimer les doublons basés sur le lien
df = pd.DataFrame(data)
df.drop_duplicates(subset="Lien", inplace=True)



# ==== SAUVEGARDER ====
df = pd.DataFrame(data)
df.to_csv(f"resultats_motos_{moto_url}.csv", index=False, encoding='utf-8')
print(f"Scraping terminé. {len(df)} annonces sauvegardées dans resultats_motos_{moto_url}.csv")

driver.quit()



driver = webdriver.Chrome(service=service, options=options)

def scraper_prix_avito(modele, annee):
    """Scrape les prix des motos du modèle et année donnés sur Avito Maroc"""
    url = f"https://www.avito.ma/fr/maroc/motos/{modele.lower().replace(' ','_')}--%C3%A0_vendre?regdate={annee}-{annee}"
    print(f"URL: {url}")
    driver.get(url)
    
    prix_list = []
    
    try:
        # Accepter les cookies si popup
        try:
            cookie_btn = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.XPATH, "//button[contains(., 'Accepter') or contains(., 'J\'accepte')]"))
            )
            cookie_btn.click()
            print("Cookies acceptés")
            time.sleep(1)
        except:
            print("Pas de popup cookies")
            pass
        
        # Vérifier s'il y a des annonces
        no_results = driver.find_elements(By.XPATH, "//*[contains(text(), 'Aucun résultat') or contains(text(), 'aucune annonce')]")
        if no_results:
            print("Aucune annonce disponible pour cette recherche")
            return None, 0
        
        # Attente que les annonces soient chargées
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, "div.sc-b57yxx-1.eGVXZM"))
        )
        
        # Récupérer les annonces
        annonces = driver.find_elements(By.CSS_SELECTOR, 'div.sc-b57yxx-1.eGVXZM')
        print(f"Nombre d'annonces trouvées: {len(annonces)}")
        
        for annonce in annonces[:min(10, len(annonces))]:
            try:
                prix_element = annonce.find_element(By.CSS_SELECTOR, "div.sc-b57yxx-4.jouDTq p.sc-1x0vz2r-0 span[dir='auto']")
                prix_text = prix_element.text
                prix_nettoye = re.sub(r"[^\d]", "", prix_text)
                prix = int(prix_nettoye)
                print(f"Prix trouvé : {prix}")
                
                # Filtrage des prix hors plage acceptable
                if prix < 10000 or prix > 200000:
                    print(f"Annonce rejetée (prix {prix} DH hors plage autorisée)")
                    continue
                
                prix_list.append(prix)
            except NoSuchElementException:
                print("Élément prix non trouvé dans une annonce")
                continue
            except Exception as e:
                print(f"Erreur extraction prix : {e}")
                continue

    except Exception as e:
        print(f"Erreur lors du scraping : {e}")
        return None, 0
    
    if prix_list:
        avg_price = sum(prix_list) / len(prix_list)
        return avg_price + 10000, len(prix_list)
    else:
        return None, 0

# Chargement du CSV des motos extraites précédemment
df = pd.read_csv("resultats_motos_{moto_url}.csv")

# Préparation des colonnes pour le prix moyen et nombre d'annonces
df['Prix Moyen Maroc'] = None
df['Nombre Annonces'] = 0
annee_courante = dt.now().year

for index, row in df.iterrows():
    try:
        date_str = row['Date complète (jour/mois/année)']
        annee = dt.strptime(date_str, '%d/%m/%Y').year
        
        if annee > annee_courante:
            print(f"Année {annee} dans le futur - passage à la suivante")
            continue
        
        titre = row['Titre']  # Exemple : "yamaha MT 09"

        # Suppression de la marque au début du titre (insensible à la casse)
        modele = titre.lower().replace(marque.lower(), "", 1).strip()
        
        # Vérifier si prix moyen déjà calculé pour ce modèle+année
        existing_rows = df[(df['Titre'] == row['Titre']) & (df['Date complète (jour/mois/année)'].str.contains(str(annee)))]
        existing = existing_rows['Prix Moyen Maroc']
        if existing.notnull().any():
            prix_moyen = existing.dropna().iloc[0]
            nb_annonces = existing_rows['Nombre Annonces'].iloc[0]
            print(f"Réutilisation du prix moyen calculé : {prix_moyen} DH pour {modele} {annee}")
        else:
            print(f"Scraping pour {modele} {annee}...")
            prix_moyen, nb_annonces = scraper_prix_avito(modele, annee)
        
        if prix_moyen:
            df.at[index, 'Prix Moyen Maroc'] = prix_moyen
            df.at[index, 'Nombre Annonces'] = nb_annonces
            print(f"Prix moyen : {prix_moyen:.2f} DH | Annonces : {nb_annonces}")
        else:
            print(f"Aucun prix trouvé pour {modele} {annee}")
            
    except Exception as e:
        print(f"Erreur ligne {index} : {e}")
        continue

driver.quit()

# Calcul de la marge et rentabilité pour les lignes avec prix moyen
valid_rows_index = df['Prix Moyen Maroc'].notna()
df.loc[:, 'Prix d\'achat avec frais'] = df.loc[:, 'Prix (DH)'] + df.loc[:, 'Valeur taxable']
df.loc[valid_rows_index, 'Marge'] = df.loc[valid_rows_index, 'Prix Moyen Maroc'] - (df.loc[valid_rows_index, 'Prix (DH)'] + df.loc[valid_rows_index, 'Valeur taxable'])
df.loc[valid_rows_index, 'Rentabilité %'] = (df.loc[valid_rows_index, 'Marge'] / (df.loc[valid_rows_index, 'Prix (DH)'] + df.loc[valid_rows_index, 'Valeur taxable'])) * 100

# Sauvegarde finale
df.to_csv("resultats_avec_prix_maroc.csv", index=False)

# Résumé statistique
if 'Prix Moyen Maroc' in df.columns and df['Prix Moyen Maroc'].notna().any():
    print("\nRésumé statistique :")
    print(f"- Prix moyen au Maroc : {df['Prix Moyen Maroc'].mean():.2f} DH")
    print(f"- Marge moyenne : {df['Marge'].mean():.2f} DH")
    print(f"- Rentabilité moyenne : {df['Rentabilité %'].mean():.2f} %")
else:
    print("\n Aucune donnée de prix disponible pour calculer les statistiques")

print("\n Données sauvegardées dans resultats_avec_prix_maroc.csv")

df = pd.read_csv("resultats_avec_prix_maroc.csv")

# Calculer la marge brute si pas déjà présente
if 'Marge' not in df.columns or df['Marge'].isnull().all():
    df['Prix d\'achat avec frais'] = df['Prix (DH)'] + df['Valeur taxable']
    df['Marge'] = df['Prix Moyen Maroc'] - df['Prix d\'achat avec frais']

# Filtrer les annonces valides avec marge calculée
df_valid = df.dropna(subset=['Marge', 'Prix Moyen Maroc', 'Prix d\'achat avec frais']).reset_index(drop=True)

# Indices des annonces (numérotation)
indices = np.arange(len(df_valid))

# Définir couleurs selon la marge
colors = ['green' if m >= 0 else 'red' for m in df_valid['Marge']]

# Largeur des bougies
width = 0.6

fig, ax = plt.subplots(figsize=(14, 7))

for i, row in df_valid.iterrows():
    prix_achat = row["Prix d'achat avec frais"]
    prix_maroc = row["Prix Moyen Maroc"]

    # Position verticale de la bougie : entre prix_achat et prix_maroc
    lower = min(prix_achat, prix_maroc)
    height = abs(prix_maroc - prix_achat)

    # Dessiner une "bougie"
    ax.bar(i, height, width, bottom=lower, color=colors[i], alpha=0.7, edgecolor='black')

# Tracer ligne zéro comme repère (facultatif)
ax.axhline(0, color='black', linewidth=0.8)

# Labels et titres
ax.set_xticks(indices)
ax.set_xticklabels(indices + 1)  # Numérotation annonces à partir de 1
ax.set_xlabel("Numéro de l'annonce")
ax.set_ylabel("Montant (DH)")
ax.set_title("Visualisation des marges brutes des annonces de motos")

# Légende manuelle
import matplotlib.patches as mpatches
green_patch = mpatches.Patch(color='green', label='Marge positive')
red_patch = mpatches.Patch(color='red', label='Marge négative')
ax.legend(handles=[green_patch, red_patch])

plt.tight_layout()
plt.savefig("marge_candlestick_annonces.png", dpi=300)
plt.show()

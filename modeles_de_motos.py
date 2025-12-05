from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
import csv
import time

chemin_chromedriver = r"C:\chromedriver-win64\chromedriver.exe"
url = "https://www2.douane.gov.ma/mcv/#/view?pageId=2"

options = Options()
options.add_argument("--start-maximized")

driver = webdriver.Chrome(service=Service(chemin_chromedriver), options=options)
wait = WebDriverWait(driver, 15)

driver.get(url)

# === Ouvrir le menu des marques ===
wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='marque']"))).click()
time.sleep(1)

# === Récupérer toutes les marques disponibles ===
wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "mat-option span")))
marque_elements = driver.find_elements(By.CSS_SELECTOR, "mat-option span")
marques = [m.text.strip() for m in marque_elements if m.text.strip()]

print(f"✅ {len(marques)} marques détectées.")

# === Fichier CSV en écriture
with open("tous_les_modeles.csv", "w", newline="", encoding="utf-8") as f:
    writer = csv.writer(f)
    writer.writerow(["Marque", "Modèle"])

    for marque in marques:
        try:
            # Fermer backdrop s’il est présent
            try:
                backdrop = driver.find_element(By.CSS_SELECTOR, ".cdk-overlay-backdrop")
                driver.execute_script("arguments[0].click();", backdrop)
                time.sleep(0.5)
            except:
                pass

            # Réouvrir le menu des marques
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='marque']"))).click()
            time.sleep(1)

            # Cliquer sur la marque actuelle
            wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "mat-option span")))
            element_marque = driver.find_element(By.XPATH, f"//span[normalize-space()='{marque}']")
            driver.execute_script("arguments[0].scrollIntoView(true);", element_marque)
            element_marque.click()
            time.sleep(1.5)

            # === Tenter d’ouvrir le menu des modèles
            try:
                modele_select = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, "mat-select[formcontrolname='modele']")))
                modele_select.click()
            except:
                print(f"❌ Aucun modèle pour la marque {marque}")
                continue

            time.sleep(1)

            # Extraire les modèles
            modele_elements = wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "div[role='listbox'] mat-option span")))
            modeles = [m.text.strip() for m in modele_elements if m.text.strip()]
            
            print(f"✅ {marque} : {len(modeles)} modèles")
            for modele in modeles:
                writer.writerow([marque, modele])

        except Exception as e:
            print(f"⚠️ Problème avec {marque} : {e}")
            continue

print("✅ Export terminé → fichier : tous_les_modeles.csv")
driver.quit()

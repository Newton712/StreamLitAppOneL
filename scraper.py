# scraper.py (version simplifiée côté Streamlit qui appelle l'API)
import requests

API_URL = "https://melee-scraper-api.onrender.com/scrape"  # Remplace par l'URL de ton API FastAPI

def scrape_tournament_data(url):
    response = requests.get(API_URL, params={"url": url})
    if response.status_code == 200:
        data = response.json()
        tournament = data.get("tournament")
        players = data.get("players")
        tables = data.get("tables")
        return tournament, players, tables
    else:
        raise Exception("Erreur API scraping : " + response.text)

def import_last_pairing(url, tournament_id):
    # Pour l'instant, on peut réutiliser la même API pour ré-importer le dernier pairing si la logique est centralisée
    return scrape_tournament_data(url)[2]  # Retourne uniquement les tables

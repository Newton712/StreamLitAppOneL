# scraper.py



from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from datetime import datetime, timedelta
from supabase import create_client
import chromedriver_autoinstaller

SUPABASE_URL = "https://zxlumrmkuuighyfxzshg.supabase.co"
SUPABASE_KEY = "yeyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4bHVtcm1rdXVpZ2h5Znh6c2hnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Njk3MzU2NiwiZXhwIjoyMDYyNTQ5NTY2fQ.ANiwlR7Sm7EhrHgP0SvIUrYQdLHYuP-WF4jyHB06Te0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


def start_browser():
    chromedriver_autoinstaller.install()  # ✅ Installe la bonne version de chromedriver

    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--disable-gpu")
    options.binary_location = "/usr/bin/chromium"

    return webdriver.Chrome(options=options)

def scrape_tournament_data(url):
    driver = start_browser()
    driver.get(url)

    tournament_id = driver.find_element(By.ID, "tournament-id").get_attribute("value").strip()
    tournament_name = driver.find_element(By.CSS_SELECTOR, "h3.mb-1").text.strip()
    raw_date = driver.find_element(By.CSS_SELECTOR, "span[data-toggle='datetime']").get_attribute("data-value").strip()
    dt = datetime.strptime(raw_date, "%m/%d/%Y %I:%M:%S %p") + timedelta(hours=2)
    formatted_date = dt.strftime("%d/%m/%Y %H:%M CEST")
    tournament = {
        "tournament_id": tournament_id,
        "tournament_name": tournament_name,
        "tournament_date": formatted_date
    }

    players = set()
    elements = driver.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
    for el in elements:
        name = el.get_attribute("innerHTML").split("<svg")[0].strip()
        if name:
            players.add(name)
    players = sorted(players)

    rows = driver.find_elements(By.CSS_SELECTOR, "#pairings tbody tr")
    tables = []
    for row in rows:
        try:
            table_num = row.find_element(By.CSS_SELECTOR, "td.TableNumber-column").text.strip()
            ps = row.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
            p1 = ps[0].get_attribute("innerHTML").split("<svg")[0].strip()
            p2 = ps[1].get_attribute("innerHTML").split("<svg")[0].strip()
            tables.append({
                "round": "Ronde 1",
                "tableNum": table_num,
                "player_1": p1,
                "player_2": p2,
                "DeckcolorA1": None,
                "DeckcolorA2": None,
                "DeckcolorB1": None,
                "DeckcolorB2": None
            })
        except:
            continue

    driver.quit()
    return tournament, players, tables

def import_last_pairing(url, tournament_id):
    driver = start_browser()
    driver.get(url)
    rows = driver.find_elements(By.CSS_SELECTOR, "#pairings tbody tr")
    new_pairings = []

    for row in rows:
        try:
            table_num = row.find_element(By.CSS_SELECTOR, "td.TableNumber-column").text.strip()
            ps = row.find_elements(By.CSS_SELECTOR, 'a[data-type="player"]')
            p1 = ps[0].get_attribute("innerHTML").split("<svg")[0].strip()
            p2 = ps[1].get_attribute("innerHTML").split("<svg")[0].strip()

            p1data = supabase.table("players").select("*").eq("name", p1).eq("tournament_id", tournament_id).execute().data
            p2data = supabase.table("players").select("*").eq("name", p2).eq("tournament_id", tournament_id).execute().data

            a1, a2 = (p1data[0]["Deckcolor1"], p1data[0]["Deckcolor2"]) if p1data else (None, None)
            b1, b2 = (p2data[0]["Deckcolor1"], p2data[0]["Deckcolor2"]) if p2data else (None, None)

            new_pairings.append({
                "tournament_id": tournament_id,
                "round": "Nouvelle Ronde",
                "tableNum": table_num,
                "player_1": p1,
                "player_2": p2,
                "DeckcolorA1": a1,
                "DeckcolorA2": a2,
                "DeckcolorB1": b1,
                "DeckcolorB2": b2
            })
        except:
            continue

    driver.quit()
    if new_pairings:
        supabase.table("pairings").insert(new_pairings).execute()

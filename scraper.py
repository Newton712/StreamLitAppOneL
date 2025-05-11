# scraper.py
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from datetime import datetime, timedelta
from supabase import create_client
import chromedriver_autoinstaller

SUPABASE_URL = "https://your-project.supabase.co"
SUPABASE_KEY = "your-service-role-key"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

def start_browser():
    chromedriver_autoinstaller.install()  # ✅ auto-installe le bon ChromeDriver

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

    WebDriverWait(driver, 15).until(
        EC.presence_of_element_located((By.ID, "tournament-id"))
    )

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

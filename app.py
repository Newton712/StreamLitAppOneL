# app.py
import streamlit as st
from supabase import create_client
from scraper import scrape_tournament_data, import_last_pairing

SUPABASE_URL = "https://zxlumrmkuuighyfxzshg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4bHVtcm1rdXVpZ2h5Znh6c2hnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Njk3MzU2NiwiZXhwIjoyMDYyNTQ5NTY2fQ.ANiwlR7Sm7EhrHgP0SvIUrYQdLHYuP-WF4jyHB06Te0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Import Tournoi Melee.gg")
st.title("Import Tournoi Melee.gg")

url = st.text_input("URL du tournoi Melee.gg", "https://www.melee.gg/Tournament/View/305532")

if st.button("Lancer Recherche"):
    tournament_id = url.split("/")[-1]
    existing = supabase.table("tournaments").select("tournament_id").eq("tournament_id", tournament_id).execute()

    if existing.data:
        st.success("✅ Tournoi déjà existant.")
    else:
        with st.spinner("Scraping et importation..."):
            tournament, players, tables = scrape_tournament_data(url)
            supabase.table("tournaments").insert(tournament).execute()
            supabase.table("players").insert(
                [{"name": name, "tournament_id": tournament["tournament_id"]} for name in players]
            ).execute()
            for row in tables:
                row["tournament_id"] = tournament["tournament_id"]
            supabase.table("pairings").insert(tables).execute()

        st.success("✅ Nouveau tournoi importé.")

    st.switch_page("pages/gestion.py")

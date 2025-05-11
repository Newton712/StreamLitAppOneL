# pages/gestion.py
import streamlit as st
from supabase import create_client
from scraper import import_last_pairing

SUPABASE_URL = "https://zxlumrmkuuighyfxzshg.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Inp4bHVtcm1rdXVpZ2h5Znh6c2hnIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc0Njk3MzU2NiwiZXhwIjoyMDYyNTQ5NTY2fQ.ANiwlR7Sm7EhrHgP0SvIUrYQdLHYuP-WF4jyHB06Te0"
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

st.set_page_config(page_title="Gestion du tournoi")
st.title("Gestion du tournoi")

tournaments = supabase.table("tournaments").select("*").execute().data
if not tournaments:
    st.warning("Aucun tournoi importé.")
    st.stop()

tour = tournaments[-1]
tid = tour["tournament_id"]
st.subheader(f"🎯 {tour['tournament_name']} ({tour['tournament_date']})")

if st.button("📥 Importer la ronde suivante"):
    import_last_pairing(f"https://www.melee.gg/Tournament/View/{tid}", tid)
    st.experimental_rerun()

st.divider()
st.subheader("🎮 Joueurs")
players = supabase.table("players").select("*").eq("tournament_id", tid).execute().data
for p in players:
    c1 = st.selectbox(f"{p['name']} - Couleur 1", ["", "jaune", "mauve", "vert", "rouge", "bleu", "gris"], index=0, key=f"p1_{p['id']}")
    c2 = st.selectbox(f"{p['name']} - Couleur 2", ["", "jaune", "mauve", "vert", "rouge", "bleu", "gris"], index=0, key=f"p2_{p['id']}")
    if st.button(f"💾 Enregistrer {p['name']}", key=f"save_{p['id']}"):
        supabase.table("players").update({
            "Deckcolor1": c1 if c1 else None,
            "Deckcolor2": c2 if c2 else None
        }).eq("id", p["id"]).execute()
        st.success("✅ Couleurs mises à jour")

st.divider()
st.subheader("🪑 Tables")
tables = supabase.table("pairings").select("*").eq("tournament_id", tid).execute().data
st.table(tables)

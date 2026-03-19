import streamlit as st
from mongo_manager import get_mongo_client
from neo4j_manager import run_query

# Configuration de la page
st.set_page_config(page_title="Mon Dashboard Multi-NoSQL", layout="wide")
st.title("🎬 Analyse de Films (Mongo + Neo4j)")

# --- SECTION MONGODB ---
st.header("📊 Statistiques Globales (MongoDB)")
client = get_mongo_client()

if client:
    db = client.entertainment  # Nom de ta base
    col1, col2 = st.columns(2)
    
    with col1:
        total_films = db.films.count_documents({})
        st.metric("Total des films", total_films)
        
    with col2:
        # Exemple d'agrégation : Moyenne des votes pour 2007
        res = db.films.aggregate([
            {"$match": {"year": 2007}},
            {"$group": {"_id": None, "avg": {"$avg": "$Votes"}}}
        ]).next()
        st.metric("Moyenne Votes (2007)", f"{res['avg']:.0f}")

# --- SECTION NEO4J ---
st.header("🕸️ Relations et Graphes (Neo4j)")

# Requête Cypher pour compter les nœuds
cypher_count = "MATCH (n) RETURN count(n) AS total"
data_neo = run_query(cypher_count)

if data_neo:
    total_nodes = data_neo[0]['total']
    st.write(f"Nombre de nœuds dans le graphe : **{total_nodes}**")
    
    # On peut aussi afficher les derniers résultats sous forme de tableau
    st.subheader("Aperçu des données")
    st.table(data_neo)
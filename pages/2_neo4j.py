import streamlit as st
from neo4j_manager import run_query

# --- SECTION NEO4J ---
st.header("Relations et Graphes (Neo4j)")

# Requête Cypher pour compter les nœuds
cypher_count = "MATCH (n) RETURN count(n) AS total"
data_neo = run_query(cypher_count)

if data_neo:
    total_nodes = data_neo[0]['total']
    st.write(f"Nombre de nœuds dans le graphe : **{total_nodes}**")
    
    # On peut aussi afficher les derniers résultats sous forme de tableau
    st.subheader("Aperçu des données")
    st.table(data_neo)
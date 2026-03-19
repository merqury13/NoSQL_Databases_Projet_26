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

    st.subheader("14. Which actor has appeared in the most films?")
    st.subheader("15. Which actors have appeared in films in which the actress Anne Hathaway has also appeared?")
    st.subheader("16. Which actor has appeared in films with the highest total box office takings?")
    st.subheader("17. What is the average rating?")
    st.subheader("18. Which genre is most represented in the database?")
    st.subheader("19. Which films have the actors who starred alongside you also appeared in?")
    st.subheader("20. Which director has worked with the most different actors?")
    st.subheader("21. Which films are the most ‘connected’, i.e. those that share the most actors with other films?")
    st.subheader("22. Find the 5 actors who have starred in films directed by the most different directors.")
    st.subheader("23. Recommend a film to an actor based on the genres of the films in which they have already starred.")
    st.subheader("24. Create an INFLUENCE BY relationship between directors based on similarities in the genres of the films they have directed.")
    st.subheader("25. What is the shortest ‘path’ between two given actors (e.g. Tom Hanks and Scarlett Johansson)?")
    st.subheader("26. Analyse actor communities: Which groups of actors tend to work together? (Using community detection algorithms such as Louvain.)")
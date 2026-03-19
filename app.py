import streamlit as st
from mongo_manager import get_mongo_client
from neo4j_manager import run_query
from data_sync import migrate_mongo_to_neo4j 


# Configuration de la page
st.set_page_config(page_title="Mon Dashboard Multi-NoSQL", layout="wide")
st.title("🎬 Analyse de Films (Mongo + Neo4j)")

st.write("This project, developed for the 2025-2026 academic year, is a comprehensive data " \
"exploration and visualization application built with Streamlit. It demonstrates the integration of two " \
"distinct database paradigms: MongoDB for document-oriented storage and Neo4j for graph-based relationship" \
" analysis. \n" \
" The application performs advanced data processing—ranging from statistical aggregations on " \
"movie metadata in MongoDB to complex network analysis and pathfinding in Neo4j—while adhering to " \
"professional development standards such as virtual environments, secure credential management, and " \
"modular code organization.")


st.sidebar.title("Administration")#to update the Neo4j DB according to MongoDB
if st.sidebar.button("Initialiser Neo4j depuis MongoDB"):
    with st.spinner("Migration en cours..."):
        try:
            migrate_mongo_to_neo4j()
            st.sidebar.success("Données injectées dans Neo4j !")
        except Exception as e:
            st.sidebar.error(f"Erreur lors de la migration : {e}")

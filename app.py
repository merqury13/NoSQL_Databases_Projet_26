import streamlit as st
from mongo_manager import get_mongo_client
from neo4j_manager import run_query

# Configuration de la page
st.set_page_config(page_title="Mon Dashboard Multi-NoSQL", layout="wide")
st.title("🎬 Analyse de Films (Mongo + Neo4j)")

st.write("This project, developed for the 2025-2026 academic year , is a comprehensive data " \
"exploration and visualization application built with Streamlit. It demonstrates the integration of two " \
"distinct database paradigms: MongoDB for document-oriented storage and Neo4j for graph-based relationship" \
" analysis.\n" \
" The application performs advanced data processing—ranging from statistical aggregations on " \
"movie metadata in MongoDB to complex network analysis and pathfinding in Neo4j—while adhering to " \
"professional development standards such as virtual environments, secure credential management, and " \
"modular code organization.")

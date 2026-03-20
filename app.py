import streamlit as st
from mongo_manager import get_mongo_client
from neo4j_manager import run_query
from data_sync import migrate_mongo_to_neo4j 


# Configuration de la page
st.title("🎬 Movies DB analysis project (Mongo + Neo4j)")

st.write("This project, developed for the 2025-2026 fourth ESIEA academic year, is a comprehensive data " \
"exploration and visualization application built with Streamlit. It demonstrates the integration of two " \
"distinct database paradigms: MongoDB for document-oriented storage and Neo4j for graph-based relationship" \
" analysis. \n" \
" The application performs advanced data processing—ranging from statistical aggregations on " \
"movie metadata in MongoDB to complex network analysis and pathfinding in Neo4j—while adhering to " \
"professional development standards such as virtual environments, secure credential management, and " \
"modular code organization.")

st.write("Explore the other pages to discover the information we can find in our DBs !")


st.sidebar.title("Update Neo4j according to MongoDB")#to update the Neo4j DB following MongoDB
if st.sidebar.button("Updating Neo4j DB from MongoDB"):
    with st.spinner("Migrating..."):
        try:
            migrate_mongo_to_neo4j()
            st.sidebar.success("Neo4j DB updated !")
        except Exception as e:
            st.sidebar.error(f"Error when updating : {e}")

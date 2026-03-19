import os
import streamlit as st
from neo4j import GraphDatabase, basic_auth
from dotenv import load_dotenv

load_dotenv()

def get_neo4j_driver():
    uri = st.secrets.get("NEO4J_URI") or os.getenv("NEO4J_URI")
    user = st.secrets.get("NEO4J_USERNAME") or os.getenv("NEO4J_USERNAME")
    password = st.secrets.get("NEO4J_PASSWORD") or os.getenv("NEO4J_PASSWORD")

    if not all([uri, user, password]):
        st.error("Identifiants Neo4j manquants")
        return None

    return GraphDatabase.driver(uri, auth=basic_auth(user, password))

def run_query(query, parameters=None):
    driver = get_neo4j_driver()
    if not driver: return None
    
    try:
        with driver.session(database="neo4j") as session:
            result = session.run(query, parameters)
            return list(result) 
    finally:
        driver.close()
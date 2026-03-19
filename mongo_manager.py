import os
import streamlit as st
from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
from dotenv import load_dotenv

# Charge le .env uniquement si on est en local
load_dotenv()

def get_mongo_client():
    # Streamlit Cloud stocke les secrets dans st.secrets
    # En local, os.getenv ira chercher dans ton .env
    uri = st.secrets.get("MONGO_URI") or os.getenv("MONGO_URI")
    
    if not uri:
        st.error("MONGO_URI non trouvée dans les secrets ou le .env")
        return None
        
    return MongoClient(uri, server_api=ServerApi('1'))

# Fonction pour tester la connexion (utile pour le debug au lancement)
def test_mongo():
    client = get_mongo_client()
    try:
        client.admin.command('ping')
        return True
    except Exception as e:
        print(f"Erreur Mongo: {e}")
        return False
    
def get_mongo_db():
    client = get_mongo_client()
    # Tu peux aussi mettre "entertainment" dans tes secrets/env
    db_name = st.secrets.get("MONGO_DB_NAME") or os.getenv("MONGO_DB_NAME") or "entertainment"
    return client[db_name]
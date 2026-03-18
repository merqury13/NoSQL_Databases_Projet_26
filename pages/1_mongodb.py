import streamlit as st
from mongo_manager import get_db_client

st.title("Mon App NoSQL")
'''
# Utilisation du client
client = get_db_client()
db = client.entertainment # Remplace par le nom de ta base

if st.button("Tester la connexion"):
    try:
        client.admin.command('ping')
        st.success("Connexion établie !")
    except:
        st.error("Échec de la connexion")'''
import streamlit as st
import subprocess

# Exemple de mise à jour de pip
if st.button('Mettre à jour pip'):
    result = subprocess.run(['pip', 'install', '--upgrade', 'pip'], capture_output=True, text=True)
    st.text(result.stdout)  # Affiche la sortie de la commande
    st.text(result.stderr)  # Affiche les erreurs (le cas échéant)

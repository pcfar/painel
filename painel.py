import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io
import streamlit_authenticator as stauth
import copy

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Inteligência Tática", page_icon="🧠", layout="wide")

# --- SISTEMA DE AUTENTICAÇÃO ---
config = {
    'credentials': {
        'usernames': dict(st.secrets['credentials']['usernames'])
    },
    'cookie': dict(st.secrets['cookie'])
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- CORREÇÃO DEFINITIVA ---
# Chamamos a função de login no centro da página, sem argumentos extras.
# A função irá guardar os resultados em st.session_state.
authenticator.login(location='main')

# --- LÓGICA DE ACESSO ---
# Lemos o status do login a partir de st.session_state.
if st.session_state.get("authentication_status"):
    # --- APLICAÇÃO PRINCIPAL (SÓ APARECE APÓS LOGIN) ---
    col1, col2 = st.columns([0.85, 0.15])
    with col2:
        authenticator.logout('Logout', key='unique_key')

    st.write(f'Bem-vindo, *{st.session_state["name"]}*!')
    st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
    # O resto do seu código da aplicação viria aqui...


elif st.session_state.get("authentication_status") == False:
    st.error('Nome de utilizador/senha incorreto(a)')
elif st.session_state.get("authentication_status") == None:
    st.warning('Por favor, introduza o seu nome de utilizador e senha')

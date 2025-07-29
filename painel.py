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

# --- CORREÇÃO FINAL: Chamamos a função de login na barra lateral ---
# Esta função não retorna valores, mas os guarda em st.session_state
authenticator.login(location='sidebar')

# --- LÓGICA DE ACESSO ---
# Verificamos os valores guardados em st.session_state
if st.session_state["authentication_status"]:
    # --- APLICAÇÃO PRINCIPAL (SÓ APARECE APÓS LOGIN) ---
    with st.sidebar:
        st.write(f'Bem-vindo, *{st.session_state["name"]}*!')
        authenticator.logout('Logout', location='sidebar', key='unique_key')

    st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
    st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

    # --- CENTRAL DE UPLOAD (APENAS PARA ADMIN) ---
    if st.session_state["username"] == 'admin':
        st.header("1. Central de Upload e Organização")
        with st.expander("Clique aqui para enviar novos 'prints' para análise"):
            # (O formulário de upload viria aqui)
            st.success("Área de Upload disponível.")

    # --- CENTRAL DE ANÁLISE (VISÍVEL PARA TODOS OS USUÁRIOS LOGADOS) ---
    st.markdown("---")
    st.header("2. Central de Análise: Gerar Dossiês")
    # (A lógica da Central de Análise viria aqui)
    st.info("Área de Análise disponível.")


elif st.session_state["authentication_status"] == False:
    with st.sidebar:
        st.error('Nome de utilizador/senha incorreto(a)')
elif st.session_state["authentication_status"] == None:
    with st.sidebar:
        st.warning('Por favor, introduza o seu nome de utilizador e senha')

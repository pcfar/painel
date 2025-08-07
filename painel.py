# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - Versão com Layout "Premium"
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS GLOBAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """Aplica o design final "Modo Tático", com layout refinado."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

            /* As cores base são controladas pelo config.toml. Este CSS refina os detalhes. */
            
            body, .main, [data-testid="stSidebar"] {
                font-family: 'Roboto', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }

            /* --- NOVO: Estilo para os cartões do formulário --- */
            .form-card {
                background-color: #2D3748; /* secondaryBackgroundColor do tema */
                padding: 25px;
                border-radius: 12px;
                box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2);
                border: 1px solid #4A5568;
                margin-bottom: 25px; /* Espaçamento entre os cartões */
            }

            /* Refinando os rótulos dos campos do formulário */
            .st-emotion-cache-1629p8f label {
                color: #A0AEC0; /* --text-secondary */
                font-weight: 400;
                font-size: 0.9rem;
            }
            
            /* Botão Principal com mais destaque */
            .stButton>button[kind="primary"] {
                height: 3rem;
                font-size: 1.1rem;
                font-weight: 700;
                border-radius: 8px;
                transition: all 0.3s ease-in-out;
            }
            .stButton>button[kind="primary"]:hover {
                box-shadow: 0 0 20px 0 rgba(49, 130, 206, 0.6);
            }

            /* Demais estilos... (mantidos da versão anterior) */
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; transition: all 0.3s ease-in-out !important; }
            .nav-link:hover { background-color: #4A5568 !important; }
            .nav-link-selected { box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2); }
            
            .dossier-viewer { line-height: 1.8; color: #E2E8F0; }
            .dossier-viewer h3 { border-bottom: 2px solid #3182CE; padding-bottom: 8px; }
            .dossier-viewer table {
                border-collapse: separate; border-spacing: 0; width: 100%;
                border: 1px solid #4A5568; border-radius: 8px;
                overflow: hidden; margin: 1.5rem 0;
            }
            .dossier-viewer th { background-color: #2D3748; font-weight: 700; }
            .dossier-viewer th, .dossier-viewer td { padding: 10px 15px; text-align: left; border-bottom: 1px solid #4A5568; }
            .dossier-viewer tr:last-child td { border-bottom: none; }
        </style>
    """, unsafe_allow_html=True)

# O restante do código Python é EXATAMENTE O MESMO.
# A combinação do novo config.toml e este CSS refinado resolverá o problema.
# --- 2. AUTENTICAÇÃO E CONEXÃO COM GITHUB ---
def check_password():
    if st.session_state.get("password_correct", False): return True
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Painel de Inteligência")
        password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"):
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("😕 Senha incorreta. Tente novamente.")
    return False

@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Falha na conexão com o repositório do GitHub: {e}")
        return None

# --- 3. FUNÇÕES AUXILIARES DE LÓGICA ---
def parse_path_to_form(path):
    try:
        parts = [p for p in path.split('/') if p]
        file_name = parts[-1]
        st.session_state.pais = parts[0].replace("_", " ")
        st.session_state.liga = parts[1].replace("_", " ")
        st.session_state.temporada = parts[2]
        if file_name == "Dossiê_Liga.md": st.session_state.tipo_dossie = "Dossiê de Liga"
        elif file_name == "Dossiê_Clube.md":
            st.session_state.tipo_dossie = "Dossiê de Clube"
            st.session_state.clube = parts[3].replace("_", " ")
        elif file_name in ["Briefing_Pre-Jogo.md", "Relatorio_Pos-Jogo.md"]:
            st.session_state.tipo_dossie

import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Inteligência Tática", page_icon="🧠", layout="wide")

# --- SISTEMA DE SENHA ÚNICA ---
def check_password():
    """Retorna True se a senha estiver correta."""
    def password_entered():
        """Verifica se a senha digitada corresponde à senha no cofre."""
        if st.session_state["password"] == st.secrets["APP_PASSWORD"]:
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Não manter a senha em memória
        else:
            st.session_state["password_correct"] = False

    if "password_correct" not in st.session_state:
        # Apresenta o formulário de senha
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        return False
    elif not st.session_state["password_correct"]:
        # Senha incorreta
        st.text_input("Password", type="password", on_change=password_entered, key="password")
        st.error("😕 Senha incorreta.")
        return False
    else:
        # Senha correta
        return True

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    # --- Título e Boas-vindas (Aparece após o login) ---
    st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
    st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

    # --- Autenticação no GitHub ---
    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception as e:
            st.error("Erro ao conectar com o GitHub.")
            st.exception(e)
            st.stop()
    repo = get_github_connection()

    # O resto do código da aplicação (Centrais de Upload e Análise) viria aqui...
    # Por enquanto, vamos confirmar que o login funciona.
    st.success("Login bem-sucedido! O painel completo seria exibido aqui.")

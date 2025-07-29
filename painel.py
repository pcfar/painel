import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io

st.set_page_config(page_title="Painel Tático", page_icon="🧠", layout="wide")

def check_password():
    if st.session_state.get("password_correct", False):
        return True

    def password_entered():
        if st.session_state.get("password") == st.secrets.get("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta.")
    return False

if check_password():
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")
    st.subheader("Plataforma de Análise para Trading Esportivo")

    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo = g.get_repo("pcfar/painel")
    except Exception:
        st.error("Erro ao conectar com o GitHub. Verifique o GITHUB_TOKEN.")
        st.stop()

    # O resto do seu código funcional (Centrais de Upload e Análise) viria aqui.
    st.success("Login bem-sucedido! O sistema está pronto para ter as funcionalidades adicionadas.")

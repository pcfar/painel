import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v6.5", page_icon="🧠", layout="wide")

# --- SISTEMA DE SENHA ÚNICA ---
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

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")

    # --- Conexão com o GitHub (Omitida para brevidade, mas deve ser mantida) ---
    # ...

    # --- CENTRAL DE COMANDO COM ABAS ---
    st.header("Central de Comando")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        st.info("Formulário do Dossiê 1.")

    with tab2:
        st.info("Formulário do Dossiê 2.")
        
    with tab3:
        st.info("Formulário do Dossiê 3.")

    with tab4:
        st.subheader("Gerar Dossiê 4: Briefing Semanal Autónomo")
        with st.form("form_dossie_4"):
            st.write("Forneça o contexto da partida para que o Agente de IA possa iniciar a busca por inteligência.")

            temporada = st.text_input("Temporada*", placeholder="Ex: 2025-2026")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            clube = st.text_input("Clube-Alvo (nome completo)*", placeholder="Ex: Feyenoord")
            adversario = st.text_input("Adversário (nome completo)*", placeholder="Ex: Ajax")
            rodada = st.text_input("Rodada*", placeholder="Ex: R06")

            if st.form_submit_button("Iniciar Agente de IA e Gerar Briefing"):
                if not all([temporada, liga, clube, adversario, rodada]):
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    # Guarda o comando na memória da sessão
                    comando = f"EXECUTE O BRIEFING: Temporada {temporada}, Liga {liga}, Rodada {rodada}, {clube} vs {adversario}"
                    st.session_state['comando_ia'] = comando
        
        # Mostra a confirmação fora do formulário
        if 'comando_ia' in st.session_state:
            st.success("Comando recebido pelo sistema!")
            st.info("O Agente de Inteligência está pronto para a missão.")
            st.warning(f"""
            Para receber o seu relatório, por favor, volte ao seu assistente (Gemini) e envie o seguinte comando:

            **{st.session_state['comando_ia']}**
            """)

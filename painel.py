import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v6.3", page_icon="🧠", layout="wide")

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

    # --- Conexão com o GitHub ---
    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception:
            st.error("Erro ao conectar com o GitHub.")
            st.stop()
    repo = get_github_connection()

    # --- CENTRAL DE COMANDO COM ABAS ---
    st.header("Central de Comando")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        # Lógica do Dossiê 1
        st.info("Formulário do Dossiê 1.")

    with tab2:
        # Lógica do Dossiê 2
        st.info("Formulário do Dossiê 2.")
        
    with tab3:
        st.subheader("Criar Dossiê 3: Relatório Pós-Jogo")
        with st.form("form_dossie_3"):
            st.write("Forneça os 'prints' da última partida da equipe-alvo para gerar a análise.")

            temporada = st.text_input("Temporada*", placeholder="Ex: 2024-2025")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            clube = st.text_input("Clube (código)*", placeholder="Ex: FEY")
            rodada = st.text_input("Rodada*", placeholder="Ex: R05")

            st.markdown("---")

            print_stats_ht = st.file_uploader("1) Print das Estatísticas do 1º Tempo (Sofascore)*", help="Capture a tela de 'Estatísticas' da partida com o filtro '1º Tempo' selecionado.", type=['png', 'jpg'])
            print_stats_st = st.file_uploader("2) Print das Estatísticas do 2º Tempo (Sofascore)*", help="Capture a mesma tela de 'Estatísticas', mas com o filtro '2º Tempo'.", type=['png', 'jpg'])
            print_timeline = st.file_uploader("3) Print da Linha do Tempo e Substituições (Sofascore)*", help="Capture a tela principal do jogo que mostra a sequência de gols, eventos e substituições.", type=['png', 'jpg'])

            if st.form_submit_button("Processar e Gerar Dossiê 3"):
                if not all([temporada, liga, clube, rodada, print_stats_ht, print_stats_st, print_timeline]):
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    with st.spinner("Processando Dossiê 3..."):
                        # (A lógica completa de upload inteligente e análise OCR viria aqui)
                        st.success("Simulação: Dossiê 3 (Pós-Jogo) gerado com sucesso!")
                        st.balloons()
    with tab4:
        st.info("Formulário para o Dossiê 4 (Pré-Jogo) em desenvolvimento.")

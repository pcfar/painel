import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v6.4", page_icon="🧠", layout="wide")

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
        st.info("Formulário do Dossiê 1.")

    with tab2:
        st.info("Formulário do Dossiê 2.")
        
    with tab3:
        st.info("Formulário do Dossiê 3.")

    with tab4:
        st.subheader("Criar Dossiê 4: Briefing Semanal Pré-Jogo")
        with st.form("form_dossie_4"):
            st.write("Forneça os 'prints' com o contexto mais recente para a próxima partida.")

            temporada = st.text_input("Temporada*", placeholder="Ex: 2024-2025")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            clube = st.text_input("Clube-Alvo (código)*", placeholder="Ex: FEY")
            rodada = st.text_input("Rodada*", placeholder="Ex: R06")

            st.markdown("---")

            prints_coletiva = st.file_uploader("1) Print(s) com Citações-Chave do Treinador*", help="Capture a coletiva de imprensa pré-jogo.", accept_multiple_files=True, type=['png', 'jpg'])
            print_elenco = st.file_uploader("2) Print com Status do Elenco (Lesões/Suspensões)*", help="Capture notícias recentes sobre o estado do elenco.", type=['png', 'jpg'])
            print_adversario = st.file_uploader("3) Print com Contexto do Adversário*", help="Capture a tabela de classificação e os últimos resultados do adversário.", type=['png', 'jpg'])

            if st.form_submit_button("Processar e Gerar Dossiê 4"):
                if not all([temporada, liga, clube, rodada, prints_coletiva, print_elenco, print_adversario]):
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    with st.spinner("Processando Dossiê 4..."):
                        # (A lógica completa de upload inteligente e análise OCR viria aqui)
                        st.success("Simulação: Dossiê 4 (Pré-Jogo) gerado com sucesso!")
                        st.balloons()

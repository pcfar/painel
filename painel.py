import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v6.1", page_icon="🧠", layout="wide")

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
        # Lógica do Dossiê 1 (já implementada)
        st.subheader("Criar Dossiê 1: Análise Geral da Liga")
        # ... (código do formulário do Dossiê 1 omitido por brevidade) ...
        st.info("Formulário do Dossiê 1.")


    with tab2:
        st.subheader("Criar Dossiê 2: Análise Aprofundada do Clube")
        
        # --- PARTE 1: ANÁLISE PRELIMINAR ---
        with st.form("form_dossie_2_p1"):
            st.markdown("**Parte 1: Análise Preliminar do Elenco**")
            st.write("Forneça os dados gerais da equipe na temporada passada e a lista do elenco atual.")

            temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            clube = st.text_input("Clube (código)*", placeholder="Ex: FEY")
            st.markdown("---")

            print_stats_gerais = st.file_uploader("1) Print da Visão Geral de Estatísticas do Clube*", help="Sugestão: No FBref, capture a página principal do clube na temporada de referência.")
            print_elenco = st.file_uploader("2) Print dos Detalhes do Elenco (Entradas e Saídas)*", help="Sugestão: No Transfermarkt ou Sofascore, capture a tela que mostra o elenco atual, incluindo reforços e saídas.")
            
            if st.form_submit_button("Gerar Análise Preliminar e Identificar Reforços-Chave"):
                if not all([temporada, liga, clube, print_stats_gerais, print_elenco]):
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    with st.spinner("AGENTE ANALISTA a processar a Parte 1..."):
                        # Lógica de upload e análise da Parte 1 viria aqui
                        # Simulação da saída da IA
                        st.success("Análise Preliminar Concluída!")
                        st.markdown("---")
                        st.markdown("**Resultado da Análise (Saída da IA):**")
                        st.info("""
                        Com base nos dados fornecidos, a base da equipe para a temporada **2024-2025** está mantida. 
                        Os seguintes reforços foram identificados como de alto impacto e necessitam de uma análise aprofundada:
                        - **Jogador A (Atacante)**
                        - **Jogador B (Meio-campista)**
                        
                        *Por favor, prossiga para a Parte 2 para fornecer os 'prints' detalhados destes jogadores.*
                        """)
                        st.warning("A Parte 2 (formulário de upload para os reforços) será implementada no próximo passo.")

    with tab3:
        st.info("Formulário para o Dossiê 3 (Relatório Pós-Jogo) em desenvolvimento.")
    with tab4:
        st.info("Formulário para o Dossiê 4 (Briefing Semanal) em desenvolvimento.")

    # (Área de Administração na sidebar permanece a mesma)

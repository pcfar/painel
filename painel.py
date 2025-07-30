import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v6.2", page_icon="🧠", layout="wide")

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
        st.subheader("Criar Dossiê 2: Análise Aprofundada do Clube (Fluxo Interativo)")
        
        # --- PARTE 1: ANÁLISE PRELIMINAR ---
        if 'jogadores_identificados' not in st.session_state:
            with st.form("form_dossie_2_p1"):
                st.markdown("**Parte 1: Análise Preliminar do Elenco**")
                temporada = st.text_input("Temporada*", placeholder="Ex: 2024-2025")
                liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
                clube = st.text_input("Clube (código)*", placeholder="Ex: FEY")
                print_stats_gerais = st.file_uploader("1) Print da Visão Geral de Estatísticas do Clube*", help="Sugestão: No FBref...")
                print_elenco = st.file_uploader("2) Print dos Detalhes do Elenco (Entradas e Saídas)*", help="Sugestão: No Transfermarkt...")
                
                if st.form_submit_button("Gerar Análise Preliminar e Identificar Reforços-Chave"):
                    if not all([temporada, liga, clube, print_stats_gerais, print_elenco]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("AGENTE ANALISTA a processar a Parte 1..."):
                            # Lógica de upload e análise da Parte 1 viria aqui
                            # Simulação: Guardamos os resultados na memória (session_state)
                            st.session_state['contexto_dossie2'] = {'temporada': temporada, 'liga': liga, 'clube': clube}
                            st.session_state['jogadores_identificados'] = ["Jogador A (Atacante)", "Jogador B (Meio-campista)"]
                            st.rerun() # Reinicia o script para mostrar a Parte 2

        # --- PARTE 2: ANÁLISE DOS REFORÇOS ---
        if 'jogadores_identificados' in st.session_state:
            st.markdown("---")
            st.success("Análise Preliminar Concluída!")
            st.markdown("**Resultado da Análise (Saída da IA):**")
            st.info(f"""
            Com base nos dados fornecidos para o **{st.session_state['contexto_dossie2']['clube']}**, os seguintes reforços foram identificados como de alto impacto:
            - **{st.session_state['jogadores_identificados'][0]}**
            - **{st.session_state['jogadores_identificados'][1]}**
            """)

            with st.form("form_dossie_2_p2"):
                st.markdown("**Parte 2: Análise Aprofundada dos Reforços**")
                st.write("Por favor, forneça o 'Pacote de Prints' para cada jogador identificado abaixo.")

                # Cria campos de upload dinamicamente para cada jogador
                for jogador in st.session_state['jogadores_identificados']:
                    st.markdown(f"--- \n ##### Pacote de Prints para: **{jogador}**")
                    st.file_uploader(f"Print A: Perfil Quantitativo (Sofascore)*", key=f"{jogador}_A")
                    st.file_uploader(f"Print B: Perfil Funcional (Transfermarkt)*", key=f"{jogador}_B")
                    st.file_uploader(f"Print C: Perfil Tático / Mapa de Calor (Opcional)", key=f"{jogador}_C")
                
                if st.form_submit_button("Gerar Dossiê 2 Consolidado"):
                    # (A lógica final de upload e análise da Parte 2 viria aqui)
                    st.success("Simulação: Dossiê 2 final gerado com sucesso!")
                    st.balloons()
                    # Limpa a memória para um novo ciclo
                    del st.session_state['jogadores_identificados']
                    del st.session_state['contexto_dossie2']

    with tab3:
        st.info("Formulário para o Dossiê 3 em desenvolvimento.")
    with tab4:
        st.info("Formulário para o Dossiê 4 em desenvolvimento.")

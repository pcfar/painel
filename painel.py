import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v5.3", page_icon="🧠", layout="wide")

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

    # --- CENTRAL DE COMANDO ---
    st.header("Central de Comando")
    acao_usuario = st.selectbox("O que deseja fazer?", ["Selecionar...", "Criar um Novo Dossiê"])

    if acao_usuario == "Criar um Novo Dossiê":
        # --- ATUALIZAÇÃO: Adicionamos o Dossiê 2 à lista ---
        tipo_dossie = st.selectbox("Qual dossiê deseja criar?", ["Selecionar...", "Dossiê 1: Análise Geral da Liga", "Dossiê 2: Análise Aprofundada do Clube"])
        
        # --- FLUXO PARA DOSSIÊ 1 ---
        if tipo_dossie == "Dossiê 1: Análise Geral da Liga":
            with st.form("form_dossie_1"):
                st.subheader("Formulário do Dossiê 1: Análise Geral da Liga")
                temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
                liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
                
                prints_campeoes = st.file_uploader("1) Print(s) dos Últimos Campeões da Década*", accept_multiple_files=True, type=['png', 'jpg'])
                prints_classificacao = st.file_uploader("2) Print(s) da Classificação Final da Última Temporada*", accept_multiple_files=True, type=['png', 'jpg'])
                prints_curiosidades = st.file_uploader("3) Print(s) de Curiosidades (Opcional)", accept_multiple_files=True, type=['png', 'jpg'])
                
                if st.form_submit_button("Processar e Gerar Dossiê 1"):
                    # (Lógica de upload e análise do Dossiê 1)
                    st.info("Lógica do Dossiê 1 a ser executada...")


        # --- NOVO: FLUXO PARA DOSSIÊ 2 ---
        elif tipo_dossie == "Dossiê 2: Análise Aprofundada do Clube":
            with st.form("form_dossie_2"):
                st.subheader("Formulário do Dossiê 2: Análise Aprofundada do Clube")
                st.write("Preencha os campos e envie os 'prints' para a análise do clube-alvo.")

                temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
                liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
                clube = st.text_input("Clube (código)*", placeholder="Ex: FEY")

                st.markdown("---")

                print_stats_gerais = st.file_uploader("1) Print da Visão Geral de Estatísticas do Clube (FBref)*", accept_multiple_files=False, type=['png', 'jpg'])
                print_elenco = st.file_uploader("2) Print dos Detalhes do Elenco (Transfermarkt/Sofascore)*", accept_multiple_files=False, type=['png', 'jpg'])
                prints_analise_tatica = st.file_uploader("3) Print(s) de Análises Táticas / Mapas de Calor (Opcional)", accept_multiple_files=True, type=['png', 'jpg'])

                if st.form_submit_button("Processar e Gerar Dossiê 2"):
                    if not all([temporada, liga, clube, print_stats_gerais, print_elenco]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        # Lógica de upload e análise do Dossiê 2
                        with st.spinner("Processando Dossiê 2..."):
                            todos_os_prints = [print_stats_gerais, print_elenco] + prints_analise_tatica
                            temporada_fmt = temporada.replace('/', '-')
                            caminho_base = f"{temporada_fmt}/{liga.upper()}/{clube.upper()}/Dossie_2"
                            
                            # (A lógica completa de upload inteligente e análise OCR viria aqui)
                            st.success(f"Simulação: {len(todos_os_prints)} arquivos seriam salvos em `{caminho_base}` e analisados.")
                            st.balloons()

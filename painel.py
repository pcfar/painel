import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from datetime import datetime
import pytesseract
from PIL import Image
import io

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v7.0", page_icon="🧠", layout="wide")

# --- SISTEMA DE SENHA ÚNICA ---
def check_password():
    if st.session_state.get("password_correct", False): return True
    def password_entered():
        if st.session_state.get("password") == st.secrets.get("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
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
        st.subheader("Criar Dossiê 1: Análise Geral da Liga (Modelo Híbrido)")
        with st.form("form_dossie_1_hibrido"):
            st.write("Forneça o contexto e os 'prints' com dados técnicos. A IA será responsável pela pesquisa de dados históricos e contextuais.")

            # Inputs de Contexto
            temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            pais = st.text_input("País*", placeholder="Ex: Holanda")
            st.markdown("---")

            # Campos de Upload Guiados (agora apenas para dados técnicos)
            print_classificacao = st.file_uploader("1) Print da Tabela de Classificação Final*", help="Sugestão: No Sofascore ou FBref, capture a tabela de classificação completa da última temporada.", accept_multiple_files=True)
            print_stats = st.file_uploader("2) Print das Estatísticas Avançadas das Equipes*", help="Sugestão: No FBref, na página da temporada, capture a tabela 'Squad Advanced Stats'.", accept_multiple_files=True)

            if st.form_submit_button("Processar Prints e Preparar Prompt Híbrido para IA"):
                if not all([temporada, liga, pais, print_classificacao, print_stats]):
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    with st.spinner("AGENTE DE COLETA a processar 'prints' técnicos..."):
                        try:
                            # Agrupar e fazer OCR dos prints técnicos
                            textos_extraidos = {}
                            grupos_de_prints = {
                                "TABELA DE CLASSIFICAÇÃO FINAL": print_classificacao,
                                "ESTATÍSTICAS AVANÇADAS": print_stats
                            }
                            texto_final_para_prompt = ""
                            for nome_grupo, prints in grupos_de_prints.items():
                                if prints:
                                    texto_final_para_prompt += f"\n--- [INÍCIO DOS DADOS DO UTILIZADOR: {nome_grupo}] ---\n"
                                    for print_file in prints:
                                        imagem = Image.open(print_file)
                                        texto_final_para_prompt += pytesseract.image_to_string(imagem, lang='por+eng') + "\n"
                                    texto_final_para_prompt += f"--- [FIM DOS DADOS DO UTILIZADOR: {nome_grupo}] ---\n"

                            # Construir o Prompt Mestre Híbrido
                            data_hoje = datetime.now().strftime("%d/%m/%Y")
                            prompt_mestre = f"""

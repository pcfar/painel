import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io
import streamlit_authenticator as stauth
import copy

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Inteligência Tática", page_icon="🧠", layout="wide")

# --- SISTEMA DE AUTENTICAÇÃO ---
config = {
    'credentials': {
        'usernames': dict(st.secrets['credentials']['usernames'])
    },
    'cookie': dict(st.secrets['cookie'])
}

authenticator = stauth.Authenticate(
    config['credentials'],
    config['cookie']['name'],
    config['cookie']['key'],
    config['cookie']['expiry_days']
)

# --- Chamada da função de login na barra lateral ---
name, authentication_status, username = authenticator.login(location='sidebar')

# --- LÓGICA DE ACESSO ---
if authentication_status:
    # --- APLICAÇÃO PRINCIPAL (SÓ APARECE APÓS LOGIN) ---
    with st.sidebar:
        st.write(f'Bem-vindo, *{name}*!')
        authenticator.logout('Logout', location='sidebar', key='unique_key')

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

    # --- Função para listar o conteúdo de um diretório no GitHub ---
    @st.cache_data(ttl=60)
    def listar_conteudo_pasta(caminho):
        try:
            return repo.get_contents(caminho)
        except UnknownObjectException:
            return []
        except Exception:
            return []

    # --- CENTRAL DE UPLOAD (APENAS PARA ADMIN) ---
    if username == 'admin':
        st.header("1. Central de Upload e Organização")
        with st.expander("Clique aqui para enviar novos 'prints' para análise"):
            with st.form("form_upload_dossie", clear_on_submit=True):
                st.write("Preencha os dados abaixo para enviar os 'prints' para a análise correta.")
                temporada = st.text_input("Temporada:", placeholder="Ex: 2025 ou 2025-2026")
                tipo_dossie = st.selectbox("Selecione o Tipo de Dossiê:", ["Dossiê 1: Análise Geral da Liga", "Dossiê 2: Análise Aprofundada do Clube", "Dossiê 3: Briefing Pré-Jogo (Rodada)", "Dossiê 4: Análise Pós-Jogo (Rodada)"])
                liga_analisada = st.text_input("Liga ou País (código de 3 letras):", placeholder="Ex: HOL, ING, BRA")
                clube_analisado = st.text_input("Clube (código de 3 letras ou 'GERAL'):", placeholder="Ex: FEY, AJA, ou GERAL")
                rodada_dossie = st.text_input("Rodada (se aplicável):", placeholder="Ex: R01, R02...")
                arquivos_enviados = st.file_uploader("Upload dos 'prints':", accept_multiple_files=True, type=['png', 'jpg', 'jpeg'])
                submitted = st.form_submit_button("Enviar Arquivos para Análise")
                if submitted:
                    # (A lógica de upload completa será inserida aqui no próximo passo)
                    st.success("Lógica de upload a ser implementada.")

    # --- CENTRAL DE ANÁLISE (VISÍVEL PARA TODOS OS USUÁRIOS LOGADOS) ---
    st.markdown("---")
    st.header("2. Central de Análise: Gerar Dossiês")
    # (A lógica da Central de Análise completa será inserida aqui no próximo passo)
    st.info("Lógica de análise a ser implementada.")


elif authentication_status == False:
    with st.sidebar:
        st.error('Nome de utilizador/senha incorreto(a)')
elif authentication_status == None:
    with st.sidebar:
        st.warning('Por favor, introduza o seu nome de utilizador e senha')

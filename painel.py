import streamlit as st
import os
import requests
import base64

# Configuração da página
st.set_page_config(page_title="Central de Arquivo Tático", page_icon="📚", layout="wide")

# Carregamento de secrets
APP_PASSWORD = st.secrets["APP_PASSWORD"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO_NAME = st.secrets["GITHUB_REPO_NAME"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Autenticação simples
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if not st.session_state.authenticated:
    st.title("🔒 Painel de Acesso")
    password = st.text_input("Digite a senha para acessar o painel:", type="password")

    if password == APP_PASSWORD:
        st.session_state.authenticated = True
        st.success("✅ Acesso autorizado! Carregando painel...")
        st.experimental_rerun()
    elif password != "":
        st.error("❌ Senha incorreta.")
    st.stop()

# --- Funções auxiliares ---

def upload_markdown_file(file_content, path, commit_message="Upload de novo dossiê"):
    api_url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/contents/{path}"
    encoded_content = base64.b64encode(file_content.encode()).decode("utf-8")

    data = {
        "message": commit_message,
        "content": encoded_content
    }

    response = requests.put(api_url, json=data, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    return response

def list_markdown_files(repo_path="dossies"):
    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/contents/{repo_path}"
    response = requests.get(url, auth=(GITHUB_USERNAME, GITHUB_TOKEN))
    if response.status_code == 200:
        return response.json()
    return []

def download_markdown_file(file_path):
    url = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/main/{file_path}"
    response = requests.get(url)
    if response.status_code == 200:
        return response.text
    return "Erro ao carregar o arquivo."

# --- Layout principal ---
st.markdown("<h1 style='color:#FFD700'>📚 Central de Arquivo Tático</h1>", unsafe_allow_html=True)

aba = st.sidebar.radio("📁 Selecione o Módulo", ["📤 Upload de Dossiês", "📚 Biblioteca de Dossiês", "🧠 Geração (IA)"])

# --- ABA 1: Upload ---
if aba == "📤 Upload de Dossiês":
    st.header("📤 Upload de Novo Dossiê")
    tipo = st.selectbox("Tipo de Dossiê", ["Liga", "Clube", "Jogo", "Outro"])
    nome_arquivo = st.text_input("Nome do arquivo (sem .md):")
    conteudo_md = st.text_area("Conteúdo do Dossiê (.md)", height=400)
    enviar = st.button("🚀 Enviar para GitHub")

    if enviar:
        if nome_arquivo.strip() == "" or conteudo_md.strip() == "":
            st.warning("Preencha todos os campos.")
        else:
            caminho = f"dossies/{tipo.lower()}/{nome_arquivo}.md"
            r = upload_markdown_file(conteudo_md, caminho)
            if r.status_code in [200, 201]:
                st.success("✅ Dossiê enviado com sucesso!")
            else:
                st.error(f"Erro ao enviar: {r.json()}")

# --- ABA 2: Biblioteca ---
elif aba == "📚 Biblioteca de Dossiês":
    st.header("📚 Navegação pelos Dossiês")
    categorias = ["liga", "clube", "jogo", "outro"]

    categoria = st.selectbox("Escolha uma categoria:", categorias)
    arquivos = list_markdown_files(f"dossies/{categoria}")

    if arquivos:
        nomes = [arq['name'] for arq in arquivos if arq['name'].endswith(".md")]
        selecionado = st.selectbox("📄 Escolha um dossiê:", nomes)

        if selecionado:
            conteudo = download_markdown_file(f"dossies/{categoria}/{selecionado}")
            st.markdown("---")
            st.markdown(f"### 📘 {selecionado}", unsafe_allow_html=True)
            st.markdown(conteudo, unsafe_allow_html=True)
    else:
        st.info("Nenhum dossiê disponível nesta categoria.")

# --- ABA 3: Geração (placeholder) ---
elif aba == "🧠 Geração (IA)":
    st.header("🧠 Geração de Dossiês com IA")
    st.info("Funcionalidade em desenvolvimento.")

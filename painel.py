import streamlit as st
import requests
import base64
import os
from datetime import datetime

# Configuração da página
st.set_page_config(page_title="Central de Arquivo Tático", page_icon="📚", layout="wide")

# Estilo customizado para modo escuro e visual moderno
def custom_css():
    st.markdown("""
        <style>
            html, body, [class*="css"] {
                background-color: #0e1117 !important;
                color: #fafafa !important;
            }
            .markdown-body {
                font-family: 'Segoe UI', sans-serif;
                line-height: 1.7;
                font-size: 16px;
            }
            .markdown-body h1, .markdown-body h2, .markdown-body h3 {
                color: #f8f8f2;
                border-bottom: 1px solid #444;
                padding-bottom: 4px;
            }
            .markdown-body blockquote {
                color: #cccccc;
                border-left: 4px solid #666;
                margin-left: 0;
                padding-left: 1em;
                font-style: italic;
                background-color: #1e1e1e;
            }
            .markdown-body ul {
                list-style-type: '➤ ';
            }
            .markdown-body code {
                background-color: #2d2d2d;
                padding: 2px 4px;
                border-radius: 4px;
            }
            .css-1aumxhk {
                background-color: #0e1117;
            }
        </style>
    """, unsafe_allow_html=True)

custom_css()

# Autenticação por senha
def autenticar():
    if "autenticado" not in st.session_state:
        st.session_state.autenticado = False
    if not st.session_state.autenticado:
        senha = st.text_input("Digite a senha para acessar o painel:", type="password")
        if senha == st.secrets["APP_PASSWORD"]:
            st.session_state.autenticado = True
            st.success("Acesso autorizado!")
        else:
            st.warning("Senha incorreta. Acesso negado.")
        st.stop()

autenticar()

# Dados do repositório
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO_NAME = st.secrets["GITHUB_REPO_NAME"]

# Função de upload para GitHub
def upload_file_to_github(file, folder):
    now = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    file_name = f"{folder}/{now}_{file.name}"
    content = base64.b64encode(file.read()).decode("utf-8")

    url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/contents/{file_name}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    data = {
        "message": f"Upload automático: {file_name}",
        "content": content
    }
    response = requests.put(url, headers=headers, json=data)
    return response

# Função para visualizar Markdown com estilo
def render_markdown(md_text):
    st.markdown(f'<div class="markdown-body">{md_text}</div>', unsafe_allow_html=True)

# Sidebar com navegação
st.sidebar.title("📁 Navegação")
abas = ["📤 Upload de Dossiês", "📚 Biblioteca de Dossiês", "🤖 Geração por IA (em breve)"]
aba = st.sidebar.radio("Escolha uma seção", abas)

# ------------------------------
# 📤 ABA 1: UPLOAD DE DOSSIÊS
# ------------------------------
if aba == "📤 Upload de Dossiês":
    st.title("📤 Upload de Dossiês para o Arquivo Central")

    tipo = st.selectbox("Tipo de dossiê:", ["Selecione", "Clube", "Rodada", "Liga", "Análise Livre"])
    uploaded_file = st.file_uploader("Escolha um arquivo .md", type=["md"])

    if uploaded_file and tipo != "Selecione":
        if st.button("📤 Enviar para o Repositório"):
            with st.spinner("Enviando para o repositório GitHub..."):
                res = upload_file_to_github(uploaded_file, tipo.lower())
                if res.status_code == 201:
                    st.success("✅ Upload realizado com sucesso!")
                else:
                    st.error(f"❌ Erro no upload: {res.status_code}")
                    st.code(res.json(), language="json")
    elif tipo == "Selecione":
        st.info("Selecione o tipo de dossiê antes de enviar.")

# ------------------------------
# 📚 ABA 2: BIBLIOTECA DE DOSSIÊS
# ------------------------------
elif aba == "📚 Biblioteca de Dossiês":
    st.title("📚 Biblioteca de Dossiês")

    def listar_arquivos(pasta):
        url = f"https://api.github.com/repos/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/contents/{pasta}"
        headers = {"Authorization": f"token {GITHUB_TOKEN}"}
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            return [f["name"] for f in response.json() if f["name"].endswith(".md")]
        return []

    abas_dossies = st.columns(4)
    pastas = ["clube", "rodada", "liga", "analise_livre"]

    with st.sidebar:
        st.markdown("### 🔍 Escolha um tipo de dossiê:")
        tipo_escolhido = st.selectbox("Tipo de dossiê", pastas)

        if tipo_escolhido:
            arquivos = listar_arquivos(tipo_escolhido)
            arquivo_escolhido = st.selectbox("Escolha o dossiê:", arquivos)

            if arquivo_escolhido:
                url_raw = f"https://raw.githubusercontent.com/{GITHUB_USERNAME}/{GITHUB_REPO_NAME}/main/{tipo_escolhido}/{arquivo_escolhido}"
                conteudo_md = requests.get(url_raw).text
                st.markdown(f"### 📄 {arquivo_escolhido}")
                render_markdown(conteudo_md)

# ------------------------------
# 🤖 ABA 3: IA (em breve)
# ------------------------------
elif aba == "🤖 Geração por IA (em breve)":
    st.title("🤖 Geração Automática por IA")
    st.info("Esta funcionalidade será ativada em breve com a API Gemini.")


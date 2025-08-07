import streamlit as st
import os
from github import Github
from datetime import datetime

# Carrega segredos do .streamlit/secrets.toml
APP_PASSWORD = st.secrets["APP_PASSWORD"]
GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
GITHUB_REPO_NAME = st.secrets["GITHUB_REPO_NAME"]
GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]

# Configuração inicial
st.set_page_config(page_title="Central de Arquivo Tático", page_icon="📚", layout="wide")
st.markdown("<style>body { background-color: #0e1117; color: #f0f0f0; }</style>", unsafe_allow_html=True)

# Função para baixar markdown de um repositório do GitHub
def download_markdown_file(repo, path):
    file_content = repo.get_contents(path)
    return file_content.decoded_content.decode("utf-8")

# Verificação de login
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

if not st.session_state["authenticated"]:
    st.title("🔐 Painel de Arquivo de Inteligência")
    senha = st.text_input("Digite a senha para acessar o painel:", type="password")
    if senha == APP_PASSWORD:
        st.session_state["authenticated"] = True
        st.success("Acesso autorizado. Painel liberado!")
        st.experimental_set_query_params(auth="true")
        st.stop()
    elif senha:
        st.error("Senha incorreta.")
    st.stop()

# Painel principal
st.sidebar.title("📂 Menu do Painel")
aba = st.sidebar.radio("Escolha a função:", ["🔍 Visualizar Dossiês", "📤 Subir Novo Dossiê", "🧠 (Em breve) Geração com IA"])

if aba == "🔍 Visualizar Dossiês":
    st.title("📖 Navegação de Dossiês")
    gh = Github(GITHUB_TOKEN)
    repo = gh.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPO_NAME)
    
    arquivos_md = [f.path for f in repo.get_contents("") if f.path.endswith(".md")]
    if arquivos_md:
        dossie_selecionado = st.selectbox("Selecione um dossiê:", arquivos_md)
        conteudo_md = download_markdown_file(repo, dossie_selecionado)
        st.markdown("---")
        st.markdown(f"### 📝 {dossie_selecionado}")
        st.markdown(conteudo_md, unsafe_allow_html=True)
    else:
        st.info("Nenhum dossiê encontrado no repositório.")

elif aba == "📤 Subir Novo Dossiê":
    st.title("📤 Upload de Dossiê para o GitHub")
    nome_arquivo = st.text_input("Nome do arquivo (ex: dossie_brasileirao.md):")
    conteudo = st.text_area("Conteúdo do dossiê em Markdown:", height=300)
    
    if st.button("Enviar para o repositório"):
        if nome_arquivo and conteudo:
            try:
                gh = Github(GITHUB_TOKEN)
                repo = gh.get_user(GITHUB_USERNAME).get_repo(GITHUB_REPO_NAME)
                data = datetime.now().strftime("%Y-%m-%d %H:%M")
                repo.create_file(nome_arquivo, f"Upload via painel em {data}", conteudo)
                st.success(f"Dossiê '{nome_arquivo}' enviado com sucesso!")
            except Exception as e:
                st.error(f"Erro ao enviar: {e}")
        else:
            st.warning("Preencha o nome e o conteúdo do dossiê.")

elif aba == "🧠 (Em breve) Geração com IA":
    st.title("🧠 Geração Inteligente de Dossiês (Em breve)")
    st.info("Este módulo será ativado em breve com integração à IA para geração automatizada de dossiês táticos.")

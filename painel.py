import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v5.2", page_icon="🧠", layout="wide")

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
        tipo_dossie = st.selectbox("Qual dossiê deseja criar?", ["Selecionar...", "Dossiê 1: Análise Geral da Liga"])
        
        if tipo_dossie == "Dossiê 1: Análise Geral da Liga":
            with st.form("form_dossie_1"):
                st.subheader("Formulário do Dossiê 1: Análise Geral da Liga")
                temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
                liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
                
                prints_campeoes = st.file_uploader("1) Print(s) dos Últimos Campeões da Década*", accept_multiple_files=True, type=['png', 'jpg'])
                prints_classificacao = st.file_uploader("2) Print(s) da Classificação Final da Última Temporada*", accept_multiple_files=True, type=['png', 'jpg'])
                prints_curiosidades = st.file_uploader("3) Print(s) de Curiosidades (Opcional)", accept_multiple_files=True, type=['png', 'jpg'])
                
                submitted = st.form_submit_button("Processar e Gerar Dossiê 1")

                if submitted:
                    todos_os_prints = []
                    if prints_campeoes: todos_os_prints.extend(prints_campeoes)
                    if prints_classificacao: todos_os_prints.extend(prints_classificacao)
                    if prints_curiosidades: todos_os_prints.extend(prints_curiosidades)

                    if not all([temporada, liga, todos_os_prints]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("Iniciando processo... AGENTE DE COLETA ativado."):
                            try:
                                temporada_fmt = temporada.replace('/', '-')
                                caminho_base = f"{temporada_fmt}/{liga.upper()}/GERAL/Dossie_1"
                                
                                for arq in todos_os_prints:
                                    conteudo_arquivo = arq.getvalue()
                                    caminho_repo = os.path.join(caminho_base, arq.name)
                                    commit_message = f"Upload/Update Dossiê 1: {arq.name}"

                                    # --- LÓGICA DE UPLOAD INTELIGENTE ---
                                    try:
                                        # Tenta obter o arquivo para ver se ele já existe
                                        arquivo_existente = repo.get_contents(caminho_repo)
                                        # Se existir, atualiza
                                        repo.update_file(caminho_repo, commit_message, conteudo_arquivo, arquivo_existente.sha)
                                        st.info(f"Arquivo `{arq.name}` atualizado com sucesso!")
                                    except UnknownObjectException:
                                        # Se não existir, cria
                                        repo.create_file(caminho_repo, commit_message, conteudo_arquivo)
                                        st.success(f"Arquivo `{arq.name}` criado com sucesso!")
                                
                                st.balloons()
                                st.header("Upload Concluído!")

                            except GithubException as e:
                                st.error(f"Ocorreu um erro na API do GitHub: {e.data['message']}")
                            except Exception as e:
                                st.error(f"Ocorreu um erro inesperado durante o upload: {e}")
                                st.stop()

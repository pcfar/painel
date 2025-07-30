import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático", page_icon="🧠", layout="wide")

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

    # --- Funções Auxiliares ---
    @st.cache_data(ttl=60)
    def listar_conteudo_pasta(caminho):
        try:
            return [item for item in repo.get_contents(caminho) if not item.name.startswith('.')]
        except UnknownObjectException:
            return []

    # --- CENTRAL DE COMANDO COM ABAS ---
    st.header("Central de Comando")
    tab1, tab2 = st.tabs(["🗂️ Arquivar Novo Dossiê", "👀 Visualizar Dossiês"])

    # --- ABA DE ARQUIVAMENTO ---
    with tab1:
        st.subheader("Arquivar Dossiê Finalizado")
        with st.form("form_arquivar"):
            st.write("Cole o conteúdo do dossiê em Markdown gerado pelo seu assistente de IA.")
            
            temporada = st.text_input("Temporada*", placeholder="Ex: 2025-2026")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            clube = st.text_input("Clube (código ou 'GERAL')*", placeholder="Ex: FEY")
            nome_arquivo = st.text_input("Nome do Arquivo (sem .md)*", placeholder="Ex: Dossie_1_Analise_Liga")
            
            conteudo_dossie = st.text_area("Conteúdo do Dossiê em Markdown*", height=400)
            
            if st.form_submit_button("Salvar Dossiê no Repositório"):
                if not all([temporada, liga, clube, nome_arquivo, conteudo_dossie]):
                    st.error("Por favor, preencha todos os campos obrigatórios.")
                else:
                    with st.spinner("A arquivar o dossiê..."):
                        try:
                            temporada_fmt = temporada.replace('/', '-')
                            caminho_final = f"{temporada_fmt}/{liga.upper()}/{clube.upper()}/{nome_arquivo}.md"
                            commit_message = f"Arquiva: {nome_arquivo}.md"
                            
                            try:
                                arquivo_existente = repo.get_contents(caminho_final)
                                repo.update_file(caminho_final, commit_message, conteudo_dossie, arquivo_existente.sha)
                                st.info(f"Dossiê `{caminho_final}` atualizado com sucesso!")
                            except UnknownObjectException:
                                repo.create_file(caminho_final, commit_message, conteudo_dossie)
                                st.success(f"Dossiê `{caminho_final}` criado com sucesso!")
                            st.balloons()
                        except Exception as e:
                            st.error(f"Ocorreu um erro ao salvar: {e}")

    # --- ABA DE VISUALIZAÇÃO ---
    with tab2:
        st.subheader("Navegar e Visualizar Dossiês Arquivados")
        
        temporadas = [item.path for item in listar_conteudo_pasta("") if item.type == "dir"]
        if not temporadas:
            st.info("Nenhum dossiê arquivado. Comece arquivando um novo dossiê.")
        else:
            sel_temporada = st.selectbox("Temporada:", [""] + temporadas)
            if sel_temporada:
                ligas = [item.name for item in listar_conteudo_pasta(sel_temporada) if item.type == "dir"]
                if ligas:
                    sel_liga = st.selectbox("Liga:", [""] + ligas)
                    if sel_liga:
                        path_liga = os.path.join(sel_temporada, sel_liga)
                        clubes = [item.name for item in listar_conteudo_pasta(path_liga) if item.type == "dir"]
                        if clubes:
                            sel_clube = st.selectbox("Clube/Alvo:", [""] + clubes)
                            if sel_clube:
                                path_clube = os.path.join(path_liga, sel_clube)
                                dossies = [item for item in listar_conteudo_pasta(path_clube) if item.name.endswith('.md')]
                                if not dossies:
                                    st.warning("Nenhum dossiê em Markdown encontrado nesta pasta.")
                                else:
                                    nomes_dossies = [d.name for d in dossies]
                                    sel_dossie = st.selectbox("Selecione o Dossiê para ler:", nomes_dossies)
                                    if sel_dossie:
                                        with st.spinner("A carregar o dossiê..."):
                                            conteudo = repo.get_contents(os.path.join(path_clube, sel_dossie))
                                            st.markdown("---")
                                            st.markdown(conteudo.decoded_content.decode("utf-8"))

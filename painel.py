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
    # (Lógica da Central de Comando como antes, com a correção do 'help')
    tipo_dossie = st.selectbox("Qual dossiê deseja criar?", ["Selecionar...", "Dossiê 1: Análise Geral da Liga"])
    if tipo_dossie == "Dossiê 1: Análise Geral da Liga":
        with st.form("form_dossie_1"):
            st.subheader("Formulário do Dossiê 1: Análise Geral da Liga")
            temporada = st.text_input("Temporada*", placeholder="Ex: 2024-2025")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            
            # --- CORREÇÃO: Adicionando o 'help' ---
            st.file_uploader("1) Print(s) dos Campeões*", accept_multiple_files=True, type=['png', 'jpg'], help="Sugestão: Na Wikipedia, capture a tabela dos últimos 10 campeões da liga.")
            st.file_uploader("2) Print(s) da Classificação Final*", accept_multiple_files=True, type=['png', 'jpg'], help="Sugestão: No Sofascore ou FBref, capture a tabela de classificação completa da última temporada.")
            st.file_uploader("3) Print(s) de Curiosidades", accept_multiple_files=True, type=['png', 'jpg'], help="Sugestão: Site oficial da liga, Wikipedia (recordes, artilheiros, etc.).")
            
            if st.form_submit_button("Processar e Gerar Dossiê 1"):
                # Lógica de upload (simplificada para o exemplo)
                st.success("Lógica de upload executada.")


    # --- ÁREA DE ADMINISTRAÇÃO ---
    st.sidebar.markdown("---")
    st.sidebar.header("Área de Administração")

    # --- NOVA FERRAMENTA DE LIMPEZA ---
    with st.sidebar.expander("🗑️ Ferramenta de Limpeza do Repositório"):
        st.warning("Atenção: A exclusão de arquivos e pastas é permanente.")
        
        try:
            # Lista apenas os itens que criamos para teste
            conteudo_raiz = repo.get_contents("")
            itens_para_limpeza = [
                item.path for item in conteudo_raiz 
                if item.path in ['teste_subpasta', 'prints_para_analise', 'config.yaml', 'Captura de tela 2025-07-29 012554.png']
            ]
            
            if not itens_para_limpeza:
                st.info("Nenhum item de teste para limpar.")
            else:
                selecionados_para_excluir = st.multiselect("Selecione os itens para excluir:", itens_para_limpeza)
                if st.button("Excluir Itens Selecionados"):
                    with st.spinner("A excluir itens..."):
                        for item_path in selecionados_para_excluir:
                            try:
                                contents = repo.get_contents(item_path)
                                # Se for uma pasta, exclui todos os arquivos dentro
                                if isinstance(contents, list):
                                    for content_file in contents:
                                        repo.delete_file(content_file.path, f"Admin: Exclui {content_file.name}", content_file.sha)
                                # Se for um arquivo, exclui diretamente
                                else:
                                    repo.delete_file(contents.path, f"Admin: Exclui {contents.name}", contents.sha)
                                st.success(f"`{item_path}` excluído com sucesso.")
                            except Exception as e:
                                st.error(f"Erro ao excluir `{item_path}`: {e}")
                        st.rerun()

        except Exception as e:
            st.error(f"Erro ao listar itens para limpeza: {e}")

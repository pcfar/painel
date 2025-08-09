# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v17.5: Correção Definitiva de Temas Dinâmicos
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import os
from streamlit_option_menu import option_menu
import markdown2
import re

# --- 1. CONFIGURAÇÃO E ESTILOS FINAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }

            .dossier-viewer { line-height: 1.7; font-size: 1.1rem; color: #F3F4F6; }
            .dossier-viewer p { color: #F3F4F6; }
            .dossier-viewer li { padding-left: 1.5em; text-indent: -1.5em; margin-bottom: 1rem; }
            .dossier-viewer hr { border: none; border-top: 2px solid #4A5568; margin: 3rem 0; }
            .dossier-viewer table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background-color: #2D3748; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); }
            .dossier-viewer th, .dossier-viewer td { padding: 1rem; text-align: left; font-size: 1rem; color: #F3F4F6; border-bottom: 1px solid #4A5568;}
            .dossier-viewer td { color: #CBD5E0; }
            .dossier-viewer tr:nth-child(even) { background-color: rgba(74, 85, 104, 0.5); }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; }

            .dossier-viewer h1 { text-align: center; font-size: 2.2rem; font-weight: 900; color: #FFFFFF; padding-bottom: 0.5rem; margin-bottom: 2rem; }
            .dossier-viewer h2 { font-size: 1.7rem; font-weight: 700; margin-top: 3rem; margin-bottom: 1.5rem; padding-left: 1rem; }
            .dossier-viewer h3 { font-size: 1.4rem; font-weight: 700; margin-top: 2.5rem; margin-bottom: 1rem; }

            .dossier-viewer.theme-d1 h1 { border-bottom: 3px solid #3182CE; }
            .dossier-viewer.theme-d1 h2 { color: #38BDF8; border-left: 4px solid #38BDF8; }
            .dossier-viewer.theme-d1 h3, .dossier-viewer.theme-d1 strong { color: #FACC15; }
            .dossier-viewer.theme-d1 li::before { content: "▪"; color: #63B3ED; margin-right: 12px; font-size: 1.2rem; }
            .dossier-viewer.theme-d1 table th { background-color: #3182CE; }

            .dossier-viewer.theme-d2p1 h1 { border-bottom: 3px solid #10B981; }
            .dossier-viewer.theme-d2p1 h2 { color: #34D399; border-left: 4px solid #34D399; }
            .dossier-viewer.theme-d2p1 h3, .dossier-viewer.theme-d2p1 strong { color: #A3E4D3; }
            .dossier-viewer.theme-d2p1 li::before { content: "›"; color: #34D399; margin-right: 12px; font-size: 1.5rem; font-weight: 700; }
            .dossier-viewer.theme-d2p1 table th { background-color: #10B981; }

            .dossier-viewer.theme-d2p2 h1 { border-bottom: 3px solid #DC2626; }
            .dossier-viewer.theme-d2p2 h2 { color: #F87171; border-left: 4px solid #F87171; }
            .dossier-viewer.theme-d2p2 h3, .dossier-viewer.theme-d2p2 strong { color: #F97316; }
            .dossier-viewer.theme-d2p2 li::before { content: "»"; color: #F87171; margin-right: 12px; font-size: 1.5rem; font-weight: 700; }
            .dossier-viewer.theme-d2p2 table th { background-color: #DC2626; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES AUXILIARES ---
def sanitize_text(text: str) -> str:
    return text.replace('\u00A0', ' ').replace('\u2011', '-')

@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}")
    except Exception as e:
        st.error(f"Falha na conexão com o GitHub: {e}")
        return None

def check_password():
    if st.session_state.get("password_correct", False): return True
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.title("Painel de Inteligência")
        st.write(" ")
        with st.container(border=True):
            st.subheader("Login de Acesso")
            password = st.text_input("Senha de Acesso", type="password", key="password_input", label_visibility="collapsed", placeholder="Digite sua senha")
            if st.button("Acessar Painel", type="primary", use_container_width=True):
                with st.spinner("Verificando..."):
                    if password == st.secrets.get("APP_PASSWORD"):
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
    return False

def display_repo_structure(repo, path=""):
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md")], key=lambda x: x.name)
        search_term = st.session_state.get("search_term", "")
        if search_term:
            files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"):
                display_repo_structure(repo, content_dir.path)
        for content_file in files:
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8")
                    st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
            with col2:
                if st.button("✏️", key=f"edit_{content_file.path}", help="Editar Dossiê", use_container_width=True):
                    st.warning("Função de edição em desenvolvimento.")
            with col3:
                if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir Dossiê", use_container_width=True):
                    st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}
                    st.rerun()
            if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                st.warning(f"Excluir `{content_file.path}`?")
                btn_c1, btn_c2 = st.columns(2)
                if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                    file_info = st.session_state.pop('file_to_delete')
                    repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                    if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']):
                                                st.session_state.pop('viewing_file_content', None)
                        st.session_state.pop('viewing_file_name', None)
                    st.success(f"Arquivo '{file_info['path']}' excluído.")
                    st.rerun()
                if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"):
                    st.session_state.pop('file_to_delete')
                    st.rerun()
    except Exception as e:
        st.error(f"Erro ao listar arquivos: {e}")

def save_dossier(repo, file_name_template: str, path_parts: list, content: str, required_fields: dict):
    if not all(required_fields.values()):
        st.error("Todos os campos marcados com * são obrigatórios.")
        return
    format_dict = {k: v.replace(' ', '_') for k, v in required_fields.items() if k in ['liga', 'pais', 'clube', 'temporada']}
    file_name = file_name_template.format(**format_dict) + ".md"
    final_path_parts = [p.replace(" ", "_") for p in path_parts]
    full_path = "/".join(final_path_parts) + "/" + file_name
    commit_message = f"Adiciona: {file_name}"
    with st.spinner("Salvando dossiê..."):
        try:
            repo.create_file(full_path, commit_message, content)
            st.success(f"Dossiê '{full_path}' salvo com sucesso!")
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar: {e}")
            st.info("Verifique se um arquivo com este nome já não existe.")

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---
if not check_password():
    st.stop()

apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês")
    default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(
        menu_title="Menu Principal",
        options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"],
        icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"],
        menu_icon="collection-play",
        default_index=default_index,
        key="main_menu"
    )
    st.session_state.selected_action = selected_action

st.title("Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório")
            st.text_input("Filtrar...", label_visibility="collapsed", placeholder="Filtrar por nome do arquivo...", key="search_term")
            st.divider()
            display_repo_structure(repo)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                content_raw = sanitize_text(st.session_state["viewing_file_content"])

                # Detecta tema no conteúdo
                match = re.search(r'<!--\s*tema:\s*(\w+)\s*-->', content_raw)
                theme_class = f'theme-{match.group(1)}' if match else 'theme-d1'

                # Converte Markdown para HTML
                html_content = markdown2.markdown(content_raw)

                # Renderiza com estilo aplicado
                st.markdown(f"#### {file_name}")
                st.divider()
                st.markdown(f'<div class="dossier-viewer {theme_class}">{html_content}</div>', unsafe_allow_html=True)
def generate_toc(markdown_text):
    headers = re.findall(r'^(#{2,3})\s+(.*)', markdown_text, re.MULTILINE)
    toc = ""
    for level, title in headers:
        anchor = re.sub(r'\s+', '-', title.lower())
        indent = " " if level == "###" else ""
        toc += f"{indent}- [{title}](#{anchor})\n"
    return markdown2.markdown(toc)

# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v14.5: Simplificação e Correção dos Formulários
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import os
from streamlit_option_menu import option_menu
import markdown2

# --- 1. CONFIGURAÇÃO E ESTILOS (Estável) ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            .dossier-viewer { line-height: 1.8; font-size: 1.1rem; color: #E2E8F0; }
            .dossier-viewer h1 { font-size: 2.2rem; font-weight: 900; color: #FFFFFF; border-bottom: 3px solid #3182CE; padding-bottom: 0.5rem; margin-bottom: 2rem; }
            .dossier-viewer h2 { font-size: 1.6rem; font-weight: 700; color: #E2E8F0; margin-top: 2.5rem; margin-bottom: 1.5rem; border-bottom: 1px solid #4A5568; padding-bottom: 0.5rem;}
            .dossier-viewer h3 { font-size: 1.3rem; font-weight: 700; color: #a5b4fc; margin-top: 2rem; margin-bottom: 1rem; }
            .dossier-viewer p { margin-bottom: 1rem; color: #A0AEC0; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer blockquote { border-left: 4px solid #63b3ed; padding: 10px 20px; margin-left: 0; background-color: rgba(49, 130, 206, 0.1); border-radius: 8px;}
            .dossier-viewer ul { list-style-type: none; padding-left: 0; margin-top: 1rem; }
            .dossier-viewer li { margin-bottom: 0.7rem; color: #A0AEC0; padding-left: 1.5em; text-indent: -1.5em; }
            .dossier-viewer li::before { content: "▪"; color: #63B3ED; margin-right: 10px; font-size: 1.2rem; }
            .dossier-viewer hr { border: none; border-top: 2px solid #4A5568; margin: 3rem 0; }
            .dossier-viewer table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background-color: #2D3748; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); }
            .dossier-viewer th, .dossier-viewer td { padding: 1rem; text-align: left; font-size: 1rem; color: #F3F4F6; border-bottom: 1px solid #4A5568;}
            .dossier-viewer th { background-color: #3B82F6; font-weight: 700; }
            .dossier-viewer tr:nth-child(even) { background-color: rgba(74, 85, 104, 0.5); }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES AUXILIARES (Estável) ---
def sanitize_text(text: str) -> str:
    text = text.replace('\u00A0', ' ').replace('\u2011', '-')
    return text
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password():
    if st.session_state.get("password_correct", False): return True
    _, center_col, _ = st.columns([1, 1, 1]);
    with center_col:
        st.title("Painel de Inteligência"); st.write(" ")
        with st.container(border=True):
            st.subheader("Login de Acesso"); password = st.text_input("Senha de Acesso", type="password", key="password_input", label_visibility="collapsed", placeholder="Digite sua senha")
            if st.button("Acessar Painel", type="primary", use_container_width=True):
                with st.spinner("Verificando..."):
                    if password == st.secrets.get("APP_PASSWORD"): st.session_state["password_correct"] = True; st.rerun()
                    else: st.error("Senha incorreta.")
    return False
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    # Lógica de exibição de arquivos (sem alterações)
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and (f.name.endswith(".yml") or f.name.endswith(".md"))], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                with c1:
                    if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                        file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                with c3:
                    if st.button("✏️", key=f"edit_{content_file.path}", help="Editar (desabilitado)", use_container_width=True): st.warning("A edição será reimplementada.")
                with c4:
                    if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir", use_container_width=True): st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                    st.warning(f"Excluir `{content_file.path}`?"); btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                        file_info = st.session_state.pop('file_to_delete'); repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                        if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content', None); st.session_state.pop('viewing_file_name', None)
                        st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                    if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
    except Exception as e: st.error(f"Erro ao listar arquivos: {e}")

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---
if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês"); default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index, key="main_menu")
    st.session_state.selected_action = selected_action

st.title("Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês"); st.text("Navegue e visualize os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório"); search_term = st.text_input("Filtrar...", label_visibility="collapsed", placeholder="Filtrar por nome do arquivo..."); st.divider()
            display_repo_structure(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}"); st.divider()
                sanitized_content = sanitize_text(st.session_state.viewing_file_content)
                html_content = markdown2.markdown(sanitized_content, extras=['tables', 'fenced-code-blocks', 'blockquote'])
                st.markdown(f"<div class='dossier-viewer'>{html_content}</div>", unsafe_allow_html=True)
            else: st.info("Selecione um arquivo para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê"); st.info("Selecione o tipo de dossiê, preencha as informações e o conteúdo em Markdown.")
    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes da Liga", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")
    
    help_text_md = "Guia Rápido de Formatação:\n- Título Principal: # Título\n- Subtítulo: ## Subtítulo\n- Listas: - Item da lista\n- Destaque: **texto**\n- Citação: > texto"

    # Template 1: Dossiê de Liga
    if dossier_type == "D1 P1 - Análise da Liga":
        with st.form("d1_p1_form", clear_on_submit=True):
            st.subheader("Template: Análise da Liga"); c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*")
            liga = c2.text_input("Liga*")
            temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Resumo (Conteúdo do Dossiê)*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"):
                if not all([pais, liga, temporada, conteudo]):
                    st.error("Todos os campos * são obrigatórios.")
                else:
                    file_name = f"D1P1_Analise_Liga_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.md"
                    path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                    with st.spinner("Salvando..."):
                        try:
                            repo.create_file(full_path, f"Adiciona: {file_name}", conteudo); st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                        except Exception as e: st.error(f"Ocorreu um erro ao salvar: {e}")

    # Template 2: Clubes Dominantes (SIMPLIFICADO)
    elif dossier_type == "D1 P2 - Análise dos Clubes Dominantes da Liga":
        with st.form("d1_p2_form", clear_on_submit=True):
            st.subheader("Template: Análise dos Clubes Dominantes")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*")
            liga = c2.text_input("Liga*")
            temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Resumo (Conteúdo da Análise)*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"):
                if not all([pais, liga, temporada, conteudo]):
                    st.error("Todos os campos * são obrigatórios.")
                else:
                    file_name = f"D1P2_Clubes_Dominantes_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.md"
                    path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                    with st.spinner("Salvando..."):
                        try:
                            repo.create_file(full_path, f"Adiciona: {file_name}", conteudo); st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                        except Exception as e: st.error(f"Ocorreu um erro ao salvar: {e}")

    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

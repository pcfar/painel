# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - Versão com Navegador de Arquivos em Ambas as Páginas
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """Aplica o design "Modo Tático" refinado."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');
            
            body, .main, [data-testid="stSidebar"] {
                font-family: 'Roboto', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }

            .form-card {
                background-color: #2D3748; padding: 25px; border-radius: 12px;
                box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2);
                border: 1px solid #4A5568; margin-bottom: 25px;
            }

            .st-emotion-cache-1629p8f label {
                color: #A0AEC0; font-weight: 400; font-size: 0.9rem;
            }
            
            .stButton>button[kind="primary"] {
                height: 3rem; font-size: 1.1rem; font-weight: 700;
                border-radius: 8px; transition: all 0.3s ease-in-out;
            }
            .stButton>button[kind="primary"]:hover {
                box-shadow: 0 0 20px 0 rgba(49, 130, 206, 0.6);
            }
            /* Demais estilos... */
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; transition: all 0.3s ease-in-out !important; }
            .nav-link:hover { background-color: #4A5568 !important; }
            .nav-link-selected { box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2); }
            .dossier-viewer { line-height: 1.8; color: #E2E8F0; }
            .dossier-viewer h3 { border-bottom: 2px solid #3182CE; padding-bottom: 8px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. AUTENTICAÇÃO E CONEXÃO ---
@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password():
    if st.session_state.get("password_correct", False): return True
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Painel de Inteligência"); password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"):
                st.session_state["password_correct"] = True; st.rerun()
            else: st.error("😕 Senha incorreta.")
    return False

# --- 3. LÓGICA DE NAVEGAÇÃO E PARSING ---
def parse_path_to_form(path):
    try:
        parts = [p for p in path.split('/') if p]; file_name = parts[-1]
        st.session_state.update(pais=parts[0].replace("_", " "), liga=parts[1].replace("_", " "), temporada=parts[2])
        if file_name == "Dossiê_Liga.md": st.session_state.tipo_dossie = "Dossiê de Liga"
        elif file_name == "Dossiê_Clube.md": st.session_state.update(tipo_dossie="Dossiê de Clube", clube=parts[3].replace("_", " "))
        elif file_name in ["Briefing_Pre-Jogo.md", "Relatorio_Pos-Jogo.md"]:
            st.session_state.update(tipo_dossie="Briefing Pré-Jogo" if file_name.startswith("Briefing") else "Relatório Pós-Jogo", clube=parts[3].replace("_", " "), rodada=parts[4].replace("_", " "))
    except Exception: st.warning("Não foi possível analisar o caminho do arquivo.")

# --- NOVA FUNÇÃO MESTRE PARA EXIBIR A ESTRUTURA DO REPOSITÓRIO ---
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    """
    Exibe a estrutura de pastas e arquivos do repositório de forma recursiva.
    - repo: O objeto do repositório do GitHub.
    - path: O caminho atual a ser explorado.
    - search_term: O termo para filtrar os arquivos.
    - show_actions: Booleano para exibir ou não os botões de ação (Visualizar, Editar, Excluir).
    """
    try:
        contents = repo.get_contents(path)
        # Separa diretórios de arquivos
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md")], key=lambda x: x.name)

        # Renderiza os diretórios (pastas) como expanders
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"):
                display_repo_structure(repo, content_dir.path, search_term, show_actions)

        # Filtra e renderiza os arquivos
        if search_term:
            files = [f for f in files if search_term.lower() in f.name.lower()]
        
        for content_file in files:
            if show_actions:
                # Layout com ações para a página "Leitor de Dossiês"
                c1, c2, c3 = st.columns([3, 1, 1])
                c1.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", on_click=lambda c=content_file: st.session_state.update(viewing_file_content=base64.b64decode(c.content).decode('utf-8'), viewing_file_name=c.name), use_container_width=True)
                if c2.button("✏️", key=f"edit_{content_file.path}", help="Editar este arquivo"):
                    parse_path_to_form(content_file.path)
                    st.session_state.update(edit_mode=True, file_to_edit_path=content_file.path, conteudo_md=base64.b64decode(content_file.content).decode('utf-8'), selected_action="Carregar Dossiê")
                    st.rerun()
                if c3.button("🗑️", key=f"delete_{content_file.path}", help="Excluir este arquivo"):
                    st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                # Lógica de confirmação de exclusão
                if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                    st.warning(f"Excluir `{content_file.path}`?")
                    btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                        file_info = st.session_state.pop('file_to_delete')
                        repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                        if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content'); st.session_state.pop('viewing_file_name')
                        st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                    if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
            else:
                # Layout simples, apenas para visualização, para a página "Carregar Dossiê"
                st.markdown(f"📄 `{content_file.name}`")

    except Exception as e: st.error(f"Erro ao listar arquivos em '{path}': {e}")


# --- INÍCIO DA EXECUÇÃO DA APLICAÇÃO ---
if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês")
    default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index)
    st.session_state.selected_action = selected_action

st.title("⚽ Sistema de Inteligência Tática")

# ---- PÁGINA 1: LEITOR DE DOSSIÊS ----
if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês"); st.text("Navegue, filtre e visualize todos os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Navegador do Repositório")
            search_term = st.text_input("🔎 Filtrar por nome...", key="search_term_reader", label_visibility="collapsed", placeholder="🔎 Filtrar por nome do arquivo...")
            st.divider()
            # Chama a função mestre com ações habilitadas
            display_repo_structure(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if "viewing_file_content" in st.session_state:
                st.markdown(f"#### {st.session_state.viewing_file_name}"); st.divider()
                cleaned_content = re.sub(r':contentReference\[.*?\]\{.*?\}', '', st.session_state.viewing_file_content)
                st.markdown(f"<div class='dossier-viewer'>{cleaned_content}</div>", unsafe_allow_html=True)
            else: st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")

# ---- PÁGINA 2: CARREGAR DOSSIÊ (COM NAVEGADOR INTEGRADO) ----
elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get('edit_mode', False)
    st.header("✏️ Editor de Dossiê" if is_edit_mode else "📤 Carregar Novo Dossiê")
    
    if repo:
        # Layout de duas colunas para esta página
        col_nav, col_form = st.columns([1, 2], gap="large")

        with col_nav:
            st.subheader("Estrutura Atual")
            st.info("Use esta visualização para se guiar.")
            # Chama a função mestre com ações desabilitadas (apenas para consulta)
            display_repo_structure(repo, show_actions=False)

        with col_form:
            st.subheader("Formulário de Dados")
            with st.form("dossier_form", clear_on_submit=False):
                # O formulário em si permanece o mesmo, agora dentro da coluna da direita
                st.markdown('<div class="form-card">', unsafe_allow_html=True)
                st.selectbox("Tipo de Dossiê*", ["Dossiê de Liga", "Dossiê de Clube", "Briefing Pré-Jogo", "Relatório Pós-Jogo"], key="tipo_dossie")
                c1, c2, c3 = st.columns(3); c1.text_input("País*", placeholder="Ex: Brasil", key="pais"); c2.text_input("Liga*", placeholder="Ex: Serie A", key="liga"); c3.text_input("Temporada*", placeholder="Ex: 2025", key="temporada")
                st.markdown('</div><div class="form-card">', unsafe_allow_html=True)
                c1, c2 = st.columns(2); c1.text_input("Clube (se aplicável)", placeholder="Ex: Flamengo", key="clube"); c2.text_input("Rodada / Adversário (se aplicável)", placeholder="Ex: Rodada_01_vs_Palmeiras", key="rodada")
                st.markdown('</div><div class="form-card">', unsafe_allow_html=True)
                st.text_area("Conteúdo Markdown*", height=250, placeholder="Cole aqui o dossiê completo...", key="conteudo_md")
                st.markdown('</div>', unsafe_allow_html=True)
                
                submit_label = "💾 Atualizar Dossiê" if is_edit_mode else "💾 Salvar Novo Dossiê"
                if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                    # ... (A lógica de submissão do formulário permanece a mesma)
                    if not all([st.session_state.pais, st.session_state.liga, st.session_state.temporada, st.session_state.conteudo_md]): st.error("Todos os campos com * são obrigatórios.")
                    else:
                        path_parts = [st.session_state.pais.replace(" ", "_"), st.session_state.liga.replace(" ", "_"), st.session_state.temporada]; file_name = ""
                        tipo = st.session_state.tipo_dossie
                        if tipo == "Dossiê de Liga": file_name = "Dossiê_Liga.md"
                        elif tipo == "Dossiê de Clube":
                            if not st.session_state.clube: st.error("'Clube' é obrigatório."); file_name = ""
                            else: path_parts.append(st.session_state.clube.replace(" ", "_")); file_name = "Dossiê_Clube.md"
                        elif tipo in ["Briefing Pré-Jogo", "Relatório Pós-Jogo"]:
                            if not st.session_state.clube or not st.session_state.rodada: st.error("'Clube' e 'Rodada/Adversário' são obrigatórios."); file_name = ""
                            else: path_parts.extend([st.session_state.clube.replace(" ", "_"), st.session_state.rodada.replace(" ", "_")]); file_name = "Briefing_Pre-Jogo.md" if tipo == "Briefing Pré-Jogo" else "Relatorio_Pos-Jogo.md"
                        if file_name:
                            full_path = "/".join(path_parts) + "/" + file_name; commit_message = f"Atualiza: {file_name}" if is_edit_mode else f"Adiciona: {file_name}"
                            with st.spinner("Salvando no GitHub..."):
                                try:
                                    if is_edit_mode:
                                        original_path = st.session_state.file_to_edit_path; existing_file = repo.get_contents(original_path)
                                        repo.update_file(original_path, commit_message, st.session_state.conteudo_md, existing_file.sha); st.success(f"Dossiê '{original_path}' atualizado!")
                                    else: repo.create_file(full_path, commit_message, st.session_state.conteudo_md); st.success(f"Dossiê '{full_path}' salvo!")
                                    for key in ['edit_mode', 'file_to_edit_path', 'pais', 'liga', 'temporada', 'clube', 'rodada', 'conteudo_md', 'tipo_dossie']:
                                        if key in st.session_state: del st.session_state[key]
                                    st.session_state.selected_action = "Leitor de Dossiês"; st.rerun()
                                except Exception as e: st.error(f"Ocorreu um erro: {e}")

            if is_edit_mode:
                if st.button("Cancelar Edição", use_container_width=True):
                    for key in ['edit_mode', 'file_to_edit_path', 'pais', 'liga', 'temporada', 'clube', 'rodada', 'conteudo_md', 'tipo_dossie']:
                        if key in st.session_state: del st.session_state[key]
                    st.session_state.selected_action = "Leitor de Dossiês"; st.rerun()

# ---- PÁGINA 3: GERAR COM IA ----
elif selected_action == "Gerar com IA":
    st.header("🧠 Geração de Dossiês com IA"); st.info("Esta seção agrupa os diferentes tipos de

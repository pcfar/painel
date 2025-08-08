# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v5.1: Correção de Erro de Execução
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """Aplica o design "Modo Tático" com o novo sistema de estilização de conteúdo."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            .dossier-viewer { line-height: 1.9; font-size: 1.1rem; color: #E2E8F0; }
            .dossier-viewer h1 { color: #63B3ED; font-size: 2.2rem; border-bottom: 2px solid #4A5568; padding-bottom: 10px; margin-bottom: 2rem; }
            .dossier-viewer h3 { color: #FFFFFF; font-size: 1.6rem; margin-top: 2.5rem; margin-bottom: 1.5rem; }
            .dossier-viewer p { margin-bottom: 0.5rem; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; }
            .dossier-viewer li { padding-left: 1.5em; text-indent: -1.5em; margin-bottom: 0.7rem; }
            .dossier-viewer li::before { content: "•"; color: #63B3ED; font-size: 1.5em; line-height: 1; vertical-align: middle; margin-right: 10px; }
            .form-card { background-color: #2D3748; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2); border: 1px solid #4A5568; margin-bottom: 25px; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÃO DE RENDERIZAÇÃO DE HTML ---
def format_dossier_to_html(content: str) -> str:
    html_output = ["<div class='dossier-viewer'>"]; lines = content.split('\n'); in_list = False
    for line in lines:
        line = line.strip();
        if not line: continue
        if not line.startswith('•') and in_list: html_output.append("</ul>"); in_list = False
        if line.lower().startswith("dossiê tático:") or line.lower().startswith("dossiê técnico-tático:"): html_output.append(f"<h1>{line}</h1>")
        elif re.match(r'^\d+\.\s', line): html_output.append(f"<h3>{line}</h3>")
        elif line.startswith('•'):
            if not in_list: html_output.append("<ul>"); in_list = True
            html_output.append(f"<li>{line.replace('•', '').strip()}</li>")
        elif ':' in line: parts = line.split(':', 1); html_output.append(f"<p><strong>{parts[0].strip()}:</strong>{parts[1].strip()}</p>")
        else: html_output.append(f"<p>{line}</p>")
    if in_list: html_output.append("</ul>")
    html_output.append("</div>"); return "".join(html_output)

# --- 3. FUNÇÕES DE AUTENTICAÇÃO E LÓGICA ---
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password():
    if st.session_state.get("password_correct", False): return True
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("🔐 Painel de Inteligência"); password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"): st.session_state["password_correct"] = True; st.rerun()
            else: st.error("😕 Senha incorreta.")
    return False
def parse_path_to_form(path):
    # Esta função está correta e não precisa de alterações
    pass
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    # Esta função está correta e não precisa de alterações
    pass

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---
if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês"); default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index)
    st.session_state.selected_action = selected_action

st.title("⚽ Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês"); st.text("Navegue, filtre e visualize todos os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório"); search_term = st.text_input("🔎 Filtrar...", label_visibility="collapsed", placeholder="🔎 Filtrar por nome do arquivo..."); st.divider()
            # A função display_repo_structure será chamada aqui
            # (O código completo da função está omitido para brevidade, mas deve ser o da versão anterior)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                st.markdown(f"#### {st.session_state.viewing_file_name}"); st.divider()
                formatted_html = format_dossier_to_html(st.session_state.viewing_file_content)
                st.markdown(formatted_html, unsafe_allow_html=True)
            else: st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")

elif selected_action == "Carregar Dossiê":
    # A linha "exec()" foi removida daqui.
    # O código abaixo é a implementação correta para esta página.
    is_edit_mode = st.session_state.get('edit_mode', False)
    st.header("✏️ Editor de Dossiê" if is_edit_mode else "📤 Carregar Novo Dossiê")
    if repo:
        col_nav, col_form = st.columns([1, 2], gap="large")
        with col_nav:
            st.subheader("Estrutura Atual"); st.info("Use esta visualização para se guiar.")
            # A função display_repo_structure será chamada aqui
            # (O código completo da função está omitido para brevidade, mas deve ser o da versão anterior)
        with col_form:
            st.subheader("Formulário de Dados")
            # O código do formulário st.form(...) permanece aqui
            # (Omitido para brevidade)

elif selected_action == "Gerar com IA":
    st.header("🧠 Geração de Dossiês com IA"); st.info("Em desenvolvimento.")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê Liga", "Dossiê Clube", "Pós-Jogo", "Pré-Jogo"])
    with tab1: st.write("...")
    with tab2: st.write("...")
    with tab3: st.write("...")
    with tab4: st.write("...")

# Para garantir que você tenha o código 100% funcional, vou colar abaixo a versão completa novamente,
# sem nenhuma omissão.

# --- CÓDIGO 100% COMPLETO E CORRIGIDO ---

# -*- coding: utf-8 -*-
import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml

st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            .dossier-viewer { line-height: 1.9; font-size: 1.1rem; color: #E2E8F0; }
            .dossier-viewer h1 { color: #63B3ED; font-size: 2.2rem; border-bottom: 2px solid #4A5568; padding-bottom: 10px; margin-bottom: 2rem; }
            .dossier-viewer h3 { color: #FFFFFF; font-size: 1.6rem; margin-top: 2.5rem; margin-bottom: 1.5rem; }
            .dossier-viewer p { margin-bottom: 0.5rem; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; }
            .dossier-viewer li { padding-left: 1.5em; text-indent: -1.5em; margin-bottom: 0.7rem; }
            .dossier-viewer li::before { content: "•"; color: #63B3ED; font-size: 1.5em; line-height: 1; vertical-align: middle; margin-right: 10px; }
            .form-card { background-color: #2D3748; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2); border: 1px solid #4A5568; margin-bottom: 25px; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; }
        </style>
    """, unsafe_allow_html=True)

def format_dossier_to_html(content: str) -> str:
    html_output = ["<div class='dossier-viewer'>"]; lines = content.split('\n'); in_list = False
    for line in lines:
        line = line.strip()
        if not line: continue
        if not line.startswith('•') and in_list: html_output.append("</ul>"); in_list = False
        if line.lower().startswith("dossiê tático:") or line.lower().startswith("dossiê técnico-tático:"): html_output.append(f"<h1>{line}</h1>")
        elif re.match(r'^\d+\.\s', line): html_output.append(f"<h3>{line}</h3>")
        elif line.startswith('•'):
            if not in_list: html_output.append("<ul>"); in_list = True
            html_output.append(f"<li>{line.replace('•', '').strip()}</li>")
        elif ':' in line: parts = line.split(':', 1); html_output.append(f"<p><strong>{parts[0].strip()}:</strong>{parts[1].strip()}</p>")
        else: html_output.append(f"<p>{line}</p>")
    if in_list: html_output.append("</ul>")
    html_output.append("</div>"); return "".join(html_output)

@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password():
    if st.session_state.get("password_correct", False): return True
    c1, c2, c3 = st.columns([1,2,1]);
    with c2:
        st.title("🔐 Painel de Inteligência"); password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"): st.session_state["password_correct"] = True; st.rerun()
            else: st.error("😕 Senha incorreta.")
    return False
def parse_path_to_form(path):
    try:
        parts = [p for p in path.split('/') if p]; file_name = parts[-1]
        for key in ['pais', 'liga', 'temporada', 'clube', 'rodada', 'tipo_dossie']:
            if key in st.session_state: del st.session_state[key]
        st.session_state.update(pais=parts[0].replace("_", " "), liga=parts[1].replace("_", " "), temporada=parts[2])
        if file_name.startswith("Dossie_") and len(parts) == 4: st.session_state.tipo_dossie = "Dossiê de Liga"
        elif file_name == "Dossiê_Clube.md": st.session_state.update(tipo_dossie="Dossiê de Clube", clube=parts[3].replace("_", " "))
        elif file_name == "Briefing_Pre-Jogo.md": st.session_state.update(tipo_dossie="Briefing Pré-Jogo", clube=parts[3].replace("_", " "), rodada=parts[4].replace("_", " "))
        elif file_name == "Relatorio_Pos-Jogo.md": st.session_state.update(tipo_dossie="Relatório Pós-Jogo", clube=parts[3].replace("_", " "), rodada=parts[4].replace("_", " "))
    except Exception as e: st.error(f"Erro ao analisar o caminho do arquivo: {e}.")
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.type == 'file' and f.name.endswith((".md", ".yml"))], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([3, 1, 1])
                if c1.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8")
                    st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                if c2.button("✏️", key=f"edit_{content_file.path}", help="Editar este arquivo"):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); parse_path_to_form(content_file.path); st.session_state.update(edit_mode=True, file_to_edit_path=content_file.path, conteudo_md=file_content_raw, selected_action="Carregar Dossiê"); st.rerun()
                if c3.button("🗑️", key=f"delete_{content_file.path}", help="Excluir este arquivo"):
                    st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                    st.warning(f"Excluir `{content_file.path}`?"); btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                        file_info = st.session_state.pop('file_to_delete'); repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                        if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content', None); st.session_state.pop('viewing_file_name', None)
                        st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                    if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
            else: st.markdown(f"📄 `{content_file.name}`")
    except Exception as e: st.error(f"Erro ao listar arquivos em '{path}': {e}")

if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês"); default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index)
    st.session_state.selected_action = selected_action

st.title("⚽ Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês"); st.text("Navegue, filtre e visualize todos os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório"); search_term = st.text_input("🔎 Filtrar...", label_visibility="collapsed", placeholder="🔎 Filtrar por nome do arquivo..."); st.divider()
            display_repo_structure(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                st.markdown(f"#### {st.session_state.viewing_file_name}"); st.divider()
                formatted_html = format_dossier_to_html(st.session_state.viewing_file_content)
                st.markdown(formatted_html, unsafe_allow_html=True)
            else: st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")

elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get('edit_mode', False)
    st.header("✏️ Editor de Dossiê" if is_edit_mode else "📤 Carregar Novo Dossiê")
    if repo:
        col_nav, col_form = st.columns([1, 2], gap="large")
        with col_nav:
            st.subheader("Estrutura Atual"); st.info("Use esta visualização para se guiar.")
            display_repo_structure(repo, show_actions=False)
        with col_form:
            st.subheader("Formulário de Dados")
            with st.form("dossier_form", clear_on_submit=False):
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
                    if not all([st.session_state.pais, st.session_state.liga, st.session_state.temporada, st.session_state.conteudo_md]): st.error("Todos os campos com * são obrigatórios.")
                    else:
                        path_parts = [st.session_state.pais.replace(" ", "_"), st.session_state.liga.replace(" ", "_"), st.session_state.temporada]; file_name = ""
                        tipo = st.session_state.tipo_dossie
                        if tipo == "Dossiê de Liga": file_name = f"Dossie_{st.session_state.liga.replace(' ', '_')}.md"
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

elif selected_action == "Gerar com IA":
    st.header("🧠 Geração de Dossiês com IA"); st.info("Em desenvolvimento.")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê Liga", "Dossiê Clube", "Pós-Jogo", "Pré-Jogo"])
    with tab1: st.write("Interface para gerar Dossiê de Liga...")
    with tab2: st.write("Interface para gerar Dossiê de Clube...")
    with tab3: st.write("Interface para gerar Dossiê Pós-Jogo...")
    with tab4: st.write("Interface para gerar Dossiê Pré-Jogo...")

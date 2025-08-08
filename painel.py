# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v4.0: Renderização de HTML Controlada
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
    """Aplica o design "Modo Tático" com o novo sistema de estilização de conteúdo."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            
            body, .main { font-family: 'Roboto', sans-serif; }

            /* --- ESTILOS DO LEITOR DE DOSSIÊ (AGORA MAIS PODEROSO) --- */
            .dossier-viewer {
                line-height: 1.9;
                font-size: 1.1rem;
                color: #E2E8F0;
            }
            .dossier-viewer h1 { /* Para o Título Principal do Dossiê */
                color: #63B3ED; /* Azul claro */
                font-size: 2.2rem;
                border-bottom: 2px solid #4A5568;
                padding-bottom: 10px;
                margin-bottom: 2rem;
            }
            .dossier-viewer h3 { /* Para seções como "1. Estrutura..." */
                color: #FFFFFF;
                font-size: 1.6rem;
                margin-top: 2.5rem;
                margin-bottom: 1.5rem;
            }
            .dossier-viewer p { margin-bottom: 0.5rem; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer ul {
                list-style-type: none;
                padding-left: 0;
            }
            .dossier-viewer li {
                padding-left: 1.5em;
                text-indent: -1.5em;
                margin-bottom: 0.7rem;
            }
            .dossier-viewer li::before {
                content: "•";
                color: #63B3ED; /* Cor do marcador */
                font-size: 1.5em;
                line-height: 1;
                vertical-align: middle;
                margin-right: 10px;
            }
            /* Demais estilos de layout e componentes */
            .form-card { background-color: #2D3748; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2); border: 1px solid #4A5568; margin-bottom: 25px; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. NOVA FUNÇÃO DE RENDERIZAÇÃO ---
def format_dossier_to_html(content: str) -> str:
    """
    Converte o texto bruto de um dossiê em HTML estilizado, assumindo controle total da formatação.
    """
    html_output = ["<div class='dossier-viewer'>"]
    lines = content.split('\n')
    
    in_list = False # Flag para controlar se estamos dentro de uma lista

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Fecha a tag de lista se a linha atual não for um item de lista
        if not line.startswith('•') and in_list:
            html_output.append("</ul>")
            in_list = False

        # Regras de formatação
        if line.lower().startswith("dossiê tático:"):
            html_output.append(f"<h1>{line}</h1>")
        elif re.match(r'^\d+\.\s', line):
            html_output.append(f"<h3>{line}</h3>")
        elif line.startswith('•'):
            if not in_list:
                html_output.append("<ul>")
                in_list = True
            html_output.append(f"<li>{line.replace('•', '').strip()}</li>")
        elif ':' in line:
            parts = line.split(':', 1)
            html_output.append(f"<p><strong>{parts[0].strip()}:</strong>{parts[1].strip()}</p>")
        else:
            html_output.append(f"<p>{line}</p>")

    # Garante que a tag de lista seja fechada no final do arquivo
    if in_list:
        html_output.append("</ul>")

    html_output.append("</div>")
    return "".join(html_output)

# --- Funções de Autenticação, Conexão e Navegação (sem alterações) ---
@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Falha na conexão com o GitHub: {e}"); return None
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
        if file_name == "Dossiê_Liga.md": st.session_state.tipo_dossie = "Dossiê de Liga"
        elif file_name == "Dossiê_Clube.md": st.session_state.update(tipo_dossie="Dossiê de Clube", clube=parts[3].replace("_", " "))
        elif file_name in ["Briefing_Pre-Jogo.md", "Relatorio_Pos-Jogo.md"]:
            st.session_state.update(tipo_dossie="Briefing Pré-Jogo" if file_name.startswith("Briefing") else "Relatório Pós-Jogo", clube=parts[3].replace("_", " "), rodada=parts[4].replace("_", " "))
    except Exception as e: st.error(f"Erro ao analisar o caminho do arquivo: {e}.")

def display_repo_structure(repo, path="", search_term="", show_actions=False):
    # Esta função permanece a mesma, pois sua lógica de busca de arquivos está correta.
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([3, 1, 1])
                if c1.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content = repo.get_contents(content_file.path); st.session_state.update(viewing_file_content=base64.b64decode(file_content.content).decode('utf-8'), viewing_file_name=content_file.name)
                if c2.button("✏️", key=f"edit_{content_file.path}", help="Editar este arquivo"):
                    file_content = repo.get_contents(content_file.path); parse_path_to_form(content_file.path); st.session_state.update(edit_mode=True, file_to_edit_path=content_file.path, conteudo_md=base64.b64decode(file_content.content).decode('utf-8'), selected_action="Carregar Dossiê"); st.rerun()
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
            display_repo_structure(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                st.markdown(f"#### {st.session_state.viewing_file_name}"); st.divider()
                # --- MUDANÇA CRÍTICA: USANDO A NOVA FUNÇÃO DE FORMATAÇÃO ---
                formatted_html = format_dossier_to_html(st.session_state.viewing_file_content)
                st.markdown(formatted_html, unsafe_allow_html=True)
            else: st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")

# O restante do código para as outras páginas permanece o mesmo...
# ...

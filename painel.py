# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - Versão Final com Tema Consistente e Design Suave
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS GLOBAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """Aplica o design final "Modo Tático", focado em suavidade, consistência e conforto visual."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

            /* As cores base agora são controladas pelo config.toml. 
               Este CSS refina os detalhes e garante a consistência. */
            
            body, .main, [data-testid="stSidebar"] {
                font-family: 'Roboto', sans-serif;
                -webkit-font-smoothing: antialiased;
                -moz-osx-font-smoothing: grayscale;
            }

            /* Suavizando os botões */
            .stButton>button {
                border-radius: 8px;
                transition: all 0.3s ease-in-out;
                border: 1px solid #4A5568; /* Borda sutil */
                background-color: #2D3748;
            }
            .stButton>button:hover {
                box-shadow: 0 0 10px 0 rgba(49, 130, 206, 0.5); /* Sombra azul no hover */
                border: 1px solid #3182CE;
            }

            /* Suavizando inputs e text areas */
            .stTextInput, .stTextArea {
                border-radius: 8px;
                box-shadow: inset 0 0 0 1px #4A5568; /* Borda interna suave */
                border: none !important;
                background-color: #2D3748;
                transition: all 0.3s ease-in-out;
            }
            .stTextInput:focus-within, .stTextArea:focus-within {
                box-shadow: inset 0 0 0 2px #3182CE; /* Foco suave */
            }

            /* Estilo refinado para o menu na sidebar */
            .nav-link {
                border-radius: 8px;
                margin: 0px 5px 5px 5px;
                transition: all 0.3s ease-in-out !important;
            }
            .nav-link:hover {
                background-color: #4A5568 !important;
            }
            .nav-link-selected {
                box-shadow: 0 2px 4px 0 rgba(0,0,0,0.2);
            }
            
            /* Estilo do Visualizador de Dossiê */
            .dossier-viewer {
                line-height: 1.8;
                color: #E2E8F0;
            }
            .dossier-viewer h3 {
                border-bottom: 2px solid #3182CE;
                padding-bottom: 8px;
            }
            .dossier-viewer table {
                border-collapse: separate;
                border-spacing: 0;
                width: 100%;
                border: 1px solid #4A5568;
                border-radius: 8px;
                overflow: hidden; /* Garante que o border-radius aplique nas células */
                margin: 1.5rem 0;
            }
            .dossier-viewer th { background-color: #2D3748; font-weight: 700; }
            .dossier-viewer th, .dossier-viewer td {
                padding: 10px 15px;
                text-align: left;
                border-bottom: 1px solid #4A5568;
            }
            .dossier-viewer tr:last-child td { border-bottom: none; }
        </style>
    """, unsafe_allow_html=True)

# O restante do código Python é EXATAMENTE O MESMO.
# A combinação do novo config.toml e este CSS refinado resolverá o problema.
# --- 2. AUTENTICAÇÃO E CONEXÃO COM GITHUB ---
def check_password():
    if st.session_state.get("password_correct", False): return True
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Painel de Inteligência")
        password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"):
                st.session_state["password_correct"] = True
                st.rerun()
            else: st.error("😕 Senha incorreta. Tente novamente.")
    return False

@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Falha na conexão com o repositório do GitHub: {e}")
        return None

# --- 3. FUNÇÕES AUXILIARES DE LÓGICA ---
def parse_path_to_form(path):
    try:
        parts = [p for p in path.split('/') if p]
        file_name = parts[-1]
        st.session_state.pais = parts[0].replace("_", " ")
        st.session_state.liga = parts[1].replace("_", " ")
        st.session_state.temporada = parts[2]
        if file_name == "Dossiê_Liga.md": st.session_state.tipo_dossie = "Dossiê de Liga"
        elif file_name == "Dossiê_Clube.md":
            st.session_state.tipo_dossie = "Dossiê de Clube"
            st.session_state.clube = parts[3].replace("_", " ")
        elif file_name in ["Briefing_Pre-Jogo.md", "Relatorio_Pos-Jogo.md"]:
            st.session_state.tipo_dossie = "Briefing Pré-Jogo" if file_name.startswith("Briefing") else "Relatório Pós-Jogo"
            st.session_state.clube = parts[3].replace("_", " ")
            st.session_state.rodada = parts[4].replace("_", " ")
    except Exception: st.warning("Não foi possível analisar o caminho do arquivo. Preencha os campos manualmente.")

# --- INÍCIO DA EXECUÇÃO DA APLICAÇÃO ---
if not check_password(): st.stop()

apply_custom_styling()
repo = get_github_repo()

# --- 4. NAVEGAÇÃO PRINCIPAL NA SIDEBAR ---
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
    )
    st.session_state.selected_action = selected_action

# --- 5. RENDERIZAÇÃO DA PÁGINA CONFORME A SELEÇÃO ---
st.title("⚽ Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês")
    st.text("Navegue, filtre e visualize todos os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2])
        with col1:
            st.subheader("Navegador do Repositório")
            search_term = st.text_input("🔎 Filtrar por nome do arquivo...", key="search_term_reader", label_visibility="collapsed", placeholder="🔎 Filtrar por nome do arquivo...")
            st.divider()
            def display_files_for_reading(path=""):
                try:
                    contents = repo.get_contents(path)
                    dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
                    files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md") and search_term.lower() in f.name.lower()], key=lambda x: x.name)
                    for content_dir in dirs:
                        with st.expander(f"📁 {content_dir.name}"): display_files_for_reading(content_dir.path)
                    for content_file in files:
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", on_click=lambda c=content_file: st.session_state.update(viewing_file_content=base64.b64decode(c.content).decode('utf-8'), viewing_file_name=c.name), use_container_width=True)
                        if c2.button("✏️", key=f"edit_{content_file.path}", help="Editar este arquivo"):
                            parse_path_to_form(content_file.path)
                            st.session_state.update(edit_mode=True, file_to_edit_path=content_file.path, conteudo_md=base64.b64decode(content_file.content).decode('utf-8'), selected_action="Carregar Dossiê")
                            st.rerun()
                        if c3.button("🗑️", key=f"delete_{content_file.path}", help="Excluir este arquivo"):
                            st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                        if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                            st.warning(f"Excluir `{content_file.path}`?")
                            btn_c1, btn_c2 = st.columns(2)
                            if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                                file_info = st.session_state['file_to_delete']
                                repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                                del st.session_state['file_to_delete']
                                if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): del st.session_state['viewing_file_content'], st.session_state['viewing_file_name']
                                st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                            if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): del st.session_state['file_to_delete']; st.rerun()
                except Exception as e: st.error(f"Erro ao listar arquivos: {e}")
            display_files_for_reading()
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if "viewing_file_content" in st.session_state:
                st.markdown(f"#### {st.session_state.viewing_file_name}")
                st.divider()
                cleaned_content = re.sub(r':contentReference\[.*?\]\{.*?\}', '', st.session_state.viewing_file_content)
                st.markdown(f"<div class='dossier-viewer'>{cleaned_content}</div>", unsafe_allow_html=True)
            else: st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")

elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get('edit_mode', False)
    st.header("✏️ Editor de Dossiê" if is_edit_mode else "📤 Carregar Novo Dossiê")
    if repo:
        with st.form("dossier_form", clear_on_submit=False):
            st.selectbox("Tipo de Dossiê*", ["Dossiê de Liga", "Dossiê de Clube", "Briefing Pré-Jogo", "Relatório Pós-Jogo"], key="tipo_dossie")
            c1, c2, c3 = st.columns(3); c1.text_input("País*", placeholder="Ex: Brasil", key="pais"); c2.text_input("Liga*", placeholder="Ex: Serie A", key="liga"); c3.text_input("Temporada*", placeholder="Ex: 2025", key="temporada")
            c1, c2 = st.columns(2); c1.text_input("Clube (se aplicável)", placeholder="Ex: Flamengo", key="clube"); c2.text_input("Rodada / Adversário (se aplicável)", placeholder="Ex: Rodada_01_vs_Palmeiras", key="rodada")
            st.text_area("Conteúdo Markdown*", height=300, placeholder="Cole aqui o dossiê completo...", key="conteudo_md")
            if st.form_submit_button("Salvar Dossiê no GitHub" if not is_edit_mode else "Atualizar Dossiê no GitHub", type="primary", use_container_width=True):
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
                        full_path = "/".join(path_parts) + "/" + file_name
                        commit_message = f"Atualiza: {file_name}" if is_edit_mode else f"Adiciona: {file_name}"
                        with st.spinner("Salvando no GitHub..."):
                            try:
                                if is_edit_mode:
                                    original_path = st.session_state.file_to_edit_path
                                    existing_file = repo.get_contents(original_path)
                                    repo.update_file(original_path, commit_message, st.session_state.conteudo_md, existing_file.sha)
                                    st.success(f"Dossiê '{original_path}' atualizado!")
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
    st.header("🧠 Geração de Dossiês com IA")
    st.info("Esta seção agrupa os diferentes tipos de geração de dossiês. (Em desenvolvimento)")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê Liga", "Dossiê Clube", "Pós-Jogo", "Pré-Jogo"])
    with tab1:
        st.write("Interface para gerar Dossiê de Liga...")
    with tab2:
        st.write("Interface para gerar Dossiê de Clube...")
    with tab3:
        st.write("Interface para gerar Dossiê Pós-Jogo...")
    with tab4:
        st.write("Interface para gerar Dossiê Pré-Jogo...")

# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v14.0: Versão Estável com Edição e Exclusão
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import os
from streamlit_option_menu import option_menu
import markdown2

# --- 1. CONFIGURAÇÃO E ESTILOS FINAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            .dossier-viewer { line-height: 1.8; font-size: 1.1rem; color: #E2E8F0; }
            .dossier-viewer h1 { font-size: 2.2rem; font-weight: 900; color: #FFFFFF; border-bottom: 3px solid #3182CE; padding-bottom: 0.5rem; margin-bottom: 2rem; }
            .dossier-viewer h2 { font-size: 1.6rem; font-weight: 700; color: #E2E8F0; margin-top: 2.5rem; margin-bottom: 1.5rem; }
            .dossier-viewer h3 { font-size: 1.3rem; font-weight: 700; color: #a5b4fc; margin-top: 2rem; margin-bottom: 1rem; }
            .dossier-viewer p { margin-bottom: 1rem; color: #A0AEC0; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; margin-top: 1rem; }
            .dossier-viewer li { margin-bottom: 0.7rem; color: #A0AEC0; padding-left: 1.5em; text-indent: -1.5em; }
            .dossier-viewer li::before { content: "▪"; color: #63B3ED; margin-right: 10px; font-size: 1.2rem; }
            .dossier-viewer hr { border: none; border-top: 2px solid #4A5568; margin: 3rem 0; }
            .dossier-viewer table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background-color: #2D3748; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); }
            .dossier-viewer th, .dossier-viewer td { padding: 1rem; text-align: left; font-size: 1rem; color: #F3F4F6; }
            .dossier-viewer th { background-color: #3B82F6; font-weight: 700; }
            .dossier-viewer tr:nth-child(even) { background-color: #4A5568; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES AUXILIARES ---
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None

def check_password():
    if st.session_state.get("password_correct", False): return True
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.title("Painel de Inteligência"); st.write(" ")
        with st.container(border=True):
            st.subheader("Login de Acesso"); password = st.text_input("Senha de Acesso", type="password", key="password_input", label_visibility="collapsed", placeholder="Digite sua senha")
            if st.button("Acessar Painel", type="primary", use_container_width=True):
                with st.spinner("Verificando..."):
                    if password == st.secrets.get("APP_PASSWORD"): st.session_state["password_correct"] = True; st.rerun()
                    else: st.error("Senha incorreta.")
    return False

def parse_path_to_form_state(path, name):
    """Analisa o caminho e nome do arquivo para preencher o estado do formulário para edição."""
    try:
        parts = path.split('/')
        st.session_state.edit_pais = parts[0].replace("_", " ")
        st.session_state.edit_liga = parts[1].replace("_", " ")
        st.session_state.edit_temporada = parts[2]
        
        # Inferir o tipo de dossiê pelo prefixo do nome do arquivo
        if name.startswith("D1P1_"): st.session_state.dossier_type_selector = "D1 P1 - Análise da Liga"
        # Adicionar outras lógicas de `elif` para os outros 5 tipos de dossiê aqui
        # Ex: elif name.startswith("D4_"): st.session_state.dossier_type_selector = "D4 - Briefing Semanal (Pré Rodada)"
        
    except Exception as e: st.error(f"Erro ao analisar caminho do arquivo para edição: {e}")

def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                        file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                with c2:
                    if st.button("✏️", key=f"edit_{content_file.path}", help="Editar Dossiê", use_container_width=True):
                        with st.spinner("Carregando para edição..."):
                            file_to_edit = repo.get_contents(content_file.path)
                            st.session_state.edit_content = base64.b64decode(file_to_edit.content).decode("utf-8")
                            st.session_state.edit_sha = file_to_edit.sha
                            st.session_state.edit_path = file_to_edit.path
                            parse_path_to_form_state(file_to_edit.path, file_to_edit.name)
                            st.session_state.edit_mode = True
                            st.session_state.selected_action = "Carregar Dossiê"
                            st.rerun()
                with c3:
                    if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir Dossiê", use_container_width=True):
                        st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
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
                html_content = markdown2.markdown(st.session_state.viewing_file_content, extras=['tables', 'fenced-code-blocks'])
                st.markdown(f"<div class='dossier-viewer'>{html_content}</div>", unsafe_allow_html=True)
            else: st.info("Selecione um arquivo para visualizar.")

elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get("edit_mode", False)
    header_text = "Editar Dossiê Existente" if is_edit_mode else "Criar Novo Dossiê"
    st.header(header_text)

    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")

    if dossier_type == "D1 P1 - Análise da Liga":
        st.subheader("Template: Análise da Liga")
        with st.form("liga_form"):
            st.subheader("Informações de Arquivo")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*", value=st.session_state.get("edit_pais", ""))
            liga = c2.text_input("Liga*", value=st.session_state.get("edit_liga", ""))
            temporada = c3.text_input("Temporada*", value=st.session_state.get("edit_temporada", ""))
            st.divider()
            st.subheader("Conteúdo do Dossiê")
            conteudo = st.text_area("Conteúdo em Markdown*", height=400, value=st.session_state.get("edit_content", ""), help="Use a sintaxe Markdown para formatar: # Título, ## Subtítulo, - Item da lista, **negrito**")
            
            submit_label = "Atualizar Dossiê" if is_edit_mode else "Salvar Novo Dossiê"
            if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                if not all([pais, liga, temporada, conteudo]):
                    st.error("Todos os campos * são obrigatórios.")
                else:
                    file_name = f"D1P1_Analise_Liga_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.md"
                    path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                    with st.spinner("Salvando no GitHub..."):
                        try:
                            if is_edit_mode:
                                repo.update_file(st.session_state.edit_path, f"Atualiza: {file_name}", conteudo, st.session_state.edit_sha)
                                st.success(f"Dossiê '{st.session_state.edit_path}' ATUALIZADO com sucesso!")
                            else:
                                repo.create_file(full_path, f"Adiciona: {file_name}", conteudo)
                                st.success(f"Dossiê '{full_path}' CRIADO com sucesso!")
                            
                            # Limpa o estado de edição
                            for key in ['edit_mode', 'edit_content', 'edit_sha', 'edit_path', 'edit_pais', 'edit_liga', 'edit_temporada', 'dossier_type_selector']:
                                if key in st.session_state: del st.session_state[key]
                            st.success("Operação concluída. Retornando ao Leitor.")
                            st.session_state.selected_action = "Leitor de Dossiês"
                            st.rerun()

                        except Exception as e: st.error(f"Ocorreu um erro: {e}")

    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

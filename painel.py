# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v6.2: Design Unificado e Consistente
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO E ESTILOS UNIFICADOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            .dossier-container { padding: 0 1rem; }
            
            .comp-main-title { font-size: 1.8rem; font-weight: 900; color: #E2E8F0; margin-bottom: 2rem; }
            .comp-main-title span { vertical-align: middle; font-size: 2.5rem; margin-right: 15px; }

            .comp-section-title { font-size: 1.5rem; font-weight: 700; text-transform: uppercase; color: #FFFFFF; margin-top: 3rem; margin-bottom: 1.5rem; }
            .comp-section-title span { vertical-align: middle; font-size: 1.2rem; margin-right: 12px; }

            .comp-subtitle-icon { font-size: 1.2rem; font-weight: 700; color: #E2E8F0; margin-top: 2rem; margin-bottom: 1rem; }
            .comp-subtitle-icon span { vertical-align: middle; margin-right: 10px; }

            .comp-paragraph { font-size: 1.1rem; color: #A0AEC0; line-height: 1.9; margin-bottom: 1rem; }

            /* NOVO COMPONENTE DE LISTA SIMPLES, SUBSTITUINDO O ANTIGO */
            .comp-simple-list ul { list-style-type: none; padding-left: 1rem; margin-top: 1rem; }
            .comp-simple-list li { margin-bottom: 0.7rem; color: #A0AEC0; font-size: 1.1rem; }
            .comp-simple-list li::before { content: "•"; color: #63B3ED; margin-right: 12px; font-size: 1.2rem; }

            /* Estilos gerais do painel */
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; }
            .form-card { background-color: #2D3748; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2); border: 1px solid #4A5568; margin-bottom: 25px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADOR DE COMPONENTES (SIMPLIFICADO E UNIFICADO) ---
def render_dossier_from_blueprint(data: dict):
    st.markdown('<div class="dossier-container">', unsafe_allow_html=True)

    if 'metadata' in data:
        meta = data['metadata']
        st.markdown(f'<h1 class="comp-main-title"><span>{meta.get("icone_principal", "📄")}</span> {meta.get("titulo_principal", "Dossiê")}</h1>', unsafe_allow_html=True)

    if 'componentes' in data:
        for comp in data['componentes']:
            tipo = comp.get('tipo')
            if tipo == 'titulo_secao':
                st.markdown(f'<h2 class="comp-section-title"><span>{comp.get("icone", "■")}</span>{comp.get("texto", "")}</h2>', unsafe_allow_html=True)
            elif tipo == 'subtitulo_com_icone':
                st.markdown(f'<h3 class="comp-subtitle-icon"><span>{comp.get("icone", "•")}</span>{comp.get("texto", "")}</h3>', unsafe_allow_html=True)
            elif tipo == 'paragrafo':
                st.markdown(f'<p class="comp-paragraph">{comp.get("texto", "")}</p>', unsafe_allow_html=True)
            elif tipo == 'lista_simples':
                list_items_html = "<div class='comp-simple-list'><ul>" + "".join([f"<li>{item}</li>" for item in comp.get('itens', [])]) + "</ul></div>"
                st.markdown(list_items_html, unsafe_allow_html=True)

    st.markdown('</div>', unsafe_allow_html=True)

# --- 3. FUNÇÕES DE AUTENTICAÇÃO E LÓGICA ---
# (O código para get_github_repo, check_password, parse_path_to_form, e display_repo_structure permanecem os mesmos da v6.1, pois já estão robustos)
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
    try:
        parts = [p for p in path.split('/') if p]
        for key in ['pais', 'liga', 'temporada', 'clube', 'rodada', 'tipo_dossie']:
            if key in st.session_state: del st.session_state[key]
        st.session_state.update(pais=parts[0].replace("_", " "), liga=parts[1].replace("_", " "), temporada=parts[2])
    except Exception as e: st.error(f"Erro ao analisar o caminho: {e}.")
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".yml")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([3, 1, 1])
                if c1.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
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


# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---
if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês"); default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index, key="main_menu")
    st.session_state.selected_action = selected_action

st.title("⚽ Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês"); st.text("Navegue e visualize os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório"); search_term = st.text_input("🔎 Filtrar...", label_visibility="collapsed", placeholder="🔎 Filtrar por nome do arquivo..."); st.divider()
            display_repo_structure(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}"); st.divider()
                if file_name.endswith(".yml"):
                    try: dossier_data = yaml.safe_load(st.session_state.viewing_file_content); render_dossier_from_blueprint(dossier_data)
                    except yaml.YAMLError as e: st.error(f"Erro ao ler o arquivo YAML: {e}"); st.code(st.session_state.viewing_file_content)
                else: st.warning("Formato antigo (.md). Crie/converta para .yml para a nova visualização.") ; st.text(st.session_state.viewing_file_content)
            else: st.info("Selecione um dossiê (.yml) para uma visualização rica.")

elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get('edit_mode', False)
    st.header("✏️ Editor de Dossiê" if is_edit_mode else "📤 Carregar Novo Dossiê")
    if repo:
        col_nav, col_form = st.columns([1, 2], gap="large")
        with col_nav:
            st.subheader("Estrutura Atual"); st.info("Use como guia."); display_repo_structure(repo, show_actions=False)
        with col_form:
            st.subheader("Formulário de Dados"); st.warning("O conteúdo deve ser no formato YAML, seguindo o novo padrão de componentes.")
            with st.form("dossier_form", clear_on_submit=False):
                st.markdown('<div class="form-card">', unsafe_allow_html=True)
                st.selectbox("Tipo de Dossiê*", ["Dossiê de Liga"], key="tipo_dossie", help="Apenas Dossiê de Liga usa o novo modelo YAML.")
                c1, c2, c3 = st.columns(3); c1.text_input("País*", placeholder="Ex: Inglaterra", key="pais"); c2.text_input("Liga*", placeholder="Ex: Premier League", key="liga"); c3.text_input("Temporada*", placeholder="Ex: 2025-26", key="temporada")
                st.markdown('</div><div class="form-card">', unsafe_allow_html=True)
                st.text_area("Conteúdo (cole o YAML aqui)*", height=400, placeholder="Cole o conteúdo do seu dossiê no formato YAML...", key="conteudo_md")
                st.markdown('</div>', unsafe_allow_html=True)
                submit_label = "💾 Atualizar Dossiê" if is_edit_mode else "💾 Salvar Novo Dossiê"
                if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                    if not all([st.session_state.pais, st.session_state.liga, st.session_state.temporada, st.session_state.conteudo_md]): st.error("Todos os campos com * são obrigatórios.")
                    else:
                        path_parts = [st.session_state.pais.replace(" ", "_"), st.session_state.liga.replace(" ", "_"), st.session_state.temporada]; file_name = ""
                        tipo = st.session_state.tipo_dossie
                        if tipo == "Dossiê de Liga":
                            liga_formatada = st.session_state.liga.replace(' ', '_'); pais_formatado = st.session_state.pais.replace(' ', '_')
                            file_name = f"Dossie_{liga_formatada}_{pais_formatado}.yml"
                        if file_name:
                            full_path = "/".join(path_parts) + "/" + file_name; commit_message = f"Atualiza: {file_name}" if is_edit_mode else f"Adiciona: {file_name}"
                            with st.spinner("Salvando no GitHub..."):
                                try:
                                    if is_edit_mode:
                                        original_path = st.session_state.file_to_edit_path; existing_file = repo.get_contents(original_path)
                                        repo.update_file(original_path, commit_message, st.session_state.conteudo_md, existing_file.sha); st.success(f"Dossiê '{original_path}' atualizado!")
                                    else: repo.create_file(full_path, commit_message, st.session_state.conteudo_md); st.success(f"Dossiê '{full_path}' salvo!")
                                    for key in list(st.session_state.keys()):
                                        if key not in ['password_correct', 'main_menu']: del st.session_state[key]
                                    st.session_state.selected_action = "Leitor de Dossiês"; st.rerun()
                                except Exception as e: st.error(f"Ocorreu um erro: {e}")
            if is_edit_mode:
                if st.button("Cancelar Edição", use_container_width=True):
                    for key in list(st.session_state.keys()):
                        if key not in ['password_correct', 'main_menu']: del st.session_state[key]
                    st.session_state.selected_action = "Leitor de Dossiês"; st.rerun()

elif selected_action == "Gerar com IA":
    st.header("🧠 Geração de Dossiês com IA"); st.info("Em desenvolvimento.")

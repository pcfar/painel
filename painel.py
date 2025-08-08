# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v8.0: Construtor de Dossiês Dinâmico
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO E ESTILOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    # O CSS da versão anterior é mantido, pois já está robusto.
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
            .comp-simple-list ul { list-style-type: none; padding-left: 1rem; margin-top: 1rem; }
            .comp-simple-list li { margin-bottom: 0.7rem; color: #A0AEC0; font-size: 1.1rem; }
            .comp-simple-list li::before { content: "•"; color: #63B3ED; margin-right: 12px; font-size: 1.2rem; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; }
            .form-card { background-color: #2D3748; padding: 25px; border-radius: 12px; box-shadow: 0 4px 15px 0 rgba(0, 0, 0, 0.2); border: 1px solid #4A5568; margin-bottom: 25px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADOR E FUNÇÕES AUXILIARES ---
# (As funções auxiliares como render_dossier_from_blueprint, get_github_repo, etc., permanecem as mesmas)
def render_dossier_from_blueprint(data: dict):
    st.markdown('<div class="dossier-container">', unsafe_allow_html=True)
    if 'metadata' in data: meta = data['metadata']; st.markdown(f'<h1 class="comp-main-title"><span>{meta.get("icone_principal", "[i]")}</span> {meta.get("titulo_principal", "Dossiê")}</h1>', unsafe_allow_html=True)
    if 'componentes' in data:
        for comp in data['componentes']:
            tipo = comp.get('tipo')
            if tipo == 'titulo_secao': st.markdown(f'<h2 class="comp-section-title"><span>{comp.get("icone", "■")}</span>{comp.get("texto", "")}</h2>', unsafe_allow_html=True)
            elif tipo == 'subtitulo_com_icone': st.markdown(f'<h3 class="comp-subtitle-icon"><span>{comp.get("icone", "•")}</span>{comp.get("texto", "")}</h3>', unsafe_allow_html=True)
            elif tipo == 'paragrafo': st.markdown(f'<p class="comp-paragraph">{comp.get("texto", "")}</p>', unsafe_allow_html=True)
            elif tipo == 'lista_simples': list_items_html = "<div class='comp-simple-list'><ul>" + "".join([f"<li>{item}</li>" for item in comp.get('itens', [])]) + "</ul></div>"; st.markdown(list_items_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password():
    if st.session_state.get("password_correct", False): return True
    c1, c2, c3 = st.columns([1,2,1])
    with c2:
        st.title("Painel de Inteligência"); password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"): st.session_state["password_correct"] = True; st.rerun()
            else: st.error("Senha incorreta.")
    return False
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".yml")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"[Pasta] {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([3, 1, 1])
                if c1.button(f"[Ver] {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                if c2.button("[Editar]", key=f"edit_{content_file.path}", help="Editar (desabilitado nesta versão)"): st.warning("A edição será reimplementada no novo Assistente.")
                if c3.button("[Excluir]", key=f"delete_{content_file.path}", help="Excluir este arquivo"): st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                    st.warning(f"Excluir `{content_file.path}`?"); btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                        file_info = st.session_state.pop('file_to_delete'); repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                        if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content', None); st.session_state.pop('viewing_file_name', None)
                        st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                    if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
            else: st.markdown(f"`{content_file.name}`")
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

st.title("Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("Leitor de Dossiês"); st.text("Navegue e visualize os dossiês salvos no repositório.")
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
                if file_name.endswith(".yml"):
                    try: dossier_data = yaml.safe_load(st.session_state.viewing_file_content); render_dossier_from_blueprint(dossier_data)
                    except yaml.YAMLError as e: st.error(f"Erro ao ler o arquivo YAML: {e}"); st.code(st.session_state.viewing_file_content)
                else: st.warning("Formato antigo (.md)."); st.text(st.session_state.viewing_file_content)
            else: st.info("Selecione um dossiê (.yml) para uma visualização rica.")

# --- PÁGINA "CARREGAR DOSSIÊ" COM O NOVO CONSTRUTOR DINÂMICO ---
elif selected_action == "Carregar Dossiê":
    st.header("Construtor de Dossiês")
    st.info("Adicione e preencha os componentes para montar seu dossiê passo a passo.")

    # Inicializa a lista de componentes no estado da sessão se não existir
    if 'components' not in st.session_state:
        st.session_state.components = []

    with st.form("dossier_dynamic_form"):
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.subheader("1. Metadados Gerais")
        c1, c2 = st.columns(2)
        meta_title = c1.text_input("Título Principal do Painel", "PAINEL DE DOSSIÊS TÉCNICOS", key="meta_title")
        meta_icon = c2.text_input("Ícone Principal", "Ex: [Taca]", key="meta_icon")
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.subheader("2. Seções de Conteúdo")
        
        # Renderiza os componentes que já foram adicionados
        for i, comp in enumerate(st.session_state.components):
            st.markdown(f"**Componente {i+1}: {comp['tipo'].replace('_', ' ').title()}**")
            if comp['tipo'] == 'titulo_secao':
                comp['icone'] = st.text_input("Ícone", value=comp.get('icone', ''), key=f"icon_{i}")
                comp['texto'] = st.text_input("Texto do Título", value=comp.get('texto', ''), key=f"text_{i}")
            elif comp['tipo'] == 'subtitulo_com_icone':
                comp['icone'] = st.text_input("Ícone", value=comp.get('icone', ''), key=f"icon_{i}")
                comp['texto'] = st.text_input("Texto do Subtítulo", value=comp.get('texto', ''), key=f"text_{i}")
            elif comp['tipo'] == 'paragrafo':
                comp['texto'] = st.text_area("Texto do Parágrafo", value=comp.get('texto', ''), key=f"text_{i}")
            elif comp['tipo'] == 'lista_simples':
                items_text = "\n".join(comp.get('itens', []))
                new_items_text = st.text_area("Itens (um por linha)", value=items_text, key=f"items_{i}")
                comp['itens'] = [item.strip() for item in new_items_text.split('\n') if item.strip()]
            st.divider()
        
        st.markdown('</div>', unsafe_allow_html=True)
        
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        st.subheader("3. Informações para Salvar")
        c1, c2, c3 = st.columns(3)
        pais = c1.text_input("País*", placeholder="Ex: Inglaterra", key="pais")
        liga = c2.text_input("Liga*", placeholder="Ex: Premier League", key="liga")
        temporada = c3.text_input("Temporada*", placeholder="Ex: 2025-26", key="temporada")
        st.markdown('</div>', unsafe_allow_html=True)

        # Botão de salvar dentro do formulário
        if st.form_submit_button("💾 Gerar e Salvar Dossiê", type="primary", use_container_width=True):
            if not all([pais, liga, temporada]):
                st.error("Os campos País, Liga e Temporada são obrigatórios para salvar o arquivo.")
            else:
                dossier_data = {'metadata': {'titulo_principal': meta_title, 'icone_principal': meta_icon}, 'componentes': st.session_state.components}
                yaml_string = yaml.dump(dossier_data, sort_keys=False, allow_unicode=True, indent=2)
                liga_fmt = liga.replace(' ', '_'); pais_fmt = pais.replace(' ', '_'); file_name = f"Dossie_{liga_fmt}_{pais_fmt}.yml"
                path_parts = [pais.replace(" ", "_"), liga.replace(" ", "_"), temporada]; full_path = "/".join(path_parts) + "/" + file_name
                commit_message = f"Adiciona dossiê via construtor: {file_name}"
                with st.spinner("Gerando e salvando arquivo YAML..."):
                    try:
                        repo.create_file(full_path, commit_message, yaml_string)
                        st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                        st.code(yaml_string, language="yaml")
                        st.session_state.components = [] # Limpa para o próximo
                    except Exception as e:
                        st.error(f"Ocorreu um erro ao salvar: {e}")

    # Botões para adicionar componentes (fora do formulário principal)
    st.subheader("Adicionar Novos Componentes")
    c1, c2, c3, c4 = st.columns(4)
    if c1.button("➕ Título de Seção"):
        st.session_state.components.append({'tipo': 'titulo_secao', 'icone': '■', 'texto': ''})
        st.rerun()
    if c2.button("➕ Subtítulo"):
        st.session_state.components.append({'tipo': 'subtitulo_com_icone', 'icone': '•', 'texto': ''})
        st.rerun()
    if c3.button("➕ Parágrafo"):
        st.session_state.components.append({'tipo': 'paragrafo', 'texto': ''})
        st.rerun()
    if c4.button("➕ Lista"):
        st.session_state.components.append({'tipo': 'lista_simples', 'itens': []})
        st.rerun()

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

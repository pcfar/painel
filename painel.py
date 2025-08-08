# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v12.2: Correção de Layout e Estabilidade
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO E ESTILOS ---
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
            .comp-paragraph { font-size: 1.1rem; color: #A0AEC0; line-height: 1.9; margin-bottom: 1rem; white-space: pre-wrap; }
            .comp-simple-list ul { list-style-type: none; padding-left: 1rem; margin-top: 1rem; }
            .comp-simple-list li { margin-bottom: 0.7rem; color: #A0AEC0; font-size: 1.1rem; }
            .comp-simple-list li::before { content: "▪"; color: #63B3ED; margin-right: 12px; font-size: 1.2rem; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADOR E FUNÇÕES AUXILIARES ---
def render_dossier_from_blueprint(data: dict):
    st.markdown('<div class="dossier-container">', unsafe_allow_html=True)
    if 'metadata' in data: meta = data['metadata']; st.markdown(f'<h1 class="comp-main-title"><span>{meta.get("icone_principal", "📄")}</span> {meta.get("titulo_principal", "Dossiê")}</h1>', unsafe_allow_html=True)
    if 'componentes' in data:
        for comp in data['componentes']:
            tipo = comp.get('tipo');
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
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".yml")], key=lambda x: x.name)
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
                try:
                    dossier_data = yaml.safe_load(st.session_state.viewing_file_content)
                    if isinstance(dossier_data, dict):
                        render_dossier_from_blueprint(dossier_data)
                    else:
                        st.warning("⚠️ Formato Inesperado"); st.code(st.session_state.viewing_file_content, language="yaml")
                except yaml.YAMLError:
                    st.error("⚠️ Formato de Arquivo Inválido ou Corrompido"); st.info("Este arquivo não pôde ser lido."); st.code(st.session_state.viewing_file_content, language="text")
            else: st.info("Selecione um dossiê para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê")
    st.info("Selecione o tipo de dossiê para ver os campos específicos e preencha as informações.")

    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")

    # Template 1: Dossiê de Liga
    if dossier_type == "D1 P1 - Análise da Liga":
        st.subheader("Template: Análise da Liga")
        # --- CÓDIGO CORRIGIDO: Linhas de st.markdown removidas ---
        with st.form("liga_form"):
            st.subheader("Informações de Arquivo")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*", key="pais_d1p1"); 
            liga = c2.text_input("Liga*", key="liga_d1p1"); 
            temporada = c3.text_input("Temporada*", key="temp_d1p1")
            
            st.divider()

            st.subheader("Conteúdo do Dossiê")
            contexto = st.text_area("Contexto Geral da Liga")
            formato = st.text_area("Formato da Competição (um item por linha)")
            
            if st.form_submit_button("Gerar Dossiê", type="primary", use_container_width=True):
                dossier_data = {
                    'metadata': {'titulo_principal': f"ANÁLISE DA LIGA: {liga.upper()}", 'icone_principal': "🏆"},
                    'componentes': [
                        {'tipo': 'titulo_secao', 'icone': '🌍', 'texto': f'{liga} — Análise Estrutural {temporada}'},
                        {'tipo': 'subtitulo_com_icone', 'icone': '📖', 'texto': 'Contexto Geral'},
                        {'tipo': 'paragrafo', 'texto': contexto},
                        {'tipo': 'subtitulo_com_icone', 'icone': '📐', 'texto': 'Formato da Competição'},
                        {'tipo': 'lista_simples', 'itens': [item.strip() for item in formato.split('\n') if item.strip()]},
                    ]
                }
                yaml_string = yaml.dump(dossier_data, sort_keys=False, allow_unicode=True, indent=2)
                file_name = f"D1P1_Analise_Liga_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.yml"
                path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                with st.spinner("Salvando..."):
                    try: repo.create_file(full_path, f"Adiciona: {file_name}", yaml_string); st.success(f"Salvo com sucesso: {full_path}")
                    except Exception as e: st.error(f"Erro ao salvar: {e}")

    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

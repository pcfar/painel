# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v10.1: Reintrodução dos 6 Tipos de Dossiê
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO E ESTILOS (sem alterações) ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            .dossier-viewer { line-height: 1.9; font-size: 1.1rem; color: #E2E8F0; }
            .dossier-viewer h1 { color: #63B3ED; font-size: 2.2rem; border-bottom: 2px solid #4A5568; padding-bottom: 10px; margin-bottom: 2rem; }
            .dossier-viewer h3 { color: #FFFFFF; font-size: 1.6rem; margin-top: 2.5rem; margin-bottom: 1.5rem; }
            .dossier-viewer p { margin-bottom: 0.5rem; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; }
            .dossier-viewer li { padding-left: 1.5em; text-indent: -1.5em; margin-bottom: 0.7rem; }
            .dossier-viewer li::before { content: "•"; color: #63B3ED; font-size: 1.5em; line-height: 1; vertical-align: middle; margin-right: 10px; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
            .nav-link { border-radius: 8px; margin: 0px 5px 5px 5px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADORES E FUNÇÕES AUXILIARES (sem alterações) ---
def format_dossier_to_html(content: str) -> str:
    html_output = ["<div class='dossier-viewer'>"]; lines = content.split('\n'); in_list = False
    for line in lines:
        line = line.strip()
        if not line: continue
        if not line.startswith(('•', '- ')) and in_list: html_output.append("</ul>"); in_list = False
        if line.lower().startswith("dossiê tático:") or line.lower().startswith("dossiê técnico-tático:"): html_output.append(f"<h1>{line}</h1>")
        elif re.match(r'^\d+\.\s', line): html_output.append(f"<h3>{line}</h3>")
        elif line.startswith(('• ', '- ')):
            if not in_list: html_output.append("<ul>"); in_list = True
            html_output.append(f"<li>{line[2:]}</li>")
        elif ':' in line: parts = line.split(':', 1); html_output.append(f"<p><strong>{parts[0].strip()}:</strong>{parts[1].strip()}</p>")
        else: html_output.append(f"<p>{line}</p>")
    if in_list: html_output.append("</ul>")
    html_output.append("</div>"); return "".join(html_output)

def render_dossier_from_blueprint(data: dict):
    # Mantido para compatibilidade com arquivos .yml antigos, se houver.
    st.markdown('<div class="dossier-container">', unsafe_allow_html=True) # A classe CSS pode precisar de ajuste
    # ... (lógica de renderização yml omitida para brevidade) ...

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
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and (f.name.endswith(".yml") or f.name.endswith(".md"))], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"[Pasta] {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([3, 1, 1])
                if c1.button(f"[Ver] {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                if c2.button("[Editar]", key=f"edit_{content_file.path}", help="Editar (desabilitado)"): st.warning("A edição será reimplementada no futuro.")
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
                else: formatted_html = format_dossier_to_html(st.session_state.viewing_file_content); st.markdown(formatted_html, unsafe_allow_html=True)
            else: st.info("Selecione um arquivo para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê")
    st.info("Selecione o tipo de dossiê para ver os campos específicos e preencha as informações.")

    # --- MUDANÇA AQUI: LISTA COMPLETA DOS 6 DOSSIÊS ---
    dossier_type_options = [
        "",
        "D1 P1 - Análise da Liga",
        "D1 P2 - Análise dos Clubes Dominantes da Liga",
        "D2 P1 - Análise Comparativa de Planteis",
        "D2 P2 - Estudo Técnico e Tático dos Clubes",
        "D3 - Análise Tática (Pós Rodada)",
        "D4 - Briefing Semanal (Pré Rodada)"
    ]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")

    help_text_md = "Guia Rápido:\n- Título: Comece com 'Dossiê Técnico-Tático:'\n- Seções: '1. Nome da Seção'\n- Listas: '- Item da lista'\n- Destaques: 'Palavra-chave: Descrição'"

    # --- FORMULÁRIOS PARA CADA TIPO DE DOSSIÊ ---

    if dossier_type == "D1 P1 - Análise da Liga":
        with st.form("d1_p1_form"):
            st.subheader("Template: Análise da Liga")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*", placeholder="Ex: Inglaterra")
            liga = c2.text_input("Liga*", placeholder="Ex: Premier League")
            temporada = c3.text_input("Temporada*", placeholder="Ex: 2025-26")
            conteudo = st.text_area("Conteúdo do Dossiê*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary", use_container_width=True):
                # Lógica de salvar (exemplo)
                file_name = f"D1P1_Analise_Liga_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.md"
                st.success(f"Arquivo a ser salvo: {file_name}")

    elif dossier_type == "D1 P2 - Análise dos Clubes Dominantes da Liga":
        with st.form("d1_p2_form"):
            st.subheader("Template: Clubes Dominantes")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*", placeholder="Ex: Espanha")
            liga = c2.text_input("Liga*", placeholder="Ex: La Liga")
            temporada = c3.text_input("Temporada*", placeholder="Ex: 2025-26")
            conteudo = st.text_area("Conteúdo da Análise dos Clubes*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary", use_container_width=True):
                file_name = f"D1P2_Clubes_Dominantes_{liga.replace(' ', '_')}.md"
                st.success(f"Arquivo a ser salvo: {file_name}")

    elif dossier_type == "D2 P1 - Análise Comparativa de Planteis":
        with st.form("d2_p1_form"):
            st.subheader("Template: Comparativo de Planteis")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*", placeholder="Ex: Itália")
            liga = c2.text_input("Liga*", placeholder="Ex: Serie A")
            clube = c3.text_input("Clube*", placeholder="Ex: Juventus")
            temporada_atual = st.text_input("Temporada Atual*", placeholder="Ex: 2025-26")
            conteudo = st.text_area("Conteúdo da Análise Comparativa*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary", use_container_width=True):
                file_name = f"D2P1_Planteis_{clube.replace(' ', '_')}_{temporada_atual}.md"
                st.success(f"Arquivo a ser salvo: {file_name}")

    elif dossier_type == "D2 P2 - Estudo Técnico e Tático dos Clubes":
        with st.form("d2_p2_form"):
            st.subheader("Template: Estudo Técnico e Tático")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*", placeholder="Ex: Alemanha")
            liga = c2.text_input("Liga*", placeholder="Ex: Bundesliga")
            clube = c3.text_input("Clube*", placeholder="Ex: Bayern München")
            temporada = st.text_input("Temporada*", placeholder="Ex: 2025-26")
            conteudo = st.text_area("Conteúdo do Estudo Tático*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary", use_container_width=True):
                file_name = f"D2P2_Estudo_Tatico_{clube.replace(' ', '_')}_{temporada}.md"
                st.success(f"Arquivo a ser salvo: {file_name}")

    elif dossier_type == "D3 - Análise Tática (Pós Rodada)":
        with st.form("d3_form"):
            st.subheader("Template: Análise Pós Rodada")
            c1, c2, c3 = st.columns(3)
            liga = c1.text_input("Liga*", placeholder="Ex: Brasileirão Série A")
            temporada = c2.text_input("Temporada*", placeholder="Ex: 2025")
            rodada = c3.text_input("Rodada*", placeholder="Ex: 15")
            c1, c2 = st.columns(2)
            time_casa = c1.text_input("Time da Casa*")
            time_visitante = c2.text_input("Time Visitante*")
            conteudo = st.text_area("Conteúdo da Análise da Partida*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary", use_container_width=True):
                file_name = f"D3_Pos_Rodada_{time_casa.replace(' ', '_')}_vs_{time_visitante.replace(' ', '_')}_R{rodada}.md"
                st.success(f"Arquivo a ser salvo: {file_name}")
    
    elif dossier_type == "D4 - Briefing Semanal (Pré Rodada)":
        with st.form("d4_form"):
            st.subheader("Template: Briefing Pré Rodada")
            c1, c2, c3 = st.columns(3)
            liga = c1.text_input("Liga*", placeholder="Ex: Brasileirão Série A")
            clube_analisado = c2.text_input("Clube Analisado*", placeholder="Nosso Clube")
            rodada = c3.text_input("Rodada*", placeholder="Ex: 16")
            adversario = st.text_input("Próximo Adversário*")
            conteudo = st.text_area("Conteúdo do Briefing*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary", use_container_width=True):
                file_name = f"D4_Briefing_{clube_analisado.replace(' ', '_')}_vs_{adversario.replace(' ', '_')}_R{rodada}.md"
                st.success(f"Arquivo a ser salvo: {file_name}")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v11.0: Solução Definitiva com Renderizador Markdown Profissional
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml
import markdown2 # Importa a nova biblioteca

# --- 1. CONFIGURAÇÃO E ESTILOS FINAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """CSS de alta fidelidade para renderizar o HTML gerado pelo Markdown2."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            
            .dossier-viewer { line-height: 1.8; font-size: 1.1rem; color: #E2E8F0; }
            .dossier-viewer h1 { 
                font-size: 2.2rem; font-weight: 900; color: #FFFFFF; 
                border-bottom: 3px solid #3182CE; padding-bottom: 0.5rem; margin-bottom: 2rem; 
            }
            .dossier-viewer h2 { 
                font-size: 1.6rem; font-weight: 700; color: #E2E8F0; 
                margin-top: 2.5rem; margin-bottom: 1.5rem; 
            }
            .dossier-viewer h3 { 
                font-size: 1.3rem; font-weight: 700; color: #a5b4fc; 
                margin-top: 2rem; margin-bottom: 1rem; 
            }
            .dossier-viewer p { margin-bottom: 1rem; color: #A0AEC0; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer em { font-style: italic; color: #90cdf4; }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; }
            .dossier-viewer li { 
                margin-bottom: 0.7rem; color: #A0AEC0;
                padding-left: 1.5em; text-indent: -1.5em;
            }
            .dossier-viewer li::before { 
                content: "▪"; color: #63B3ED; margin-right: 10px; 
                font-size: 1.2rem;
            }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES AUXILIARES ---
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None

def check_password():
    """Verifica a senha com um layout de login centralizado e profissional."""
    if st.session_state.get("password_correct", False):
        return True

    # Cria colunas para centralizar o conteúdo
    _, center_col, _ = st.columns([1, 1, 1])

    with center_col:
        st.title("Painel de Inteligência")
        st.write(" ") # Adiciona um espaço vertical

        # Usamos um container para agrupar os elementos do formulário
        with st.container(border=True):
            st.subheader("Login de Acesso")
            password = st.text_input(
                "Senha de Acesso", 
                type="password", 
                key="password_input", 
                label_visibility="collapsed",
                placeholder="Digite sua senha"
            )
            
            # Botão de acesso com destaque (primary) e largura total do container
            if st.button("Acessar Painel", type="primary", use_container_width=True):
                with st.spinner("Verificando..."):
                    if password == st.secrets.get("APP_PASSWORD"):
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
    
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
                if c2.button("[Editar]", key=f"edit_{content_file.path}", help="Editar (desabilitado)"): st.warning("A edição será reimplementada em breve.")
                if c3.button("[Excluir]", key=f"delete_{content_file.path}", help="Excluir este arquivo"): st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                    st.warning(f"Excluir `{content_file.path}`?"); btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                        file_info = st.session_state.pop('file_to_delete'); repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                        if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content', None); st.session_state.pop('viewing_file_name', None)
                        st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                    if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
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
                # A ROTA PRINCIPAL AGORA USA MARKDOWN2 PARA ARQUIVOS .MD
                if file_name.endswith(".md"):
                    # Converte o conteúdo Markdown em HTML com a biblioteca profissional
                    html_content = markdown2.markdown(st.session_state.viewing_file_content, extras=['tables', 'fenced-code-blocks'])
                    # Envolve no nosso container de estilo e renderiza
                    st.markdown(f"<div class='dossier-viewer'>{html_content}</div>", unsafe_allow_html=True)
                elif file_name.endswith(".yml"):
                    st.warning("Formato .yml antigo. Considere converter para .md para a nova visualização.")
                    st.code(st.session_state.viewing_file_content, language="yaml")
            else: st.info("Selecione um arquivo para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê")
    st.info("Selecione o tipo de dossiê, preencha as informações e o conteúdo em Markdown.")

    dossier_type_options = [
        "", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes",
        "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes",
        "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"
    ]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")

    help_text_md = "Guia Rápido:\n- Título Principal: # Título\n- Subtítulo: ## Subtítulo\n- Listas: - Item da lista\n- Negrito: **texto**"

    # Função para salvar no GitHub (para evitar repetição de código)
    def salvar_dossie(file_name_pattern, path_parts, content):
        if not all(path_parts + [content]):
            st.error("Todos os campos marcados com * são obrigatórios.")
            return
        
        file_name = file_name_pattern.format(**st.session_state).replace(" ", "_") + ".md"
        full_path = "/".join([p.replace(" ", "_") for p in path_parts]) + "/" + file_name
        commit_message = f"Adiciona: {file_name}"
        
        with st.spinner("Salvando dossiê..."):
            try:
                repo.create_file(full_path, commit_message, content)
                st.success(f"Dossiê '{full_path}' salvo com sucesso!")
            except Exception as e:
                st.error(f"Ocorreu um erro ao salvar: {e}")

    # Template 1
    if dossier_type == "D1 P1 - Análise da Liga":
        with st.form("d1_p1_form"):
            st.subheader("Template: Análise da Liga")
            c1, c2, c3 = st.columns(3)
            st.session_state.pais = c1.text_input("País*")
            st.session_state.liga = c2.text_input("Liga*")
            st.session_state.temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Conteúdo do Dossiê*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"):
                salvar_dossie("D1P1_Analise_Liga_{liga}_{pais}", [st.session_state.pais, st.session_state.liga, st.session_state.temporada], conteudo)

    # Template 2
    elif dossier_type == "D1 P2 - Análise dos Clubes Dominantes":
        with st.form("d1_p2_form"):
            st.subheader("Template: Clubes Dominantes")
            c1, c2, c3 = st.columns(3)
            st.session_state.pais = c1.text_input("País*")
            st.session_state.liga = c2.text_input("Liga*")
            st.session_state.temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Conteúdo da Análise*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"):
                salvar_dossie("D1P2_Clubes_Dominantes_{liga}", [st.session_state.pais, st.session_state.liga, st.session_state.temporada], conteudo)

    # ... E assim por diante para os outros 4 formulários, todos seguindo este modelo simples.
    # Adicionando os demais como placeholders para não sobrecarregar
    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' será adicionado em breve, seguindo este novo modelo simplificado.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

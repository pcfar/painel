# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v16.8: Alinhamento Definitivo de Listas e Intertítulos
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
    """CSS de alta fidelidade com os refinamentos finais de estilo."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            
            .dossier-viewer { 
                line-height: 1.7; 
                font-size: 1.1rem; 
                color: #F3F4F6;
            }
            .dossier-viewer h1 { 
                font-size: 2.2rem; font-weight: 900; color: #FFFFFF; 
                border-bottom: 3px solid #3182CE; padding-bottom: 0.5rem; margin-bottom: 2rem; 
            }
            .dossier-viewer h2 { 
                font-size: 1.7rem; font-weight: 700; color: #38BDF8;
                margin-top: 3rem; margin-bottom: 1.5rem; 
                padding-left: 1rem;
                border-left: 4px solid #38BDF8;
            }
            .dossier-viewer h3 { 
                font-size: 1.4rem; font-weight: 700; color: #FACC15;
                margin-top: 2.5rem; margin-bottom: 1rem; 
            }
            .dossier-viewer p { 
                margin-bottom: 1rem; 
                color: #F3F4F6;
                padding-left: 0; 
                text-indent: 0;
            }
            .dossier-viewer strong { 
                color: #FACC15; /* Cor amarela/gold para todos os negritos */
                font-weight: 700; /* Peso 700 para consistência */
                text-shadow: none; /* Removido o glow para um look mais limpo */
            }
            
            /* --- MUDANÇA CENTRAL: Novo sistema de listas para alinhamento perfeito --- */
            .dossier-viewer ul { 
                list-style-type: none; 
                padding-left: 0; 
                margin-top: 1rem; 
            }
            .dossier-viewer li { 
                color: #F3F4F6;
                margin-bottom: 1rem;
                position: relative;      /* Cria o contexto para o marcador */
                padding-left: 2em;       /* Cria espaço à esquerda para o marcador */
            }
            .dossier-viewer li::before { 
                content: "▪"; 
                color: #63B3ED; 
                position: absolute;      /* Posiciona o marcador no espaço criado */
                left: 0;
                top: 0.1em;              /* Ajuste fino da altura do marcador */
                font-size: 1.2rem;
            }

            .dossier-viewer hr { border: none; border-top: 2px solid #4A5568; margin: 3rem 0; }
            .dossier-viewer table { width: 100%; border-collapse: collapse; margin: 1.5rem 0; background-color: #2D3748; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); }
            .dossier-viewer th, .dossier-viewer td { padding: 1rem; text-align: left; font-size: 1rem; color: #F3F4F6; border-bottom: 1px solid #4A5568;}
            .dossier-viewer th { background-color: #3B82F6; font-weight: 700; }
            .dossier-viewer tr:nth-child(even) { background-color: rgba(74, 85, 104, 0.5); }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

# --- FUNÇÕES AUXILIARES E CÓDIGO PRINCIPAL (SEM ALTERAÇÕES) ---
def sanitize_text(text: str) -> str:
    return text.replace('\u00A0', ' ').replace('\u2011', '-')
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); return g.get_repo(f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}")
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
def display_repo_structure(repo, path=""):
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md")], key=lambda x: x.name)
        search_term = st.session_state.get("search_term", "")
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"):
                display_repo_structure(repo, content_dir.path)
        for content_file in files:
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8")
                    st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
            with col2:
                if st.button("✏️", key=f"edit_{content_file.path}", help="Editar Dossiê", use_container_width=True): st.warning("Função de edição em desenvolvimento.")
            with col3:
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

if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês")
    default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index, key="main_menu")
    st.session_state.selected_action = selected_action

st.title("Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório"); st.text_input("Filtrar...", label_visibility="collapsed", placeholder="Filtrar por nome do arquivo...", key="search_term"); st.divider()
            display_repo_structure(repo)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}"); st.divider()
                sanitized_content = sanitize_text(st.session_state.viewing_file_content)
                html_content = markdown2.markdown(sanitized_content, extras=['tables', 'fenced-code-blocks', 'blockquote', 'pyshell', 'break-on-newline'])
                st.markdown(f"<div class='dossier-viewer'>{html_content}</div>", unsafe_allow_html=True)
            else: st.info("Selecione um arquivo para visualizar.")
elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê"); st.info("Selecione o tipo de dossiê, preencha as informações e o conteúdo em Markdown.")
    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes da Liga", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")
    help_text_md = "Guia Rápido:\n- Título: # Título\n- Subtítulo: ## Subtítulo\n- Intertítulo: ### Título\n- Listas: - Item da lista\n- Destaque: **texto**"
    def save_dossier(repo, file_name_template: str, path_parts: list, content: str, required_fields: dict):
        if not all(required_fields.values()): st.error("Todos os campos marcados com * são obrigatórios."); return
        format_dict = {k: v for k, v in required_fields.items() if k in ['liga', 'pais']}
        file_name = file_name_template.format(**{k: v.replace(' ', '_') for k, v in format_dict.items()}) + ".md"
        full_path = "/".join([p.replace(" ", "_") for p in path_parts]) + "/" + file_name
        commit_message = f"Adiciona: {file_name}"
        with st.spinner("Salvando dossiê..."):
            try:
                repo.create_file(full_path, commit_message, content)
                st.success(f"Dossiê '{full_path}' salvo com sucesso!")
            except Exception as e:
                st.error(f"Ocorreu um erro ao salvar: {e}")
                st.info("Verifique se um arquivo com este nome já não existe.")
    if dossier_type == "D1 P1 - Análise da Liga":
        with st.form("d1_p1_form", clear_on_submit=True):
            st.subheader("Template: Análise da Liga")
            c1, c2, c3 = st.columns(3); pais = c1.text_input("País*"); liga = c2.text_input("Liga*"); temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Resumo (Conteúdo do Dossiê)*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"):
                save_dossier(repo, "D1P1_Analise_Liga_{liga}_{pais}", [pais, liga, temporada], conteudo, {"liga": liga, "pais": pais, "temporada": temporada, "conteudo": conteudo})
    elif dossier_type: st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")
elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

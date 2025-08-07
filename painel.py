# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - Versão Final com Navegação na Sidebar
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
# Importa o componente de menu para a sidebar
from streamlit_option_menu import option_menu

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS GLOBAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="🗂️", layout="wide")

def apply_custom_styling():
    """Aplica CSS personalizado para uma visualização de dossiê moderna e atraente, incluindo tabelas."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
            
            /* Estilo geral do visualizador de dossiê */
            .dossier-viewer {
                font-family: 'Inter', sans-serif;
                line-height: 1.7;
                color: #d1d5db;
            }
            .dossier-viewer h1 {
                font-size: 2.5rem; font-weight: 700; color: #ffffff;
                border-bottom: 2px solid #4f46e5; padding-bottom: 0.5rem; margin-bottom: 1.5rem;
            }
            .dossier-viewer blockquote {
                border-left: 4px solid #6366f1; padding: 1rem 1.5rem; margin-left: 0;
                font-style: italic; color: #e5e7eb; background-color: rgba(49, 46, 129, 0.2);
                border-radius: 0.5rem;
            }
            .dossier-viewer h3 {
                font-size: 1.75rem; font-weight: 600; color: #f9fafb; margin-top: 3rem;
                margin-bottom: 1.5rem; border-bottom: 1px solid #4b5563; padding-bottom: 0.5rem;
            }
            .dossier-viewer h3::before { content: '📂 '; }
            
            /* Estilo aprimorado para tabelas */
            .dossier-viewer table {
                width: 100%; border-collapse: collapse; margin-top: 1.5rem; margin-bottom: 1.5rem;
            }
            .dossier-viewer th, .dossier-viewer td {
                padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #374151;
            }
            .dossier-viewer th { background-color: #1f2937; color: #e5e7eb; font-weight: 600; }
            .dossier-viewer tr:nth-child(even) { background-color: #111827; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. AUTENTICAÇÃO E CONEXÃO COM GITHUB ---
def check_password():
    """Verifica se a senha do usuário está correta. Usa st.secrets."""
    if st.session_state.get("password_correct", False):
        return True
    
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Painel de Inteligência")
        password = st.text_input("Senha de Acesso", type="password", key="password_input")
        if st.button("Acessar Painel"):
            if password == st.secrets.get("APP_PASSWORD"):
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("😕 Senha incorreta. Tente novamente.")
    return False

@st.cache_resource
def get_github_repo():
    """Conecta-se ao repositório do GitHub usando as secrets."""
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Falha na conexão com o repositório do GitHub: {e}")
        return None

# --- 3. FUNÇÕES AUXILIARES DE LÓGICA ---
def parse_path_to_form(path):
    """Analisa o caminho do arquivo para preencher os campos do formulário de edição."""
    try:
        parts = [p for p in path.split('/') if p] # Remove partes vazias
        file_name = parts[-1]
        
        st.session_state.pais = parts[0].replace("_", " ")
        st.session_state.liga = parts[1].replace("_", " ")
        st.session_state.temporada = parts[2]
        
        if file_name == "Dossiê_Liga.md":
            st.session_state.tipo_dossie = "Dossiê de Liga"
        elif file_name == "Dossiê_Clube.md":
            st.session_state.tipo_dossie = "Dossiê de Clube"
            st.session_state.clube = parts[3].replace("_", " ")
        elif file_name in ["Briefing_Pre-Jogo.md", "Relatorio_Pos-Jogo.md"]:
            st.session_state.tipo_dossie = "Briefing Pré-Jogo" if file_name.startswith("Briefing") else "Relatório Pós-Jogo"
            st.session_state.clube = parts[3].replace("_", " ")
            st.session_state.rodada = parts[4].replace("_", " ")
    except Exception:
        st.warning("Não foi possível analisar o caminho do arquivo. Preencha os campos manualmente.")

# --- INÍCIO DA EXECUÇÃO DA APLICAÇÃO ---
if not check_password():
    st.stop()

# Aplica estilos e conecta ao repo uma vez autenticado
apply_custom_styling()
repo = get_github_repo()

# --- 4. NAVEGAÇÃO PRINCIPAL NA SIDEBAR ---
with st.sidebar:
    st.info(f"Autenticado com sucesso. {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    
    # Define a página padrão, considerando o fluxo de edição
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
st.title("🗂️ Sistema de Inteligência Tática")

# ---- PÁGINA 1: LEITOR DE DOSSIÊS ----
if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês")
    st.text("Navegue, filtre e visualize todos os dossiês salvos no repositório.")

    if repo:
        col1, col2 = st.columns([1, 2])
        
        with col1: # Coluna de Navegação
            st.subheader("Navegador do Repositório")
            search_term = st.text_input("🔎 Filtrar por nome do arquivo...", key="search_term_reader")
            st.divider()

            def display_files_for_reading(path=""):
                try:
                    contents = repo.get_contents(path)
                    dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
                    files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".md") and search_term.lower() in f.name.lower()], key=lambda x: x.name)
                    
                    for content_dir in dirs:
                        with st.expander(f"📁 {content_dir.name}"):
                            display_files_for_reading(content_dir.path)
                    
                    for content_file in files:
                        c1, c2, c3 = st.columns([3, 1, 1])
                        c1.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", on_click=lambda c=content_file: st.session_state.update(viewing_file_content=base64.b64decode(c.content).decode('utf-8'), viewing_file_name=c.name), use_container_width=True)
                        
                        if c2.button("✏️", key=f"edit_{content_file.path}", help="Editar este arquivo"):
                            parse_path_to_form(content_file.path)
                            st.session_state.edit_mode = True
                            st.session_state.file_to_edit_path = content_file.path
                            st.session_state.conteudo_md = base64.b64decode(content_file.content).decode('utf-8')
                            st.session_state.selected_action = "Carregar Dossiê"
                            st.rerun()

                        if c3.button("🗑️", key=f"delete_{content_file.path}", help="Excluir este arquivo"):
                            st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}

                        if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                            st.warning(f"Excluir `{content_file.path}`?")
                            btn_c1, btn_c2 = st.columns(2)
                            if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                                file_info = st.session_state['file_to_delete']
                                repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                                del st.session_state['file_to_delete']
                                if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']):
                                    del st.session_state['viewing_file_content'], st.session_state['viewing_file_name']
                                st.success(f"Arquivo '{file_info['path']}' excluído.")
                                st.rerun()
                            if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"):
                                del st.session_state['file_to_delete']
                                st.rerun()
                except Exception as e:
                    st.error(f"Erro ao listar arquivos: {e}")
            
            display_files_for_reading()

        with col2: # Coluna de Visualização
            st.subheader("Visualizador de Conteúdo")
            if "viewing_file_content" in st.session_state:
                st.markdown(f"#### {st.session_state.viewing_file_name}")
                st.divider()
                cleaned_content = re.sub(r':contentReference\[.*?\]\{.*?\}', '', st.session_state.viewing_file_content)
                st.markdown(f"<div class='dossier-viewer'>{cleaned_content}</div>", unsafe_allow_html=True)
            else:
                st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")

# ---- PÁGINA 2: CARREGAR / EDITAR DOSSIÊ ----
elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get('edit_mode', False)
    header_text = "✏️ Editor de Dossiê" if is_edit_mode else "📤 Carregar Novo Dossiê"
    st.header(header_text)

    if repo:
        with st.form("dossier_form", clear_on_submit=False):
            st.selectbox("Tipo de Dossiê*", ["Dossiê de Liga", "Dossiê de Clube", "Briefing Pré-Jogo", "Relatório Pós-Jogo"], key="tipo_dossie")
            c1, c2, c3 = st.columns(3)
            c1.text_input("País*", placeholder="Ex: Brasil", key="pais")
            c2.text_input("Liga*", placeholder="Ex: Serie A", key="liga")
            c3.text_input("Temporada*", placeholder="Ex: 2025", key="temporada")
            c1, c2 = st.columns(2)
            c1.text_input("Clube (se aplicável)", placeholder="Ex: Flamengo", key="clube")
            c2.text_input("Rodada / Adversário (se aplicável)", placeholder="Ex: Rodada_01_vs_Palmeiras", key="rodada")
            st.text_area("Conteúdo Markdown*", height=300, placeholder="Cole aqui o dossiê completo em formato Markdown...", key="conteudo_md")
            
            submit_label = "Atualizar Dossiê no GitHub" if is_edit_mode else "Salvar Novo Dossiê no GitHub"
            if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                # Lógica de validação e submissão
                if not all([st.session_state.pais, st.session_state.liga, st.session_state.temporada, st.session_state.conteudo_md]):
                    st.error("Todos os campos com * são obrigatórios.")
                else:
                    path_parts = [st.session_state.pais.replace(" ", "_"), st.session_state.liga.replace(" ", "_"), st.session_state.temporada]
                    file_name = "" 
                    tipo = st.session_state.tipo_dossie
                    if tipo == "Dossiê de Liga": file_name = "Dossiê_Liga.md"
                    elif tipo == "Dossiê de Clube":
                        if not st.session_state.clube: st.error("'Clube' é obrigatório para este tipo de dossiê.")
                        else: path_parts.append(st.session_state.clube.replace(" ", "_")); file_name = "Dossiê_Clube.md"
                    elif tipo in ["Briefing Pré-Jogo", "Relatório Pós-Jogo"]:
                        if not st.session_state.clube or not st.session_state.rodada: st.error("'Clube' e 'Rodada/Adversário' são obrigatórios.")
                        else:
                            path_parts.extend([st.session_state.clube.replace(" ", "_"), st.session_state.rodada.replace(" ", "_")])
                            file_name = "Briefing_Pre-Jogo.md" if tipo == "Briefing Pré-Jogo" else "Relatorio_Pos-Jogo.md"

                    if file_name:
                        full_path = "/".join(path_parts) + "/" + file_name
                        commit_message = f"Atualiza: {file_name}" if is_edit_mode else f"Adiciona: {file_name}"
                        with st.spinner(f"Aguarde, salvando no repositório GitHub..."):
                            try:
                                if is_edit_mode:
                                    original_path = st.session_state.file_to_edit_path
                                    existing_file = repo.get_contents(original_path)
                                    repo.update_file(original_path, commit_message, st.session_state.conteudo_md, existing_file.sha)
                                    st.success(f"Dossiê '{original_path}' atualizado com sucesso!")
                                else: # Modo de criação
                                    repo.create_file(full_path, commit_message, st.session_state.conteudo_md)
                                    st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                                
                                # Limpa o estado e volta para o leitor após o sucesso
                                for key in ['edit_mode', 'file_to_edit_path', 'pais', 'liga', 'temporada', 'clube', 'rodada', 'conteudo_md', 'tipo_dossie']:
                                    if key in st.session_state: del st.session_state[key]
                                st.session_state.selected_action = "Leitor de Dossiês"
                                st.rerun()

                            except UnknownObjectException:
                                 # Trata o caso de o arquivo original ter sido deletado durante a edição
                                 st.error("Erro: O arquivo original não foi encontrado. Pode ter sido excluído. Tente salvar como um novo dossiê.")
                            except Exception as e: 
                                st.error(f"Ocorreu um erro inesperado: {e}")

        if is_edit_mode:
            if st.button("Cancelar Edição", use_container_width=True):
                # Limpa o estado e volta para o leitor
                for key in ['edit_mode', 'file_to_edit_path', 'pais', 'liga', 'temporada', 'clube', 'rodada', 'conteudo_md', 'tipo_dossie']:
                    if key in st.session_state: del st.session_state[key]
                st.session_state.selected_action = "Leitor de Dossiês"
                st.rerun()

# ---- PÁGINA 3: GERAR COM IA ----
elif selected_action == "Gerar com IA":
    st.header("🧠 Geração de Dossiês com IA")
    st.info("Esta seção agrupa os diferentes tipos de geração de dossiês. (Em desenvolvimento)")

    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê Liga", "Dossiê Clube", "Pós-Jogo", "Pré-Jogo"])
    with tab1: st.write("Interface para gerar Dossiê de Liga...")
    with tab2: st.write("Interface para gerar Dossiê de Clube...")
    with tab3: st.write("Interface para gerar Dossiê Pós-Jogo...")
    with tab4: st.write("Interface para gerar Dossiê Pré-Jogo...")

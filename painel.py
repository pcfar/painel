import streamlit as st
import os
from github import Github, UnknownObjectException
from datetime import datetime
from PIL import Image
import io
import requests
import json
import time
import base64
import pandas as pd
import altair as alt
import pytesseract
import re # Importa a biblioteca para limpeza de texto

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático Final", page_icon="🗂️", layout="wide")

# --- ESTILOS VISUAIS AVANÇADOS PARA O MARKDOWN ---
def apply_custom_styling():
    """Aplica CSS personalizado para uma visualização de dossiê moderna e atraente."""
    st.markdown("""
        <style>
            .dossier-viewer {
                font-family: 'Inter', sans-serif;
                line-height: 1.7;
                color: #d1d5db; /* Cor de texto principal para tema escuro */
            }
            .dossier-viewer h1 {
                font-size: 2.5rem;
                font-weight: 700;
                color: #ffffff;
                border-bottom: 2px solid #4f46e5; /* Borda índigo */
                padding-bottom: 0.5rem;
                margin-bottom: 1.5rem;
            }
            .dossier-viewer blockquote {
                border-left: 4px solid #6366f1; /* Borda índigo mais clara */
                padding: 1rem 1.5rem;
                margin-left: 0;
                font-style: italic;
                color: #e5e7eb;
                background-color: rgba(49, 46, 129, 0.2); /* Fundo índigo transparente */
                border-radius: 0.5rem;
            }
            .dossier-viewer h3 {
                font-size: 1.75rem;
                font-weight: 600;
                color: #f9fafb;
                margin-top: 3rem;
                margin-bottom: 1.5rem;
                border-bottom: 1px solid #4b5563; /* Borda cinza escura */
                padding-bottom: 0.5rem;
            }
            .dossier-viewer h3::before {
                content: '📂 ';
            }
            .dossier-viewer h4 {
                font-size: 1.25rem;
                font-weight: 600;
                color: #e5e7eb;
                margin-top: 2rem;
                margin-bottom: 1rem;
            }
            .dossier-viewer ul {
                list-style-type: none;
                padding-left: 0;
                margin-bottom: 1rem;
            }
            .dossier-viewer li {
                margin-bottom: 0.75rem;
                padding-left: 0.5rem;
                position: relative;
            }
            .dossier-viewer li::before {
                content: '▶️';
                margin-right: 0.75rem;
                font-size: 0.8rem;
            }
             .dossier-viewer strong {
                color: #a5b4fc; /* Cor de destaque índigo */
             }
        </style>
    """, unsafe_allow_html=True)

# --- SISTEMA DE SENHA ÚNICA ---
def check_password():
    """Verifica se a senha do usuário está correta."""
    if st.session_state.get("password_correct", False): return True
    def password_entered():
        if st.session_state.get("password") == st.secrets.get("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else: st.session_state["password_correct"] = False
    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta.")
    return False

# --- FUNÇÕES DE CHAMADA À IA (COM EXPONENTIAL BACKOFF) ---
def gerar_resposta_ia(prompt, imagens_bytes=None):
    # (Esta função permanece a mesma, pois já é robusta)
    pass

# --- FUNÇÕES DO ARQUIVO GITHUB ---
@st.cache_resource
def get_github_repo():
    """Conecta-se ao repositório do GitHub usando as secrets."""
    try:
        if not all(k in st.secrets for k in ["GITHUB_TOKEN", "GITHUB_USERNAME", "GITHUB_REPO_NAME"]):
            st.error("Uma ou mais secrets do GitHub (GITHUB_TOKEN, GITHUB_USERNAME, GITHUB_REPO_NAME) não foram encontradas.")
            return None
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Erro ao conectar com o repositório do GitHub: {e}")
        return None

def display_repo_contents(repo, path=""):
    """Exibe o conteúdo de um repositório do GitHub de forma recursiva."""
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([c for c in contents if c.type == 'file'], key=lambda x: x.name)
        
        for content in dirs:
            with st.expander(f"📁 {content.name}"):
                display_repo_contents(repo, content.path)
        
        for content in files:
            if content.name.endswith(".md"):
                if st.button(f"📄 {content.name}", key=content.path, use_container_width=True):
                    st.session_state.viewing_file_content = base64.b64decode(content.content).decode('utf-8')
                    st.session_state.viewing_file_name = content.name
    except UnknownObjectException:
        try:
            repo.create_file(".gitkeep", "Inicializa o repositório", "", branch="main")
            st.info("Repositório inicializado. Por favor, atualize a página.")
        except Exception as e:
            st.info(f"Este diretório está vazio. Não foi possível inicializar: {e}")
    except Exception as e:
        st.error(f"Erro ao listar o conteúdo do repositório: {e}")
# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    # Aplica o CSS personalizado em toda a aplicação após o login
    apply_custom_styling()

    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")
    
    st.header("Central de Comando")
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)", "Arquivo"])

    with tab1: st.info("Funcionalidade de geração do Dossiê de Liga.")
    with tab2: st.info("Funcionalidade de geração do Dossiê de Clube.")
    with tab3: st.info("Funcionalidade de geração do Dossiê Pós-Jogo.")
    with tab4: st.info("Funcionalidade de geração do Dossiê Pré-Jogo.")

    # --- ABA 5: ARQUIVO DE INTELIGÊNCIA ---
    with tab5:
        st.header("Painel de Arquivo de Inteligência")
        
        repo = get_github_repo()
        if repo:
            col1, col2 = st.columns([1, 2])

            with col1:
                # Módulo de Upload para salvar novos dossiês
                st.subheader("Adicionar Novo Dossiê")
                with st.form("form_arquivo"):
                    st.selectbox("Tipo de Dossiê*", ["Dossiê de Liga", "Dossiê de Clube", "Briefing Pré-Jogo", "Relatório Pós-Jogo"], key="tipo_dossie")
                    st.text_input("País*", placeholder="Ex: Brasil", key="pais")
                    st.text_input("Liga*", placeholder="Ex: Serie A", key="liga")
                    st.text_input("Temporada*", placeholder="Ex: 2025", key="temporada")
                    st.text_input("Clube (se aplicável)", placeholder="Ex: Flamengo", key="clube")
                    st.text_input("Rodada / Adversário (se aplicável)", placeholder="Ex: Rodada_01_vs_Palmeiras", key="rodada")
                    st.text_area("Conteúdo Markdown*", height=200, placeholder="Cole aqui o dossiê completo...", key="conteudo_md")
                    
                    if st.form_submit_button("Salvar no Arquivo do GitHub"):
                        path_parts = [st.session_state.pais.replace(" ", "_"), st.session_state.liga.replace(" ", "_"), st.session_state.temporada]
                        file_name = ""
                        tipo = st.session_state.tipo_dossie
                        
                        if tipo == "Dossiê de Liga": file_name = "Dossiê_Liga.md"
                        elif tipo == "Dossiê de Clube":
                            if not st.session_state.clube: st.error("O campo 'Clube' é obrigatório.")
                            else:
                                path_parts.append(st.session_state.clube.replace(" ", "_"))
                                file_name = "Dossiê_Clube.md"
                        elif tipo in ["Briefing Pré-Jogo", "Relatório Pós-Jogo"]:
                            if not st.session_state.clube or not st.session_state.rodada: st.error("Os campos 'Clube' e 'Rodada / Adversário' são obrigatórios.")
                            else:
                                path_parts.append(st.session_state.clube.replace(" ", "_"))
                                path_parts.append(st.session_state.rodada.replace(" ", "_"))
                                file_name = "Briefing_Pre-Jogo.md" if tipo == "Briefing Pré-Jogo" else "Relatorio_Pos-Jogo.md"
                        
                        if file_name:
                            full_path = "/".join(path_parts) + "/" + file_name
                            commit_message = f"Adiciona/Atualiza dossiê: {file_name}"
                            content = st.session_state.conteudo_md
                            
                            with st.spinner(f"A salvar '{full_path}' no GitHub..."):
                                try:
                                    existing_file = repo.get_contents(full_path)
                                    repo.update_file(full_path, commit_message, content, existing_file.sha)
                                    st.success(f"Dossiê '{full_path}' atualizado com sucesso!")
                                except UnknownObjectException:
                                    repo.create_file(full_path, commit_message, content)
                                    st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                                except Exception as e:
                                    st.error(f"Ocorreu um erro ao salvar: {e}")
                
                st.divider()
                st.subheader("Navegador do Repositório")
                display_repo_contents(repo)

            with col2:
                # Visualizador de dossiês
                st.subheader("Visualizador de Dossiês")
                if "viewing_file_content" in st.session_state:
                    st.markdown(f"#### {st.session_state.viewing_file_name}")
                    
                    # --- CORREÇÃO APLICADA AQUI ---
                    # 1. Limpa os artefactos de citação do conteúdo.
                    cleaned_content = re.sub(r':contentReference\[.*?\]\{.*?\}', '', st.session_state.viewing_file_content)
                    
                    # 2. Envolve o conteúdo limpo no nosso div de estilização.
                    html_content = f"<div class='dossier-viewer'>{cleaned_content}</div>"
                    st.markdown(html_content, unsafe_allow_html=True)
                else:
                    st.info("Selecione um ficheiro no navegador para o visualizar aqui.")
        else:
            st.warning("A conexão com o GitHub não foi estabelecida. Verifique as suas secrets.")

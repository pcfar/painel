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

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático Final", page_icon="🗂️", layout="wide")

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
    """Envia um pedido para a API da IA e retorna a resposta, com lógica de retentativas."""
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada.")
        return None
    
    model_name = "gemini-1.5-flash-latest"
    url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt}]
    if imagens_bytes:
        for imagem_bytes in imagens_bytes:
            encoded_image = base64.b64encode(imagem_bytes).decode('utf-8')
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})
            
    tools = [{"google_search": {}}]
    data = {"contents": [{"parts": parts}], "tools": tools}
    
    max_retries = 5
    base_delay = 2
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=400)
            if response.status_code == 429:
                delay = base_delay * (2 ** attempt)
                st.warning(f"Limite da API atingido. A tentar novamente em {delay} segundos...")
                time.sleep(delay)
                continue
            response.raise_for_status()
            result = response.json()
            if 'candidates' in result and result['candidates']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                st.error("A API respondeu, mas o formato do conteúdo é inesperado.")
                st.json(result)
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na chamada à API na tentativa {attempt + 1}: {e}")
            if attempt < max_retries - 1:
                delay = base_delay * (2 ** attempt)
                time.sleep(delay)
            else:
                st.error("Todas as tentativas de chamada à API falharam.")
                return None
    st.error("Falha ao comunicar com a API após múltiplas tentativas devido a limites de utilização.")
    return None

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
        st.info("Este diretório está vazio.")
    except Exception as e:
        st.error(f"Erro ao listar o conteúdo do repositório: {e}")

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")
    
    st.header("Central de Comando")
    # Adicionada uma nova aba para o "Arquivo"
    tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)", "Arquivo"])

    with tab1:
        st.info("Funcionalidade de geração do Dossiê de Liga.")
        # O código para gerar o Dossiê 1 seria colocado aqui.
    
    with tab2:
        st.info("Funcionalidade de geração do Dossiê de Clube.")
        # O código para gerar o Dossiê 2 seria colocado aqui.

    with tab3:
        st.info("Funcionalidade de geração do Dossiê Pós-Jogo.")
        # O código para gerar o Dossiê 3 seria colocado aqui.

    with tab4:
        st.info("Funcionalidade de geração do Dossiê Pré-Jogo.")
        # O código para gerar o Dossiê 4 seria colocado aqui.

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
                        # Lógica para construir o caminho do ficheiro com base nos metadados
                        path_parts = [
                            st.session_state.pais.replace(" ", "_"),
                            st.session_state.liga.replace(" ", "_"),
                            st.session_state.temporada
                        ]
                        
                        file_name = ""
                        tipo = st.session_state.tipo_dossie
                        
                        if tipo == "Dossiê de Liga":
                            file_name = "Dossiê_Liga.md"
                        elif tipo == "Dossiê de Clube":
                            if not st.session_state.clube:
                                st.error("O campo 'Clube' é obrigatório para este tipo de dossiê.")
                            else:
                                path_parts.append(st.session_state.clube.replace(" ", "_"))
                                file_name = "Dossiê_Clube.md"
                        elif tipo in ["Briefing Pré-Jogo", "Relatório Pós-Jogo"]:
                            if not st.session_state.clube or not st.session_state.rodada:
                                st.error("Os campos 'Clube' e 'Rodada / Adversário' são obrigatórios.")
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
                                    # Verifica se o ficheiro já existe para decidir entre criar ou atualizar
                                    repo.get_contents(full_path)
                                    repo.update_file(full_path, commit_message, content, repo.get_contents(full_path).sha)
                                    st.success(f"Dossiê '{full_path}' atualizado com sucesso!")
                                except UnknownObjectException:
                                    # Se não existir, cria o ficheiro
                                    repo.create_file(full_path, commit_message, content)
                                    st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                                except Exception as e:
                                    st.error(f"Ocorreu um erro ao salvar: {e}")
                
                st.divider()
                # Navegador do repositório
                st.subheader("Navegador do Repositório")
                display_repo_contents(repo)

            with col2:
                # Visualizador de dossiês
                st.subheader("Visualizador de Dossiês")
                if "viewing_file_content" in st.session_state:
                    st.markdown(f"#### {st.session_state.viewing_file_name}")
                    st.markdown(st.session_state.viewing_file_content, unsafe_allow_html=True)
                else:
                    st.info("Selecione um ficheiro no navegador para o visualizar aqui.")
        else:
            st.warning("A conexão com o GitHub não foi estabelecida. Verifique as suas secrets.")

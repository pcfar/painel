import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from datetime import datetime
from PIL import Image
import io
import requests
import json
import time
import base64
import pandas as pd
import altair as alt

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático Final", page_icon="📊", layout="wide")

# --- SISTEMA DE SENHA ÚNICA ---
def check_password():
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

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")
    
    st.header("Central de Comando")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        st.info("O Dossiê de Liga está funcional.")

    with tab2:
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Processamento por Etapas)")

        if 'club_dossier_step_staged' not in st.session_state:
            st.session_state.club_dossier_step_staged = 1

        # ETAPA 1: DEFINIR ALVO
        if st.session_state.club_dossier_step_staged == 1:
            with st.form("form_clube_etapa1_staged"):
                st.markdown("**ETAPA 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                if st.form_submit_button("Próximo Passo: Plantel Anterior"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo_staged = equipa_nome
                        st.session_state.club_dossier_step_staged = 2
                        st.rerun()
        
        # ETAPA 2: PROCESSAR PLANTEL ANTERIOR
        if st.session_state.club_dossier_step_staged == 2:
            st.markdown(f"### Etapa 2: Processamento do Plantel Anterior ({st.session_state.equipa_alvo_staged})")
            with st.form("form_clube_etapa2_staged"):
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior_staged")
                if st.form_submit_button("Extrair Plantel Anterior"):
                    if not st.session_state.prints_plantel_anterior_staged:
                        st.error("Por favor, carregue os prints do plantel anterior.")
                    else:
                        with st.spinner("Lendo os prints do plantel anterior..."):
                            imagens_bytes = [p.getvalue() for p in st.session_state.prints_plantel_anterior_staged]
                            prompt = "Leia estas imagens e retorne uma lista JSON com os nomes de todos os jogadores. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_anterior_staged = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_staged = 3
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao extrair a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar os prints.")

        # ETAPA 3: PROCESSAR PLANTEL ATUAL
        if st.session_state.club_dossier_step_staged == 3:
            st.success(f"Plantel anterior processado. Encontrados {len(st.session_state.lista_anterior_staged)} jogadores.")
            st.markdown(f"### Etapa 3: Processamento do Plantel da Nova Temporada ({st.session_state.equipa_alvo_staged})")
            with st.form("form_clube_etapa3_staged"):
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual_staged")
                if st.form_submit_button("Extrair Plantel da Nova Temporada"):
                    if not st.session_state.prints_plantel_atual_staged:
                        st.error("Por favor, carregue os prints do plantel da nova temporada.")
                    else:
                        with st.spinner("Lendo os prints do novo plantel..."):
                            imagens_bytes = [p.getvalue() for p in st.session_state.prints_plantel_atual_staged]
                            prompt = "Leia estas imagens e retorne uma lista JSON com os nomes de todos os jogadores. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_atual_staged = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_staged = 4
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao extrair a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar os prints.")

        # ETAPA 4: ANÁLISE COMPARATIVA
        if st.session_state.club_dossier_step_staged == 4:
            # ... (código da etapa 4 sem alterações) ...
            pass

        # ETAPAS FINAIS (Aprofundamento, Dados Coletivos, Geração Final)
        if st.session_state.club_dossier_step_staged >= 5:
            # ... (código da etapa 5 sem alterações) ...
            pass

            # ETAPA 6 COM GUIA INTEGRADO
            if st.session_state.club_dossier_step_staged == 6:
                with st.form("form_clube_etapa6_staged"):
                    st.markdown("**ETAPA SEGUINTE: DADOS DE DESEMPENHO COLETIVO**")
                    st.info("Siga o guia abaixo para encontrar e capturar os 3 prints necessários no FBref.com.")
                    
                    with st.expander("▼ Guia para Print A: Visão Geral e Performance Ofensiva"):
                        st.markdown("""
                        - **Onde Encontrar:** `FBref.com` → Página da Equipa → Temporada Anterior → Tabela **"Squad & Player Stats"**.
                        - **Ação:** Role a página para baixo até encontrar a tabela principal.
                        - **Conteúdo do Print:** Recorte a tabela para incluir as colunas desde **"Player"** (Jogador) até **"Expected"** (xG, npxG, xAG).
                        """)

                    with st.expander("▼ Guia para Print B: Padrões de Construção de Jogo"):
                        st.markdown("""
                        - **Onde Encontrar:** Na mesma página do Print A, acima da tabela principal, clique no link **"Passing"** (Passes).
                        - **Ação:** Aceda à tabela "Squad & Player Passing".
                        - **Conteúdo do Print:** Recorte a tabela para focar nas colunas de **"Prog"** (Passes Progressivos).
                        """)

                    with st.expander("▼ Guia para Print C: Análise Comparativa Casa vs. Fora"):
                        st.markdown("""
                        - **Onde Encontrar:** A partir da página da equipa, encontre um link para a competição (ex: "Premier League"). Na página da competição, procure pelo menu **"Home & Away"** (Casa & Fora).
                        - **Ação:** Aceda à tabela que divide o desempenho em "Home" e "Away".
                        - **Conteúdo do Print:** Recorte a tabela que compara o desempenho da equipa em casa e fora.
                        """)
                    
                    st.file_uploader("Carregar Prints da Equipa (A, B e C)*", accept_multiple_files=True, key="prints_equipa_staged")
                    
                    if st.form_submit_button("Gerar Dossiê Final Completo"):
                        if not st.session_state.prints_equipa_staged or len(st.session_state.prints_equipa_staged) < 3:
                            st.error("Por favor, carregue os 3 prints da equipa.")
                        else:
                            st.session_state.club_dossier_step_staged = 7
                            st.rerun()

            # ... (código das etapas 7 e 8 sem alterações) ...
            pass

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

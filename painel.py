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
    
    model_name = "gemini-1.5-flash-latest" # Usar o Flash para maior rapidez
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
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Linha de Montagem)")

        if 'club_dossier_step_pipe' not in st.session_state:
            st.session_state.club_dossier_step_pipe = 1

        # ETAPA 1: DEFINIR ALVO
        if st.session_state.club_dossier_step_pipe == 1:
            with st.form("form_clube_etapa1_pipe"):
                st.markdown("**FASE 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                if st.form_submit_button("Próximo Passo: Plantel Anterior"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo_pipe = equipa_nome
                        st.session_state.club_dossier_step_pipe = 2
                        st.rerun()
        
        # ETAPA 2: PROCESSAR PLANTEL ANTERIOR (SEQUENCIALMENTE)
        if st.session_state.club_dossier_step_pipe == 2:
            st.markdown(f"### Fase 2: Processamento do Plantel Anterior ({st.session_state.equipa_alvo_pipe})")
            with st.form("form_clube_etapa2_pipe"):
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior_pipe")
                if st.form_submit_button("1. Extrair Plantel Anterior"):
                    if not st.session_state.prints_plantel_anterior_pipe:
                        st.error("Por favor, carregue os prints do plantel anterior.")
                    else:
                        st.session_state.lista_anterior_pipe = []
                        status_text = st.empty()
                        progress_bar = st.progress(0)
                        total_prints = len(st.session_state.prints_plantel_anterior_pipe)

                        for i, print_file in enumerate(st.session_state.prints_plantel_anterior_pipe):
                            status_text.text(f"A ler o print {i+1} de {total_prints} do plantel anterior...")
                            imagens_bytes = [print_file.getvalue()]
                            prompt = "Leia esta imagem de um plantel e retorne uma lista JSON com os nomes de todos os jogadores visíveis. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_anterior_pipe.extend(dados.get("jogadores", []))
                                except (json.JSONDecodeError, IndexError):
                                    st.error(f"Falha ao extrair a lista de jogadores do print {i+1}. A tentar continuar...")
                            else:
                                st.error(f"A IA não conseguiu processar o print {i+1}. A tentar continuar...")
                            progress_bar.progress((i + 1) / total_prints)
                        
                        st.session_state.club_dossier_step_pipe = 3
                        st.rerun()

        # ETAPA 3: PROCESSAR PLANTEL ATUAL (SEQUENCIALMENTE)
        if st.session_state.club_dossier_step_pipe == 3:
            st.success(f"**Verificação:** Plantel anterior processado. Encontrados {len(st.session_state.lista_anterior_pipe)} jogadores.")
            st.markdown(f"### Fase 3: Processamento do Plantel da Nova Temporada ({st.session_state.equipa_alvo_pipe})")
            with st.form("form_clube_etapa3_pipe"):
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual_pipe")
                if st.form_submit_button("2. Extrair Plantel da Nova Temporada"):
                    if not st.session_state.prints_plantel_atual_pipe:
                        st.error("Por favor, carregue os prints do plantel da nova temporada.")
                    else:
                        st.session_state.lista_atual_pipe = []
                        status_text = st.empty()
                        progress_bar = st.progress(0)
                        total_prints = len(st.session_state.prints_plantel_atual_pipe)

                        for i, print_file in enumerate(st.session_state.prints_plantel_atual_pipe):
                            status_text.text(f"A ler o print {i+1} de {total_prints} do novo plantel...")
                            imagens_bytes = [print_file.getvalue()]
                            prompt = "Leia esta imagem de um plantel e retorne uma lista JSON com os nomes de todos os jogadores visíveis. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_atual_pipe.extend(dados.get("jogadores", []))
                                except (json.JSONDecodeError, IndexError):
                                    st.error(f"Falha ao extrair a lista de jogadores do print {i+1}. A tentar continuar...")
                            else:
                                st.error(f"A IA não conseguiu processar o print {i+1}. A tentar continuar...")
                            progress_bar.progress((i + 1) / total_prints)
                        
                        st.session_state.club_dossier_step_pipe = 4
                        st.rerun()

        # ETAPA 4: ANÁLISE COMPARATIVA
        if st.session_state.club_dossier_step_pipe == 4:
            st.success(f"**Verificação:** Novo plantel processado. Encontrados {len(st.session_state.lista_atual_pipe)} jogadores.")
            st.markdown("### Fase 4: Análise de Transferências")
            if st.button("3. Comparar Planteis e Gerar Análise de Impacto"):
                with st.spinner("Comparando planteis e gerando a análise de impacto..."):
                    # Remove duplicados
                    lista_anterior_unica = sorted(list(set(st.session_state.lista_anterior_pipe)))
                    lista_atual_unica = sorted(list(set(st.session_state.lista_atual_pipe)))

                    prompt_comparativo = f"""
**TAREFA:** Com base nestas duas listas de jogadores, identifique as chegadas e saídas e escreva a "Parte 1: Evolução do Plantel".
**Plantel Anterior:** {json.dumps(lista_anterior_unica)}
**Plantel Atual:** {json.dumps(lista_atual_unica)}
**ALGORITMO:** Compare as duas listas para identificar as diferenças. Escreva a secção "1. EVOLUÇÃO DO PLANTEL" em Markdown, incluindo a sua análise de impacto. **IMPORTANTE:** Após o Markdown, adicione um separador `---JSON_CHEGADAS---` e depois um bloco de código JSON com a lista de nomes das chegadas. Ex: {{"chegadas": ["Jogador A", "Jogador B"]}}
"""
                    resposta = gerar_resposta_ia(prompt_comparativo)
                    if resposta and "---JSON_CHEGADAS---" in resposta:
                        parts = resposta.split("---JSON_CHEGADAS---")
                        st.session_state.analise_transferencias_md_pipe = parts[0]
                        try:
                            dados = json.loads(parts[1].strip())
                            st.session_state.lista_chegadas_pipe = dados.get("chegadas", [])
                        except json.JSONDecodeError:
                            st.session_state.lista_chegadas_pipe = []
                    else:
                        st.session_state.analise_transferencias_md_pipe = "Falha ao gerar a análise comparativa."
                        st.session_state.lista_chegadas_pipe = []
                    st.session_state.club_dossier_step_pipe = 5
                    st.rerun()

        # ETAPAS FINAIS (Aprofundamento, Dados Coletivos, Geração Final)
        if st.session_state.club_dossier_step_pipe >= 5:
            # O restante do fluxo (etapas 5, 6, 7, 8) permanece o mesmo, pois já é sequencial e robusto.
            # O código completo seria inserido aqui.
            st.markdown(st.session_state.get("analise_transferencias_md_pipe", "Análise de transferências pendente."))
            st.info("As próximas etapas para aprofundamento individual e análise coletiva seguir-se-ão.")


    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

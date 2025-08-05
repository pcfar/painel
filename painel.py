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
import pytesseract # Importa a biblioteca de OCR

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
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Híbrido por Etapas)")

        if 'club_dossier_step_hybrid' not in st.session_state:
            st.session_state.club_dossier_step_hybrid = 1

        # ETAPA 1: DEFINIR ALVO
        if st.session_state.club_dossier_step_hybrid == 1:
            with st.form("form_clube_etapa1_hybrid"):
                st.markdown("**FASE 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                if st.form_submit_button("Próximo Passo: Plantel Anterior"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo_hybrid = equipa_nome
                        st.session_state.club_dossier_step_hybrid = 2
                        st.rerun()
        
        # ETAPA 2: PROCESSAR PLANTEL ANTERIOR
        if st.session_state.club_dossier_step_hybrid == 2:
            st.markdown(f"### Fase 2: Processamento do Plantel Anterior ({st.session_state.equipa_alvo_hybrid})")
            with st.form("form_clube_etapa2_hybrid"):
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior_hybrid")
                if st.form_submit_button("1. Extrair Plantel Anterior"):
                    if not st.session_state.prints_plantel_anterior_hybrid:
                        st.error("Por favor, carregue os prints do plantel anterior.")
                    else:
                        with st.spinner("A extrair texto dos prints com OCR..."):
                            texto_bruto = ""
                            for p in st.session_state.prints_plantel_anterior_hybrid:
                                texto_bruto += pytesseract.image_to_string(Image.open(p), lang='por+eng') + "\n"
                        
                        with st.spinner("A enviar texto para a IA para limpeza e estruturação..."):
                            prompt = f"Analise este texto bruto extraído de imagens de um plantel e retorne uma lista JSON com os nomes de todos os jogadores. Limpe qualquer ruído. Texto: \n{texto_bruto}\n\n Exemplo de saída: {{\"jogadores\": [\"Nome A\", \"Nome B\"]}}"
                            resposta = gerar_resposta_ia(prompt)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_anterior_hybrid = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_hybrid = 3
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao estruturar a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar o texto extraído.")

        # ETAPA 3: PROCESSAR PLANTEL ATUAL
        if st.session_state.club_dossier_step_hybrid == 3:
            st.success(f"**Verificação:** Plantel anterior processado. Encontrados {len(st.session_state.lista_anterior_hybrid)} jogadores.")
            st.markdown(f"### Fase 3: Processamento do Plantel da Nova Temporada ({st.session_state.equipa_alvo_hybrid})")
            with st.form("form_clube_etapa3_hybrid"):
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual_hybrid")
                if st.form_submit_button("2. Extrair Plantel da Nova Temporada"):
                    if not st.session_state.prints_plantel_atual_hybrid:
                        st.error("Por favor, carregue os prints do plantel da nova temporada.")
                    else:
                        with st.spinner("A extrair texto dos prints com OCR..."):
                            texto_bruto = ""
                            for p in st.session_state.prints_plantel_atual_hybrid:
                                texto_bruto += pytesseract.image_to_string(Image.open(p), lang='por+eng') + "\n"
                        
                        with st.spinner("A enviar texto para a IA para limpeza e estruturação..."):
                            prompt = f"Analise este texto bruto extraído de imagens de um plantel e retorne uma lista JSON com os nomes de todos os jogadores. Limpe qualquer ruído. Texto: \n{texto_bruto}\n\n Exemplo de saída: {{\"jogadores\": [\"Nome A\", \"Nome B\"]}}"
                            resposta = gerar_resposta_ia(prompt)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_atual_hybrid = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_hybrid = 4
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao estruturar a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar o texto extraído.")

        # ETAPA 4: ANÁLISE COMPARATIVA
        if st.session_state.club_dossier_step_hybrid == 4:
            st.success(f"**Verificação:** Novo plantel processado. Encontrados {len(st.session_state.lista_atual_hybrid)} jogadores.")
            st.markdown("### Fase 4: Análise de Transferências")
            if st.button("3. Comparar Planteis e Gerar Análise de Impacto"):
                with st.spinner("A IA está a comparar os planteis e a gerar a análise de impacto..."):
                    lista_anterior = sorted(list(set(st.session_state.lista_anterior_hybrid)))
                    lista_atual = sorted(list(set(st.session_state.lista_atual_hybrid)))
                    prompt_comparativo = f"""
**TAREFA:** Com base nestas duas listas de jogadores, identifique as chegadas e saídas e escreva a "Parte 1: Evolução do Plantel".
**Plantel Anterior:** {json.dumps(lista_anterior)}
**Plantel Atual:** {json.dumps(lista_atual)}
**ALGORITMO:** Compare as duas listas para identificar as diferenças. Escreva a secção "1. EVOLUÇÃO DO PLANTEL" em Markdown, incluindo a sua análise de impacto. **IMPORTANTE:** Após o Markdown, adicione um separador `---JSON_CHEGADAS---` e depois um bloco de código JSON com a lista de nomes das chegadas. Ex: {{"chegadas": ["Jogador A", "Jogador B"]}}
"""
                    resposta = gerar_resposta_ia(prompt_comparativo)
                    if resposta and "---JSON_CHEGADAS---" in resposta:
                        parts = resposta.split("---JSON_CHEGADAS---")
                        st.session_state.analise_transferencias_md_hybrid = parts[0]
                        try:
                            dados = json.loads(parts[1].strip())
                            st.session_state.lista_chegadas_hybrid = dados.get("chegadas", [])
                        except json.JSONDecodeError:
                            st.session_state.lista_chegadas_hybrid = []
                    else:
                        st.session_state.analise_transferencias_md_hybrid = "Falha ao gerar a análise comparativa."
                        st.session_state.lista_chegadas_hybrid = []
                    st.session_state.club_dossier_step_hybrid = 5
                    st.rerun()

        # ETAPAS FINAIS
        if st.session_state.club_dossier_step_hybrid >= 5:
            st.markdown(st.session_state.analise_transferencias_md_hybrid)
            st.divider()

            if st.session_state.club_dossier_step_hybrid == 5:
                # ... (código da etapa de aprofundamento individual) ...
                pass

            if st.session_state.club_dossier_step_hybrid == 6:
                # ... (código da etapa de dados coletivos) ...
                pass
            
            if st.session_state.club_dossier_step_hybrid == 7:
                # ... (código da geração final) ...
                pass

            if st.session_state.club_dossier_step_hybrid == 8:
                # ... (código da exibição final) ...
                pass

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

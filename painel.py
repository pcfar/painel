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

# --- FUNÇÕES DE CHAMADA À IA (ESPECIALIZADAS) ---
def gerar_texto_com_ia(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada.")
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=180)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        st.error(f"Erro na chamada à API de texto: {e}")
    return None

def gerar_dossie_com_ia_multimodal(prompt_texto, lista_imagens_bytes):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada.")
        return None
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    parts = [{"text": prompt_texto}]
    for imagem_bytes in lista_imagens_bytes:
        encoded_image = base64.b64encode(imagem_bytes).decode('utf-8')
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})
    data = {"contents": [{"parts": parts}]}
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        st.error(f"Erro na chamada à API multimodal: {e}")
    return None

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")

    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception as e:
            st.error(f"Erro ao conectar com o GitHub: {e}")
            st.stop()
    repo = get_github_connection()

    st.header("Central de Comando")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        st.subheader("Criar Dossiê 1: Análise Geral da Liga")

        # FASE 1: GERAÇÃO DO PANORAMA DA LIGA
        if 'dossie_p1_resultado' not in st.session_state:
            with st.form("form_dossie_1_p1"):
                st.markdown("**Parte 1: Panorama da Liga (Pesquisa Autónoma da IA)**")
                liga = st.text_input("Liga (nome completo)*", placeholder="Ex: Premier League")
                pais = st.text_input("País*", placeholder="Ex: Inglaterra")
                if st.form_submit_button("Gerar Panorama da Liga"):
                    if not all([liga, pais]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("AGENTE DE INTELIGÊNCIA a pesquisar (Etapa 1/2)..."):
                            # --- ETAPA 1: GERAÇÃO BRUTA ---
                            prompt_etapa1 = f"Aja como um jornalista desportivo. Escreva um texto informativo sobre a liga de futebol '{liga}' do país '{pais}'. Fale sobre o perfil da liga, dominância recente, rivalidades, lendas e curiosidades."
                            texto_bruto = gerar_texto_com_ia(prompt_etapa1)

                        if texto_bruto and "liga" in texto_bruto.lower():
                            with st.spinner("AGENTE DE INTELIGÊNCIA a formatar o relatório (Etapa 2/2)..."):
                                # --- ETAPA 2: REFINAMENTO E FORMATAÇÃO ---
                                prompt_etapa2 = f"""
**TAREFA:** Pegue no texto abaixo e reestruture-o EXATAMENTE no formato Markdown especificado. Não adicione nenhuma informação nova. Apenas formate o texto fornecido.

**TEXTO A FORMATAR:**
---
{texto_bruto}
---

**MODELO DE SAÍDA OBRIGATÓRIO (USE ESTE FORMATO):**
---
### **DOSSIÊ ESTRATÉGICO DE LIGA: {liga.upper()}**
#### **PARTE 1: VISÃO GERAL E HISTÓRICA**
* **Perfil da Liga:** [Extraia a parte relevante do texto sobre o perfil da liga aqui.]
* **Dominância na Década:** [Extraia a parte relevante do texto sobre a dominância aqui.]
* **Principais Rivalidades:** [Extraia a parte relevante do texto sobre as rivalidades aqui.]
* **Lendas da Liga:** [Extraia a parte relevante do texto sobre as lendas aqui.]
* **Curiosidades e Recordes:** [Extraia a parte relevante do texto sobre as curiosidades aqui.]
---
"""
                                resultado_final_p1 = gerar_texto_com_ia(prompt_etapa2)

                                if resultado_final_p1 and "dossiê estratégico" in resultado_final_p1.lower():
                                    st.session_state['dossie_p1_resultado'] = resultado_final_p1
                                    st.session_state['contexto_liga'] = {'liga': liga, 'pais': pais}
                                    st.rerun()
                                else:
                                    st.error("A etapa de formatação do relatório falhou. Tente novamente.")
                        else:
                            st.error("A geração da Parte 1 falhou. A IA retornou uma resposta inesperada. Tente novamente.")
                            st.text_area("Resposta recebida da IA (para depuração):", texto_bruto or "Nenhuma resposta.", height=150)

        # FASE 2: UPLOAD DAS IMAGENS E GERAÇÃO FINAL
        if 'dossie_p1_resultado' in st.session_state and 'dossie_final_completo' not in st.session_state:
            st.markdown("---"); st.success("Parte 1 (Panorama da Liga) gerada com sucesso!"); st.markdown(st.session_state['dossie_p1_resultado']); st.markdown("---")
            st.subheader("Parte 2: Análise Técnica via Upload de Imagens")
            with st.form("form_dossie_1_p2"):
                st.write("Faça o upload das imagens das tabelas de classificação. A IA irá analisá-las diretamente.")
                prints_classificacao = st.file_uploader("Prints das Classificações*", accept_multiple_files=True, key="prints_gerais")
                if st.form_submit_button("Analisar Imagens e Gerar Dossiê Final"):
                    if not prints_classificacao:
                        st.error("Por favor, faça o upload de pelo menos uma imagem.")
                    else:
                        with st.spinner("AGENTE DE INTELIGÊNCIA a 'ler' imagens e a finalizar o dossiê..."):
                            lista_imagens_bytes = [p.getvalue() for p in prints_classificacao]
                            contexto = st.session_state['contexto_liga']
                            prompt_final = f"""**ALGORITMO DE EXECUÇÃO OBRIGATÓRIO:**... [Resto do prompt final "blindado", que já está robusto]"""
                            dossie_final = gerar_dossie_com_ia_multimodal(prompt_final, lista_imagens_bytes)
                            if dossie_final and "dossiê estratégico" in dossie_final.lower() and "placar de dominância" in dossie_final.lower():
                                st.session_state['dossie_final_completo'] = dossie_final
                                st.rerun()
                            else:
                                st.error("A geração do dossiê final falhou ou retornou um formato inesperado. Tente novamente.")
                                st.text_area("Resposta recebida (para depuração):", dossie_final or "Nenhuma resposta", height=200)

        # EXIBIÇÃO DO DOSSIÊ FINAL
        if 'dossie_final_completo' in st.session_state:
            st.markdown("---"); st.header("Dossiê Final Consolidado"); st.success("Dossiê gerado com sucesso!")
            st.markdown(st.session_state['dossie_final_completo'])
            if st.button("Limpar e Iniciar Nova Análise"):
                password_state = st.session_state.get("password_correct", False)
                st.session_state.clear()
                st.session_state["password_correct"] = password_state
                st.rerun()

    with tab2: st.info("Em desenvolvimento.")
    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

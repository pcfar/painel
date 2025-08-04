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
import altair as alt # Importa a biblioteca para gráficos

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
                        with st.spinner("AGENTE DE INTELIGÊNCIA a pesquisar e redigir o panorama da liga..."):
                            prompt_p1 = f"""**PERSONA:** Você é um Jornalista Investigativo... [Resto do prompt da Parte 1]"""
                            resultado_p1 = gerar_texto_com_ia(prompt_p1)
                            if resultado_p1 and "parte 1" in resultado_p1.lower() and "visão geral" in resultado_p1.lower():
                                st.session_state['dossie_p1_resultado'] = resultado_p1
                                st.session_state['contexto_liga'] = {'liga': liga, 'pais': pais}
                                st.rerun()
                            else:
                                st.error("A geração da Parte 1 falhou. Tente novamente.")
                                st.text_area("Resposta recebida da IA:", resultado_p1 or "Nenhuma resposta.", height=150)

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
                            # --- PROMPT ATUALIZADO PARA SOLICITAR JSON ---
                            prompt_final = f"""
**PERSONA:** Você é um Analista de Dados Quantitativo... [Resto do prompt multimodal]...

**MODELO DE SAÍDA OBRIGATÓRIO:**
[Copie e cole aqui o modelo de saída completo do dossiê em Markdown, como antes]
---
**INSTRUÇÃO FINAL E CRÍTICA:** Após o final do dossiê em markdown, adicione um separador `---JSON_DATA_START---` seguido por um bloco de código JSON. Este JSON deve ser uma lista de objetos, onde cada objeto representa uma equipa e contém as chaves "Equipa" e "Pontuação Total" do seu 'Placar de Dominância'.
**Exemplo do JSON:**
```json
[
  {{"Equipa": "Manchester City", "Pontuação Total": 25}},
  {{"Equipa": "Liverpool", "Pontuação Total": 18}}
]
```
"""
                            dossie_final_raw = gerar_dossie_com_ia_multimodal(prompt_final, lista_imagens_bytes)
                            if dossie_final_raw:
                                # --- LÓGICA PARA PROCESSAR MARKDOWN E JSON ---
                                if "---JSON_DATA_START---" in dossie_final_raw:
                                    parts = dossie_final_raw.split("---JSON_DATA_START---")
                                    st.session_state['dossie_final_completo'] = parts[0]
                                    
                                    # Limpa e extrai o JSON
                                    json_str = parts[1].strip().replace("```json", "").replace("```", "")
                                    try:
                                        data = json.loads(json_str)
                                        df = pd.DataFrame(data)
                                        # Renomeia colunas para o gráfico
                                        df.rename(columns={"Pontuação Total": "Pontuacao"}, inplace=True)
                                        st.session_state['dominancia_df'] = df
                                    except json.JSONDecodeError as e:
                                        st.error(f"Erro ao processar os dados do gráfico: {e}")
                                        st.session_state['dominancia_df'] = None
                                else:
                                    st.session_state['dossie_final_completo'] = dossie_final_raw
                                    st.session_state['dominancia_df'] = None
                                st.rerun()
                            else:
                                st.error("A geração do dossiê final falhou.")

        # --- EXIBIÇÃO DO DOSSIÊ FINAL E GRÁFICO ---
        if 'dossie_final_completo' in st.session_state:
            st.markdown("---"); st.header("Dossiê Final Consolidado"); st.success("Dossiê gerado com sucesso!")
            
            # Extrai e exibe o markdown e o gráfico em colunas
            dossie_markdown = st.session_state['dossie_final_completo']
            dominancia_df = st.session_state.get('dominancia_df')

            col1, col2 = st.columns([2, 1]) # Dossiê ocupa 2/3, Gráfico 1/3

            with col1:
                st.markdown(dossie_markdown)

            with col2:
                if dominancia_df is not None and not dominancia_df.empty:
                    st.subheader("Visualização da Dominância")
                    
                    # Cria o gráfico de barras com Altair
                    chart = alt.Chart(dominancia_df).mark_bar().encode(
                        x=alt.X('Pontuacao:Q', title='Pontuação Total'),
                        y=alt.Y('Equipa:N', sort='-x', title='Equipa'),
                        tooltip=['Equipa', 'Pontuacao']
                    ).properties(
                        title='Placar de Dominância na Liga'
                    ).interactive()

                    st.altair_chart(chart, use_container_width=True)
                else:
                    st.info("Não foi possível gerar a visualização de dados.")

            if st.button("Limpar e Iniciar Nova Análise"):
                password_state = st.session_state.get("password_correct", False)
                st.session_state.clear()
                st.session_state["password_correct"] = password_state
                st.rerun()

    with tab2: st.info("Em desenvolvimento.")
    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

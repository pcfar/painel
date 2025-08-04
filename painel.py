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

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático Final", page_icon="🧠", layout="wide")

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

# Função Otimizada APENAS para gerar texto
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
        # Validação robusta da resposta
        if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error("Resposta da IA recebida, mas em formato inesperado.")
            st.json(result)
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na chamada à API: {e}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Erro ao processar a resposta da IA: {e}")
        return None

# Função Otimizada para gerar texto A PARTIR DE TEXTO + IMAGENS
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
        if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error("Resposta da IA (multimodal) em formato inesperado.")
            st.json(result)
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na chamada à API (multimodal): {e}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Erro ao processar a resposta da IA (multimodal): {e}")
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

        # --- FASE 1: GERAÇÃO DO PANORAMA DA LIGA ---
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
                            prompt_p1 = f"""
**PERSONA:** Você é um Jornalista Investigativo e Historiador de Futebol... [O mesmo prompt da Parte 1, que já está a funcionar bem]
**CONTEXTO:** Liga para Análise: {liga}, País: {pais}
**MISSÃO:** Realize uma pesquisa aprofundada na web para criar a "PARTE 1" de um Dossiê Estratégico sobre a {liga}.
... [Resto do prompt da Parte 1] ...
"""
                            # Usar a função dedicada a texto
                            resultado_p1 = gerar_texto_com_ia(prompt_p1)
                            # Validação para garantir que a IA não deu uma resposta vazia/genérica
                            if resultado_p1 and "###" in resultado_p1:
                                st.session_state['dossie_p1_resultado'] = resultado_p1
                                st.session_state['contexto_liga'] = {'liga': liga, 'pais': pais}
                                st.rerun()
                            else:
                                st.error("A geração da Parte 1 falhou ou retornou uma resposta inválida. Por favor, tente novamente.")
                                st.text_area("Resposta recebida da IA:", resultado_p1 or "Nenhuma resposta.", height=150)

        # --- FASE 2: UPLOAD DAS IMAGENS E GERAÇÃO FINAL ---
        if 'dossie_p1_resultado' in st.session_state and 'dossie_final_completo' not in st.session_state:
            st.markdown("---")
            st.success("Parte 1 (Panorama da Liga) gerada com sucesso!")
            st.markdown(st.session_state['dossie_p1_resultado'])
            st.markdown("---")
            st.subheader("Parte 2: Análise Técnica via Upload de Imagens")
            with st.form("form_dossie_1_p2"):
                st.write("Faça o upload das imagens das tabelas de classificação. A IA irá analisá-las diretamente.")
                prints_classificacao = st.file_uploader(
                    "Prints das Classificações das Últimas Temporadas*",
                    help="Capture as tabelas de classificação completas. A IA irá 'ler' as imagens.",
                    accept_multiple_files=True,
                    key="prints_gerais"
                )
                if st.form_submit_button("Analisar Imagens e Gerar Dossiê Final"):
                    if not prints_classificacao:
                        st.error("Por favor, faça o upload de pelo menos uma imagem.")
                    else:
                        with st.spinner("AGENTE DE INTELIGÊNCIA a 'ler' as imagens e a finalizar o dossiê..."):
                            lista_imagens_bytes = [p.getvalue() for p in prints_classificacao]
                            contexto = st.session_state['contexto_liga']
                            prompt_final = f"""
**PERSONA:** Você é um Analista de Dados Quantitativo...
**CONTEXTO:** Você recebeu duas fontes de informação sobre a liga '{contexto['liga']}':
1.  **Análise Qualitativa (Parte 1):** Um resumo textual.
2.  **Dados Visuais (Imagens):** Uma série de imagens de tabelas de classificação.
**MISSÃO FINAL:** Analise CADA imagem, extraia os dados, e consolide tudo num único dossiê.
... [Resto do prompt final multimodal, que já está a funcionar bem] ...
**DADOS DISPONÍVEIS PARA A SUA ANÁLISE:**
**1. Análise Qualitativa (Parte 1 - Texto):**
{st.session_state['dossie_p1_resultado']}
**2. Dados Visuais (Parte 2 - Imagens):**
[As imagens que lhe enviei a seguir a este texto são os seus dados visuais. Analise-as agora.]
... [Resto do modelo de saída] ...
"""
                            # Usar a função dedicada a multimodal
                            dossie_final = gerar_dossie_com_ia_multimodal(prompt_final, lista_imagens_bytes)
                            if dossie_final:
                                st.session_state['dossie_final_completo'] = dossie_final
                                st.rerun()
                            else:
                                st.error("A geração do dossiê final falhou. Verifique os logs de erro.")

        # --- EXIBIÇÃO DO DOSSIÊ FINAL ---
        if 'dossie_final_completo' in st.session_state:
            st.markdown("---")
            st.header("Dossiê Final Consolidado")
            st.success("Dossiê gerado com sucesso!")
            st.markdown(st.session_state['dossie_final_completo'])
            if st.button("Limpar e Iniciar Nova Análise"):
                password_state = st.session_state.get("password_correct", False)
                st.session_state.clear()
                st.session_state["password_correct"] = password_state
                st.rerun()

    with tab2: st.info("Em desenvolvimento.")
    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

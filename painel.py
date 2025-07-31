import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from datetime import datetime
import pytesseract
from PIL import Image
import io
import requests
import json
import time

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

# --- FUNÇÃO DE CHAMADA À IA (GEMINI) ---
def gerar_dossie_com_ia(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada nos segredos (Secrets).")
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    max_retries = 3
    for attempt in range(max_retries):
        try:
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=120)
            response.raise_for_status()
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na chamada à API (tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                st.error(f"Resposta da API: {response.text if 'response' in locals() else 'Sem resposta'}")
                return None
        except (KeyError, IndexError) as e:
            st.error(f"Erro ao processar a resposta da IA: {e}")
            st.error(f"Resposta completa da API: {result if 'result' in locals() else 'Sem resultado'}")
            return None
# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")

    # --- Conexão com o GitHub ---
    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception:
            st.error("Erro ao conectar com o GitHub.")
            st.stop()
    repo = get_github_connection()

    # --- CENTRAL DE COMANDO ---
    st.header("Central de Comando")
    
    tipo_dossie = st.selectbox("Qual dossiê deseja criar?", ["Selecionar...", "Dossiê 1: Análise Geral da Liga"])
    
    if tipo_dossie == "Dossiê 1: Análise Geral da Liga":
        with st.form("form_dossie_1_final"):
            st.subheader("Criar Dossiê 1: Análise Geral da Liga (Híbrido)")
            
            temporada = st.text_input("Temporada*", placeholder="Ex: 2024-2025")
            liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
            pais = st.text_input("País*", placeholder="Ex: Holanda")
            st.markdown("---")

            print_classificacao = st.file_uploader("1) Print da Tabela de Classificação Final*", accept_multiple_files=True)
            print_stats = st.file_uploader("2) Print das Estatísticas Avançadas*", accept_multiple_files=True)
            
            if st.form_submit_button("Gerar Dossiê com IA"):
                if not all([temporada, liga, pais, print_classificacao, print_stats]):
                    st.error("Por favor, preencha todos os campos obrigatórios (*).")
                else:
                    # 1. OCR
                    with st.spinner("AGENTE DE COLETA a processar 'prints'..."):
                        try:
                            grupos_de_prints = {
                                "TABELA DE CLASSIFICAÇÃO FINAL": print_classificacao,
                                "ESTATÍSTICAS AVANÇADAS": print_stats
                            }
                            texto_final_para_prompt = ""
                            for nome_grupo, prints in grupos_de_prints.items():
                                if prints:
                                    texto_final_para_prompt += f"\n--- [INÍCIO DOS DADOS DO UTILIZADOR: {nome_grupo}] ---\n"
                                    for print_file in prints:
                                        imagem = Image.open(print_file)
                                        texto_final_para_prompt += pytesseract.image_to_string(imagem, lang='por+eng') + "\n"
                                    texto_final_para_prompt += f"--- [FIM DOS DADOS DO UTILIZADOR: {nome_grupo}] ---\n"
                        except Exception as e:
                            st.error(f"Erro durante o OCR: {e}")
                            st.stop()
                    
                    # 2. Construção do Prompt
                    data_hoje = datetime.now().strftime("%d/%m/%Y")
                    prompt_mestre = f"""
**PERSONA:** Você é um Analista de Futebol Sênior...
**CONTEXTO:** Liga: {liga.upper()}, País: {pais}, Temporada: {temporada}
**TAREFAS:**
* **TAREFA 1 (Pesquisa Autónoma):** Busque na web os campeões da {liga.upper()} na última década e curiosidades sobre a liga.
* **TAREFA 2 (Análise de Dados Fornecidos):** Use os dados brutos abaixo para analisar a última temporada.
{texto_final_para_prompt}
* **TAREFA 3 (Consolidação):** Junte tudo no modelo de saída.
**MODELO DE SAÍDA:**
---
### **DOSSIÊ ESTRATÉGICO DE LIGA: {liga.upper()}**
**TEMPORADA:** {temporada} | **DATA:** {data_hoje}
---
#### **PARTE 1: VISÃO GERAL E HISTÓRICA**
* **Dominância na Década:** [Sua pesquisa aqui]
* **Fatos Relevantes:** [Sua pesquisa aqui]
#### **PARTE 2: ANÁLISE TÉCNICA**
* **Panorama da Temporada:** [Sua análise dos dados fornecidos aqui]
* **Equipes Dominantes:** [Sua análise dos dados fornecidos aqui]
#### **VEREDITO FINAL: PLAYLIST DE MONITORAMENTO**
* **1. [Equipe 1]**
* **2. [Equipe 2]**
* **3. [Equipe 3]**
---
"""
                    # 3. Chamada à IA e Exibição
                    with st.spinner("AGENTE DE INTELIGÊNCIA a contactar o núcleo de IA... Este processo pode demorar."):
                        dossie_final = gerar_dossie_com_ia(prompt_mestre)
                        if dossie_final:
                            st.markdown("---")
                            st.header("Dossiê Final Gerado pela IA")
                            st.markdown(dossie_final)
                            
                            # 4. Salvar no GitHub
                            try:
                                temporada_fmt = temporada.replace('/', '-')
                                caminho_final = f"{temporada_fmt}/{liga.upper()}/GERAL/Dossie_1_Completo.md"
                                commit_message = f"Gera Dossiê 1 para {liga.upper()} {temporada_fmt}"
                                
                                try:
                                    arquivo_existente = repo.get_contents(caminho_final)
                                    repo.update_file(caminho_final, commit_message, dossie_final, arquivo_existente.sha)
                                    st.info(f"Dossiê atualizado em `{caminho_final}` no GitHub.")
                                except UnknownObjectException:
                                    repo.create_file(caminho_final, commit_message, dossie_final)
                                    st.success(f"Dossiê salvo em `{caminho_final}` no GitHub!")
                            except Exception as e:
                                st.warning(f"Não foi possível salvar o dossiê no GitHub: {e}")

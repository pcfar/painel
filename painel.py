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
def gerar_resposta_ia(prompt, imagens_bytes=None):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada.")
        return None
    
    # O modelo Gemini 1.5 Pro é mais indicado para tarefas complexas como esta
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt}]
    if imagens_bytes:
        for imagem_bytes in imagens_bytes:
            encoded_image = base64.b64encode(imagem_bytes).decode('utf-8')
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})
            
    # Habilita a ferramenta de busca na web para a IA poder aceder aos links
    tools = [{"google_search": {"type": "retrieval"}}]
    
    data = {"contents": [{"parts": parts}], "tools": tools}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=400) # Timeout aumentado
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
        st.error(f"Resposta recebida do servidor: {response.text if 'response' in locals() else 'N/A'}")
    return None

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")

    @st.cache_resource
    def get_github_connection():
        # ... (código do GitHub sem alterações)
        pass
    
    st.header("Central de Comando")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    # --- ABA 1: DOSSIÊ DE LIGA ---
    with tab1:
        st.info("O Dossiê de Liga está funcional. Use esta aba para analisar uma liga inteira.")
        # O código completo da Aba 1, que já está estável, seria mantido aqui.
        # Por uma questão de clareza, foi omitido desta visualização.

    # --- ABA 2: DOSSIÊ DE CLUBE (MODELO ORIENTADO PELO ANALISTA) ---
    with tab2:
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube v3.0")

        if 'dossie_clube_final_v3' not in st.session_state:
            with st.form("form_clube_v3"):
                st.markdown("**FASE 1: INPUTS DO ANALISTA**")
                st.info("Forneça as fontes de dados primárias para a IA processar. A precisão da análise depende da qualidade dos seus inputs.")

                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                
                st.markdown("<h6>Links dos Planteis (Transfermarkt ou similar)</h6>", unsafe_allow_html=True)
                link_plantel_anterior = st.text_input("Link do Plantel (Temporada Anterior)*", placeholder="Ex: https://www.transfermarkt.pt/manchester-city/kader/verein/281/saison_id/2023")
                link_plantel_atual = st.text_input("Link do Plantel (Temporada Atual)*", placeholder="Ex: https://www.transfermarkt.pt/manchester-city/kader/verein/281/saison_id/2024")

                st.markdown("<h6>Prints de Desempenho (FBref, Sofascore, etc.)</h6>", unsafe_allow_html=True)
                prints_desempenho = st.file_uploader("Carregue os prints com as estatísticas detalhadas da temporada anterior*", 
                                                     accept_multiple_files=True, 
                                                     key="prints_clube")

                if st.form_submit_button("Gerar Análise do Clube"):
                    if not all([equipa_nome, link_plantel_anterior, link_plantel_atual, prints_desempenho]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner(f"AGENTE DE INTELIGÊNCIA a processar os dados sobre o {equipa_nome}... Este processo é complexo e pode demorar alguns minutos."):
                            lista_imagens_bytes = [p.getvalue() for p in prints_desempenho]
                            
                            prompt_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite. A sua única função é processar os dados fornecidos e redigir um dossiê tático profundo sobre o clube '{equipa_nome}'. NÃO use nenhum conhecimento prévio que tenha. Baseie-se APENAS nas fontes fornecidas.

**ALGORITMO DE EXECUÇÃO OBRIGATÓRIO:**

**1. COMPARAÇÃO DE PLANTEIS (Fontes: Links)**
   - ACEDA ao link da temporada anterior: {link_plantel_anterior}
   - ACEDA ao link da temporada atual: {link_plantel_atual}
   - COMPARE as duas listas de jogadores e identifique TODAS as saídas e TODAS as chegadas. Ignore jogadores que regressam de empréstimo, a menos que sejam relevantes.
   - ESTRUTURE esta informação para a secção "Balanço de Transferências".

**2. EXTRAÇÃO DE DADOS DE DESEMPENHO (Fontes: Imagens)**
   - ANALISE CADA imagem fornecida.
   - EXTRAIA as principais métricas estatísticas da temporada anterior (xG, posse de bola, finalizações, desempenho em casa vs. fora, etc.).
   - ESTRUTURE estes dados para a secção "Raio-X Estatístico" e use-os para escrever a análise dos "Padrões de Jogo".

**3. REDAÇÃO DO DOSSIÊ**
   - Com todos os dados extraídos e estruturados, REDIJA o dossiê final seguindo o **MODELO OBRIGATÓRIO** abaixo.
   - A sua análise deve CONECTAR os pontos. Por exemplo, como as transferências (ponto 1) podem impactar os padrões de desempenho (ponto 2) e o modelo de jogo projetado.

---
**MODELO OBRIGATÓRIO (Use este formato exato):**

### **DOSSIÊ ESTRATÉGICO DE CLUBE: {equipa_nome.upper()}**

**1. EVOLUÇÃO DO PLANTEL (ANÁLISE COMPARATIVA)**
* **Balanço de Transferências (Factos):**
    * **Lista Completa de Chegadas:** [Liste aqui as chegadas identificadas no passo 1]
    * **Lista Completa de Saídas:** [Liste aqui as saídas identificadas no passo 1]
* **Análise de Impacto (Ganhos e Perdas):**
    * [Escreva a sua análise qualitativa sobre o que a equipa ganha com os reforços]
    * [Escreva a sua análise qualitativa sobre o que a equipa perde com as saídas]

**2. DNA DO DESEMPENHO (TEMPORADA ANTERIOR)**
* **Raio-X Estatístico:** [Crie uma tabela com as principais métricas extraídas dos prints]
* **Padrões de Jogo Identificados:** [Analise os dados da tabela. A equipa é dominante? Tem dificuldade em criar? etc.]
* **Análise Comparativa Casa vs. Fora:** [Analise os padrões de desempenho em casa e fora, com base nos dados dos prints]

**3. O PLANO DE JOGO (ANÁLISE TÁTICA)**
* **Modelo de Jogo Principal:** [Descreva a formação e o estilo de jogo mais utilizados na temporada anterior]
* **Protagonistas e Destaques:** [Identifique os jogadores mais influentes estatisticamente]
* **Projeção Tática para a Nova Temporada:** [Conecte as transferências com o modelo de jogo e projete possíveis mudanças táticas]

**4. VEREDITO FINAL E CENÁRIOS DE OBSERVAÇÃO**
* **Síntese Analítica:** [O resumo inteligente que conecta todos os pontos do dossiê]
* **Cenários de Monitoramento:** [Crie 3 cenários práticos e detalhados para observar nos primeiros jogos da nova temporada]
"""
                            dossie_final = gerar_resposta_ia(prompt_final, lista_imagens_bytes)
                            if dossie_final and "dossiê estratégico de clube" in dossie_final.lower():
                                st.session_state['dossie_clube_final_v3'] = dossie_final
                                st.rerun()
                            else:
                                st.error("A geração do dossiê falhou. A IA pode ter tido dificuldade em aceder aos links ou processar as imagens. Verifique os links e tente novamente.")
                                st.text_area("Resposta recebida (para depuração):", dossie_final or "Nenhuma resposta", height=200)

        # --- Exibição do Dossiê de Clube Final ---
        if 'dossie_clube_final_v3' in st.session_state:
            st.markdown("---")
            st.header("Dossiê de Clube Gerado")
            st.success("Análise concluída com sucesso!")
            st.markdown(st.session_state['dossie_clube_final_v3'])

            if st.button("Limpar e Analisar Outro Clube"):
                if 'dossie_clube_final_v3' in st.session_state:
                    del st.session_state['dossie_clube_final_v3']
                st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

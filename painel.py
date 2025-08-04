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
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Pedido Único Consolidado)")

        if 'dossie_clube_final_consolidado' not in st.session_state:
            with st.form("form_clube_consolidado"):
                st.markdown("**Forneça todos os dados para a análise completa**")
                
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                
                st.divider()
                
                st.markdown("**1. Prints dos Planteis**")
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior_consolidado")
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual_consolidado")
                
                st.divider()

                # --- GUIA DE NAVEGAÇÃO INTEGRADO ---
                st.markdown("**2. Prints de Desempenho da Equipa (Temporada Anterior)**")
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
                
                st.file_uploader("Carregar Prints da Equipa (A, B e C)*", 
                                 accept_multiple_files=True, 
                                 key="prints_equipa_consolidado")

                if st.form_submit_button("Gerar Dossiê Completo"):
                    # Validação
                    if not all([equipa_nome, 
                                st.session_state.prints_plantel_anterior_consolidado,
                                st.session_state.prints_plantel_atual_consolidado,
                                st.session_state.prints_equipa_consolidado]) or len(st.session_state.prints_equipa_consolidado) < 3:
                        st.error("Por favor, preencha todos os campos e carregue todos os prints necessários.")
                    else:
                        with st.spinner(f"AGENTE DE INTELIGÊNCIA a processar todos os dados sobre o {equipa_nome}... Este pedido único é complexo e pode demorar vários minutos."):
                            
                            todas_imagens_bytes = []
                            prompt_imagens_info = []

                            for p in st.session_state.prints_plantel_anterior_consolidado:
                                todas_imagens_bytes.append(p.getvalue())
                            prompt_imagens_info.append(f"- O primeiro conjunto de imagens corresponde ao plantel da TEMPORADA ANTERIOR.")
                            
                            for p in st.session_state.prints_plantel_atual_consolidado:
                                todas_imagens_bytes.append(p.getvalue())
                            prompt_imagens_info.append(f"- O segundo conjunto de imagens corresponde ao plantel da NOVA TEMPORADA.")

                            for p in st.session_state.prints_equipa_consolidado:
                                todas_imagens_bytes.append(p.getvalue())
                            prompt_imagens_info.append(f"- O terceiro conjunto de imagens corresponde aos prints de desempenho da equipa (A, B, C).")

                            prompt_imagens_info_str = "\n".join(prompt_imagens_info)

                            prompt_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite. A sua única função é processar TODOS os dados fornecidos num único passo e redigir um dossiê tático profundo sobre o clube '{equipa_nome}'.

**INFORMAÇÃO DISPONÍVEL:**
{prompt_imagens_info_str}

**ALGORITMO DE EXECUÇÃO OBRIGATÓRIO (execute todos os passos):**

1.  **ANÁLISE DE PLANTEIS:**
    - Leia os nomes dos jogadores dos prints da temporada anterior e da nova temporada.
    - Compare as duas listas para identificar TODAS as chegadas e saídas.
    - Escreva a secção "1. EVOLUÇÃO DO PLANTEL", incluindo a sua análise de impacto.

2.  **ANÁLISE DE DESEMPENHO:**
    - Analise os prints de desempenho da equipa (A, B, C).
    - Extraia as métricas e escreva a secção "2. DNA DO DESEMPENHO".

3.  **ANÁLISE TÁTICA E VEREDITO:**
    - Com base em TUDO o que analisou, escreva as secções "3. O PLANO DE JOGO" e "4. VEREDITO FINAL". A sua análise deve conectar todos os pontos (como as transferências impactam o desempenho e a tática).

---
**MODELO OBRIGATÓRIO (Use este formato exato):**

### **DOSSIÊ ESTRATÉGICO DE CLUBE: {equipa_nome.upper()}**

**1. EVOLUÇÃO DO PLANTEL (ANÁLISE COMPARATIVA)**
* **Balanço de Transferências (Factos):**
    * **Lista Completa de Chegadas:** [Resultado do passo 1]
    * **Lista Completa de Saídas:** [Resultado do passo 1]
* **Análise de Impacto (Ganhos e Perdas):** [A sua análise do passo 1]

**2. DNA DO DESEMPENHO (TEMPORADA ANTERIOR)**
* **Raio-X Estatístico:** [Crie uma tabela com as principais métricas extraídas dos prints no passo 2]
* **Padrões de Jogo Identificados:** [Sua análise do passo 2]
* **Análise Comparativa Casa vs. Fora:** [Sua análise do passo 2]

**3. O PLANO DE JOGO (ANÁLISE TÁTICA)**
* **Modelo de Jogo Principal:** [Sua análise do passo 3]
* **Protagonistas e Destaques:** [Sua análise do passo 3]
* **Projeção Tática para a Nova Temporada:** [Sua análise do passo 3]

**4. VEREDITO FINAL E CENÁRIOS DE OBSERVAÇÃO**
* **Síntese Analítica:** [Sua análise do passo 3]
* **Cenários de Monitoramento:** [Sua análise do passo 3]
"""
                            dossie_final = gerar_resposta_ia(prompt_final, todas_imagens_bytes)
                            if dossie_final and "dossiê estratégico de clube" in dossie_final.lower():
                                st.session_state.dossie_clube_final_consolidado = dossie_final
                            else:
                                st.session_state.dossie_clube_final_consolidado = "A geração do dossiê falhou. A IA pode ter tido dificuldade em processar o grande volume de dados. Tente novamente com prints mais claros ou menos ficheiros."
                            st.rerun()

        # --- Exibição do Dossiê de Clube Final ---
        if 'dossie_clube_final_consolidado' in st.session_state:
            st.markdown("---")
            st.header("Dossiê de Clube Gerado")
            
            if "falhou" in st.session_state.dossie_clube_final_consolidado:
                st.error(st.session_state.dossie_clube_final_consolidado)
            else:
                st.success("Análise concluída com sucesso!")
                st.markdown(st.session_state.dossie_clube_final_consolidado)

            if st.button("Limpar e Analisar Outro Clube"):
                if 'dossie_clube_final_consolidado' in st.session_state:
                    del st.session_state['dossie_clube_final_consolidado']
                st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

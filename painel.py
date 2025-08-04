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
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-pro-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt}]
    if imagens_bytes:
        for imagem_bytes in imagens_bytes:
            encoded_image = base64.b64encode(imagem_bytes).decode('utf-8')
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})
            
    tools = [{"google_search": {}}] # Habilita a busca na web
    
    data = {"contents": [{"parts": parts}], "tools": tools}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=400)
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

    # --- ABA 2: DOSSIÊ DE CLUBE (FLUXO DE TRABALHO INTELIGENTE) ---
    with tab2:
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube v5.0")

        # Inicializa o estado do fluxo de trabalho
        if 'club_dossier_step_v5' not in st.session_state:
            st.session_state.club_dossier_step_v5 = 1

        # ETAPA 1: DEFINIR O ALVO
        if st.session_state.club_dossier_step_v5 == 1:
            with st.form("form_clube_etapa1_v5"):
                st.markdown("**ETAPA 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                
                if st.form_submit_button("Próximo Passo: Coleta de Dados"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo_v5 = equipa_nome
                        st.session_state.club_dossier_step_v5 = 2
                        st.rerun()

        # ETAPA 2: CHECKLIST DE COLETA DE DADOS UNIFICADA
        if st.session_state.club_dossier_step_v5 == 2:
            st.markdown(f"### Checklist de Coleta para: **{st.session_state.equipa_alvo_v5}**")
            st.info("Forneça os links e carregue os prints necessários para a análise.")

            with st.form("form_clube_etapa2_v5"):
                
                with st.expander("▼ 1. Fontes de Dados sobre o Plantel (Obrigatório)"):
                    st.text_input("Link do Plantel (Temporada Anterior)*", 
                                 placeholder="Ex: https://www.transfermarkt.pt/.../saison_id/2023",
                                 key="link_anterior_v5")
                    st.text_input("Link do Plantel (Temporada Atual)*", 
                                 placeholder="Ex: https://www.transfermarkt.pt/.../saison_id/2024",
                                 key="link_atual_v5")

                with st.expander("▼ 2. Prints de Desempenho (Obrigatório)"):
                    st.markdown("""
                    **Instruções:** Capture e carregue os 3 prints descritos abaixo.
                    - **Print A: Visão Geral e Performance Ofensiva**
                        - *Onde Encontrar:* `FBref.com` → Página da Equipa → Temporada Anterior → Tabela "Estatísticas do Elenco".
                        - *Conteúdo:* Incluir colunas desde "Jogador" até **"Gols Esperados (xG, npxG, xAG)"**.
                    - **Print B: Padrões de Construção de Jogo**
                        - *Onde Encontrar:* `FBref.com` → Página da Equipa → Temporada Anterior → Clique no link **"Passes"**.
                        - *Conteúdo:* Focar nas colunas de **"Passes Progressivos"**.
                    - **Print C: Análise Comparativa Casa vs. Fora**
                        - *Onde Encontrar:* `FBref.com` → Página da Competição → Temporada Anterior → Menu "Relatórios de mandante e visitante".
                        - *Conteúdo:* Tabela que compara o desempenho da equipa em casa e fora.
                    """)
                    st.file_uploader("Carregar Prints (A, B e C)*", 
                                     accept_multiple_files=True, 
                                     key="prints_clube_v5", 
                                     type=['png', 'jpg', 'jpeg'])
                
                st.divider()

                if st.form_submit_button("Gerar Análise Completa"):
                    # Validação dos inputs
                    if not all([st.session_state.link_anterior_v5, st.session_state.link_atual_v5]) or not st.session_state.prints_clube_v5:
                        st.error("Por favor, forneça todos os links e carregue os prints obrigatórios.")
                    elif len(st.session_state.prints_clube_v5) < 3:
                        st.error("Por favor, carregue os 3 prints descritos nas instruções.")
                    else:
                        st.session_state.club_dossier_step_v5 = 3
                        st.rerun()

        # ETAPA 3: GERAÇÃO E VISUALIZAÇÃO
        if st.session_state.club_dossier_step_v5 == 3:
            with st.spinner(f"AGENTE DE INTELIGÊNCIA a processar os dados sobre o {st.session_state.equipa_alvo_v5}... Este processo é complexo e pode demorar alguns minutos."):
                
                lista_imagens_bytes = [p.getvalue() for p in st.session_state.prints_clube_v5]
                
                # O novo prompt inteligente
                prompt_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite. A sua única função é processar os dados fornecidos e redigir um dossiê tático profundo sobre o clube '{st.session_state.equipa_alvo_v5}'. NÃO use nenhum conhecimento prévio. Baseie-se APENAS nas fontes fornecidas.

**ALGORITMO DE EXECUÇÃO OBRIGATÓRIO:**

**0. ASSOCIAÇÃO DE DADOS (PRIMEIRA TAREFA):**
   - Eu forneci 3 imagens e 3 descrições de prints (A, B, C). A sua primeira tarefa é analisar o conteúdo visual de cada imagem e associá-la à sua descrição correta.
   - **Descrição Print A:** Visão Geral e Performance Ofensiva (Contém xG, xAG, etc.).
   - **Descrição Print B:** Padrões de Construção de Jogo (Contém Passes Progressivos).
   - **Descrição Print C:** Análise Comparativa Casa vs. Fora.
   - Use esta associação para guiar a sua extração de dados no passo 2.

**1. COMPARAÇÃO DE PLANTEIS (Fontes: Links)**
   - ACEDA ao link da temporada anterior: {st.session_state.link_anterior_v5}
   - ACEDA ao link da temporada atual: {st.session_state.link_atual_v5}
   - COMPARE as duas listas de jogadores e identifique TODAS as saídas e TODAS as chegadas.
   - ESTRUTURE esta informação para a secção "Balanço de Transferências".

**2. EXTRAÇÃO DE DADOS DE DESEMPENHO (Fontes: Imagens)**
   - Com base na associação que fez no passo 0, ANALISE CADA imagem.
   - EXTRAIA as principais métricas estatísticas da temporada anterior.
   - ESTRUTURE estes dados para a secção "Raio-X Estatístico" e use-os para escrever a análise dos "Padrões de Jogo".

**3. REDAÇÃO DO DOSSIÊ**
   - Com todos os dados extraídos e estruturados, REDIJA o dossiê final seguindo o **MODELO OBRIGATÓRIO** abaixo.
   - A sua análise deve CONECTAR os pontos (ex: como as transferências impactam os padrões de desempenho).

---
**MODELO OBRIGATÓRIO (Use este formato exato):**

### **DOSSIÊ ESTRATÉGICO DE CLUBE: {st.session_state.equipa_alvo_v5.upper()}**

**1. EVOLUÇÃO DO PLANTEL (ANÁLISE COMPARATIVA)**
* **Balanço de Transferências (Factos):**
    * **Lista Completa de Chegadas:** [Liste aqui as chegadas identificadas no passo 1]
    * **Lista Completa de Saídas:** [Liste aqui as saídas identificadas no passo 1]
* **Análise de Impacto (Ganhos e Perdas):**
    * [Escreva a sua análise qualitativa sobre o que a equipa ganha com os reforços]
    * [Escreva a sua análise qualitativa sobre o que a equipa perde com as saídas]

**2. DNA DO DESEMPENHO (TEMPORADA ANTERIOR)**
* **Raio-X Estatístico:** [Crie uma tabela com as principais métricas extraídas dos prints]
* **Padrões de Jogo Identificados:** [Analise os dados da tabela]
* **Análise Comparativa Casa vs. Fora:** [Analise os padrões de desempenho em casa e fora]

**3. O PLANO DE JOGO (ANÁLISE TÁTICA)**
* **Modelo de Jogo Principal:** [Descreva a formação e o estilo de jogo mais utilizados]
* **Protagonistas e Destaques:** [Identifique os jogadores mais influentes estatisticamente]
* **Projeção Tática para a Nova Temporada:** [Conecte as transferências com o modelo de jogo e projete possíveis mudanças]

**4. VEREDITO FINAL E CENÁRIOS DE OBSERVAÇÃO**
* **Síntese Analítica:** [O resumo inteligente que conecta todos os pontos]
* **Cenários de Monitoramento:** [Crie 3 cenários práticos e detalhados para observar nos jogos]
"""
                dossie_final = gerar_resposta_ia(prompt_final, lista_imagens_bytes)
                if dossie_final and "dossiê estratégico de clube" in dossie_final.lower():
                    st.session_state.dossie_clube_final_v5 = dossie_final
                else:
                    st.session_state.dossie_clube_final_v5 = "A geração do dossiê falhou. A IA pode ter tido dificuldade em aceder aos links ou processar as imagens. Verifique os links e tente novamente."
                
                st.session_state.club_dossier_step_v5 = 4
                st.rerun()

        # ETAPA 4: MOSTRAR RESULTADO
        if st.session_state.club_dossier_step_v5 == 4:
            st.markdown("---")
            st.header(f"Dossiê de Clube Gerado: {st.session_state.equipa_alvo_v5}")
            
            if "falhou" in st.session_state.dossie_clube_final_v5:
                st.error(st.session_state.dossie_clube_final_v5)
            else:
                st.success("Análise concluída com sucesso!")
                st.markdown(st.session_state.dossie_clube_final_v5)

            if st.button("Limpar e Analisar Outro Clube"):
                keys_to_delete = ['club_dossier_step_v5', 'equipa_alvo_v5', 'link_anterior_v5', 
                                  'link_atual_v5', 'prints_clube_v5', 'dossie_clube_final_v5']
                for key in keys_to_delete:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

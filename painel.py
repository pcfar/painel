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
import re

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
            
    tools = [{"google_search": {}}]
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
    
    st.header("Central de Comando")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        st.info("O Dossiê de Liga está funcional.")

    with tab2:
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube v6.0")

        if 'club_dossier_step_v6' not in st.session_state:
            st.session_state.club_dossier_step_v6 = 1

        # ETAPA 1: DEFINIR ALVO E PLANTEIS
        if st.session_state.club_dossier_step_v6 == 1:
            with st.form("form_clube_etapa1_v6"):
                st.markdown("**ETAPA 1: DEFINIR O ALVO E OS PLANTEIS**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                link_plantel_anterior = st.text_input("Link do Plantel (Temporada Anterior)*", placeholder="Ex: https://www.transfermarkt.pt/.../2023")
                link_plantel_atual = st.text_input("Link do Plantel (Temporada Atual)*", placeholder="Ex: https://www.transfermarkt.pt/.../2024")
                
                if st.form_submit_button("Analisar Transferências"):
                    if not all([equipa_nome, link_plantel_anterior, link_plantel_atual]):
                        st.error("Por favor, preencha todos os campos obrigatórios.")
                    else:
                        st.session_state.equipa_alvo_v6 = equipa_nome
                        st.session_state.link_anterior_v6 = link_plantel_anterior
                        st.session_state.link_atual_v6 = link_plantel_atual
                        st.session_state.club_dossier_step_v6 = 2
                        st.rerun()

        # ETAPA 2: ANÁLISE DE TRANSFERÊNCIAS E APROFUNDAMENTO INDIVIDUAL
        if st.session_state.club_dossier_step_v6 == 2:
            with st.spinner(f"AGENTE DE INTELIGÊNCIA a comparar os planteis..."):
                prompt_transferencias = f"""
**TAREFA:** Aceda aos dois links de planteis do Transfermarkt e compare-os.
- Link Anterior: {st.session_state.link_anterior_v6}
- Link Atual: {st.session_state.link_atual_v6}

**ALGORITMO:**
1.  Identifique TODAS as chegadas e TODAS as saídas.
2.  Escreva a secção "1. EVOLUÇÃO DO PLANTEL" em Markdown, incluindo a sua análise de impacto.
3.  **IMPORTANTE:** Após o Markdown, adicione um separador `---JSON_CHEGADAS---` e depois um bloco de código JSON com uma lista dos nomes dos jogadores que chegaram. Ex: {{"chegadas": ["Jogador A", "Jogador B"]}}
"""
                analise_transferencias_raw = gerar_resposta_ia(prompt_transferencias)
                
                if analise_transferencias_raw and "---JSON_CHEGADAS---" in analise_transferencias_raw:
                    parts = analise_transferencias_raw.split("---JSON_CHEGADAS---")
                    st.session_state.analise_transferencias_md = parts[0]
                    
                    json_str = parts[1].strip()
                    try:
                        chegadas_data = json.loads(json_str)
                        st.session_state.lista_chegadas = chegadas_data.get("chegadas", [])
                    except json.JSONDecodeError:
                        st.session_state.lista_chegadas = []
                else:
                    st.session_state.analise_transferencias_md = "Falha ao analisar as transferências. Verifique os links."
                    st.session_state.lista_chegadas = []

                st.session_state.club_dossier_step_v6 = 3
                st.rerun()

        if st.session_state.club_dossier_step_v6 == 3:
            st.markdown("### Parte 1: Evolução do Plantel")
            st.markdown(st.session_state.analise_transferencias_md)
            st.divider()

            with st.form("form_clube_etapa2_v6"):
                st.markdown("**ETAPA 2: APROFUNDAMENTO INDIVIDUAL (OPCIONAL)**")
                st.info("Para quais das novas contratações você gostaria de fornecer dados para um 'Mini Dossiê'?")
                
                jogadores_selecionados = st.multiselect("Selecione os reforços a analisar:", 
                                                       options=st.session_state.get('lista_chegadas', []))
                
                st.session_state.prints_jogadores = {}
                for jogador in jogadores_selecionados:
                    st.file_uploader(f"Carregar print de estatísticas para **{jogador}** (época anterior)", 
                                     key=f"print_{jogador}", 
                                     type=['png', 'jpg', 'jpeg'])

                if st.form_submit_button("Próximo Passo: Dados Coletivos"):
                    # Guarda os prints carregados
                    for jogador in jogadores_selecionados:
                        if st.session_state[f"print_{jogador}"]:
                            st.session_state.prints_jogadores[jogador] = st.session_state[f"print_{jogador}"].getvalue()
                    
                    st.session_state.club_dossier_step_v6 = 4
                    st.rerun()

        # ETAPA 3: COLETA DE DADOS COLETIVOS
        if st.session_state.club_dossier_step_v6 == 4:
            st.markdown("### ETAPA 3: DADOS DE DESEMPENHO COLETIVO")
            with st.form("form_clube_etapa3_v6"):
                st.markdown("""
                **Instruções:** Carregue os 3 prints sobre o desempenho da equipa na época passada.
                - **Print A:** Visão Geral e Performance Ofensiva (FBref)
                - **Print B:** Padrões de Construção de Jogo (FBref)
                - **Print C:** Análise Comparativa Casa vs. Fora (FBref)
                """)
                st.file_uploader("Carregar Prints da Equipa (A, B e C)*", 
                                 accept_multiple_files=True, 
                                 key="prints_equipa_v6")
                
                if st.form_submit_button("Gerar Dossiê Final Completo"):
                    if not st.session_state.prints_equipa_v6 or len(st.session_state.prints_equipa_v6) < 3:
                        st.error("Por favor, carregue os 3 prints da equipa.")
                    else:
                        st.session_state.club_dossier_step_v6 = 5
                        st.rerun()

        # ETAPA 4: GERAÇÃO FINAL
        if st.session_state.club_dossier_step_v6 == 5:
            with st.spinner(f"AGENTE DE INTELIGÊNCIA a consolidar todos os dados e a redigir o dossiê final..."):
                
                # Prepara todas as imagens para a API
                todas_imagens_bytes = []
                prompt_imagens_info = []

                # Adiciona prints dos jogadores individuais
                for jogador, img_bytes in st.session_state.get('prints_jogadores', {}).items():
                    todas_imagens_bytes.append(img_bytes)
                    prompt_imagens_info.append(f"- A imagem para o 'Mini Dossiê' de **{jogador}** está incluída.")

                # Adiciona prints da equipa
                for i, print_file in enumerate(st.session_state.prints_equipa_v6):
                    todas_imagens_bytes.append(print_file.getvalue())
                    # Associa a imagem pela ordem de upload
                    letra_print = chr(ord('A') + i)
                    prompt_imagens_info.append(f"- A imagem do Print da Equipa **{letra_print}** está incluída.")

                prompt_imagens_info_str = "\n".join(prompt_imagens_info)

                prompt_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite. Com base em TODA a informação fornecida, redija um dossiê profundo e coeso sobre o '{st.session_state.equipa_alvo_v6}'.

**INFORMAÇÃO DISPONÍVEL:**
1.  **Análise de Transferências Inicial:**
    {st.session_state.analise_transferencias_md}
2.  **Dados Visuais (Prints):**
    {prompt_imagens_info_str}

**ALGORITMO DE EXECUÇÃO:**
1.  **Mini Dossiês:** Para cada jogador com um print fornecido, analise as suas estatísticas da época passada e escreva o "Mini Dossiê de Contratação".
2.  **Análise Coletiva:** Analise os prints da equipa (A, B, C) para escrever a secção "DNA DO DESEMPENHO".
3.  **Consolidação:** Junte tudo no **MODELO OBRIGATÓRIO** abaixo, garantindo que a sua análise conecta todos os pontos de forma inteligente (ex: como os "Mini Dossiês" dos reforços impactam a "Projeção Tática").

---
**MODELO OBRIGATÓRIO:**

### **DOSSIÊ ESTRATÉGICO DE CLUBE: {st.session_state.equipa_alvo_v6.upper()}**

{st.session_state.analise_transferencias_md}

* **Mini Dossiês de Contratação:**
    [Para cada jogador com print, escreva aqui a análise individual]

**2. DNA DO DESEMPENHO (TEMPORADA ANTERIOR)**
* **Raio-X Estatístico:** [Tabela com métricas extraídas dos prints da equipa]
* **Padrões de Jogo Identificados:** [Análise dos dados da tabela]
* **Análise Comparativa Casa vs. Fora:** [Análise dos dados de casa/fora]

**3. O PLANO DE JOGO (ANÁLISE TÁTICA)**
* **Modelo de Jogo Principal:** [Descrição da tática]
* **Protagonistas e Destaques:** [Jogadores influentes da época passada]
* **Projeção Tática para a Nova Temporada:** [Projeção tática considerando as transferências e os perfis dos novos jogadores]

**4. VEREDITO FINAL E CENÁRIOS DE OBSERVAÇÃO**
* **Síntese Analítica:** [O resumo inteligente]
* **Cenários de Monitoramento:** [3 cenários práticos]
"""
                dossie_final = gerar_resposta_ia(prompt_final, todas_imagens_bytes)
                st.session_state.dossie_clube_final_v6 = dossie_final or "Falha na geração final."
                st.session_state.club_dossier_step_v6 = 6
                st.rerun()

        if st.session_state.club_dossier_step_v6 == 6:
            st.header(f"Dossiê Final: {st.session_state.equipa_alvo_v6}")
            st.markdown(st.session_state.dossie_clube_final_v6)
            if st.button("Limpar e Analisar Outro Clube"):
                keys_to_delete = [k for k in st.session_state if k.endswith('_v6')]
                for key in keys_to_delete:
                    del st.session_state[key]
                st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

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

    # --- ABA 2: DOSSIÊ DE CLUBE (FLUXO DE TRABALHO GUIADO) ---
    with tab2:
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube v4.0")

        # Inicializa o estado do fluxo de trabalho
        if 'club_dossier_step' not in st.session_state:
            st.session_state.club_dossier_step = 1

        # ETAPA 1: DEFINIR O ALVO
        if st.session_state.club_dossier_step == 1:
            with st.form("form_clube_etapa1"):
                st.markdown("**ETAPA 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                
                if st.form_submit_button("Próximo Passo: Coleta de Dados"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo = equipa_nome
                        st.session_state.club_dossier_step = 2
                        st.rerun()

        # ETAPA 2: CHECKLIST DE COLETA DE DADOS
        if st.session_state.club_dossier_step == 2:
            st.markdown(f"### Checklist de Coleta para: **{st.session_state.equipa_alvo}**")
            st.info("Siga as instruções abaixo para fornecer os dados necessários para a análise.")

            with st.form("form_clube_etapa2"):
                # --- Fontes do Plantel ---
                st.markdown("**1. Fontes de Dados sobre o Plantel (Obrigatório)**")
                link_plantel_anterior = st.text_input("Link do Plantel (Temporada Anterior)*", 
                                                      placeholder="Ex: https://www.transfermarkt.pt/.../saison_id/2023",
                                                      key="link_anterior")
                link_plantel_atual = st.text_input("Link do Plantel (Temporada Atual)*", 
                                                   placeholder="Ex: https://www.transfermarkt.pt/.../saison_id/2024",
                                                   key="link_atual")
                st.divider()

                # --- Prints de Desempenho ---
                st.markdown("**2. Prints de Desempenho (Obrigatório)**")

                with st.expander("▼ Print A: Visão Geral e Performance Ofensiva"):
                    st.markdown("""
                    - **Onde Encontrar:** `FBref.com` → Página da Equipa → Temporada Anterior → Tabela "Estatísticas do Elenco".
                    - **Conteúdo do Print:** Recorte a tabela para incluir as colunas desde "Jogador" até **"Gols Esperados (xG, npxG, xAG)"**.
                    """)
                    st.file_uploader("Carregar Print A", key="print_a", type=['png', 'jpg', 'jpeg'])

                with st.expander("▼ Print B: Padrões de Construção de Jogo"):
                    st.markdown("""
                    - **Onde Encontrar:** `FBref.com` → Página da Equipa → Temporada Anterior → Clique no link **"Passes"**.
                    - **Conteúdo do Print:** Recorte a tabela para focar nas colunas de **"Passes Progressivos"**.
                    """)
                    st.file_uploader("Carregar Print B", key="print_b", type=['png', 'jpg', 'jpeg'])

                with st.expander("▼ Print C: Análise Comparativa Casa vs. Fora"):
                    st.markdown("""
                    - **Onde Encontrar:** `FBref.com` → Página da Competição → Temporada Anterior → Menu "Relatórios de mandante e visitante".
                    - **Conteúdo do Print:** Recorte a tabela que compara o desempenho da equipa em casa e fora.
                    """)
                    st.file_uploader("Carregar Print C", key="print_c", type=['png', 'jpg', 'jpeg'])
                
                st.divider()

                if st.form_submit_button("Gerar Análise Completa"):
                    # Validação dos inputs
                    if not all([st.session_state.link_anterior, st.session_state.link_atual, 
                                st.session_state.print_a, st.session_state.print_b, st.session_state.print_c]):
                        st.error("Por favor, forneça todos os links e prints obrigatórios.")
                    else:
                        st.session_state.club_dossier_step = 3
                        st.rerun()

        # ETAPA 3: GERAÇÃO E VISUALIZAÇÃO
        if st.session_state.club_dossier_step == 3:
            with st.spinner(f"AGENTE DE INTELIGÊNCIA a processar os dados sobre o {st.session_state.equipa_alvo}... Este processo é complexo e pode demorar alguns minutos."):
                
                # Coleta dos dados dos widgets
                link_anterior = st.session_state.link_anterior
                link_atual = st.session_state.link_atual
                
                # Prepara as imagens para a API
                imagens_bytes = []
                prints_info = [] # Para passar os nomes dos prints no prompt
                for key in ['print_a', 'print_b', 'print_c']:
                    if st.session_state[key]:
                        img_bytes = st.session_state[key].getvalue()
                        imagens_bytes.append(img_bytes)
                        prints_info.append(f"A imagem '{st.session_state[key].name}' corresponde ao Print {key.upper()}.")
                
                prints_info_str = "\n".join(prints_info)

                prompt_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite... [O mesmo prompt final e robusto da v3.0, mas agora com os dados organizados]

**FONTES DE DADOS FORNECIDAS:**
1.  **Link Plantel Anterior:** {link_anterior}
2.  **Link Plantel Atual:** {link_atual}
3.  **Prints de Desempenho:** As imagens fornecidas correspondem aos seguintes prints:
    {prints_info_str}

**ALGORITMO DE EXECUÇÃO OBRIGATÓRIO:**
[... O mesmo algoritmo da v3.0: 1. Comparação de Planteis, 2. Extração de Dados, 3. Redação do Dossiê ...]

---
**MODELO OBRIGATÓRIO (Use este formato exato):**
[... O mesmo modelo de saída da v3.0 ...]
"""
                dossie_final = gerar_resposta_ia(prompt_final, imagens_bytes)
                if dossie_final and "dossiê estratégico de clube" in dossie_final.lower():
                    st.session_state.dossie_clube_final = dossie_final
                else:
                    st.session_state.dossie_clube_final = "A geração do dossiê falhou. A IA pode ter tido dificuldade em aceder aos links ou processar as imagens. Verifique os links e tente novamente."
                
                st.session_state.club_dossier_step = 4
                st.rerun()

        # ETAPA 4: MOSTRAR RESULTADO
        if st.session_state.club_dossier_step == 4:
            st.markdown("---")
            st.header(f"Dossiê de Clube Gerado: {st.session_state.equipa_alvo}")
            
            if "falhou" in st.session_state.dossie_clube_final:
                st.error(st.session_state.dossie_clube_final)
            else:
                st.success("Análise concluída com sucesso!")
                st.markdown(st.session_state.dossie_clube_final)

            if st.button("Limpar e Analisar Outro Clube"):
                # Limpa todas as chaves relacionadas para recomeçar o fluxo
                keys_to_delete = ['club_dossier_step', 'equipa_alvo', 'link_anterior', 'link_atual', 
                                  'print_a', 'print_b', 'print_c', 'dossie_clube_final']
                for key in keys_to_delete:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

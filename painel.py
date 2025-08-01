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

    # --- CENTRAL DE COMANDO COM ABAS ---
    st.header("Central de Comando")
    
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        st.subheader("Criar Dossiê 1: Análise Geral da Liga (Fluxo Interativo)")

        # --- FASE 1: GERAÇÃO DO PANORAMA DA LIGA ---
        if 'dossie_p1_resultado' not in st.session_state:
            with st.form("form_dossie_1_p1"):
                st.markdown("**Parte 1: Panorama da Liga (Pesquisa Autónoma da IA)**")
                st.write("Forneça o contexto para a IA gerar a análise informativa inicial.")
                
                liga = st.text_input("Liga (nome completo)*", placeholder="Ex: Eredivisie")
                pais = st.text_input("País*", placeholder="Ex: Holanda")
                
                if st.form_submit_button("Gerar Panorama da Liga"):
                    if not all([liga, pais]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("AGENTE DE INTELIGÊNCIA a pesquisar e redigir o panorama da liga..."):
                            prompt_p1 = f"""
**PERSONA:** Você é um Jornalista Investigativo e Historiador de Futebol, com um talento para encontrar detalhes que cativem o leitor.
**CONTEXTO:** Liga para Análise: {liga}, País: {pais}
**MISSÃO:** Realize uma pesquisa aprofundada na web para criar a "PARTE 1" de um Dossiê Estratégico sobre a {liga}. O seu relatório deve ser rico em informações, curiosidades e detalhes específicos.
**DIRETRIZES DE PESQUISA (Busque por estes tópicos e SEJA ESPECÍFICO):**
1. Dominância Histórica: Quem são os maiores campeões e como se distribui o poder na última década.
2. Grandes Rivalidades: Quais são os clássicos mais importantes e o que eles representam.
3. Ídolos e Lendas: Mencione 2-3 jogadores históricos que marcaram a liga, **indicando os clubes onde se destacaram**.
4. Estilo de Jogo Característico: A liga é conhecida por ser ofensiva, defensiva, tática? Dê exemplos.
5. Fatos e Curiosidades: Encontre 2-3 factos únicos ou recordes impressionantes, **citando os clubes ou jogadores envolvidos**.
**MODELO DE SAÍDA:**
---
#### **PARTE 1: VISÃO GERAL E HISTÓRICA DA LIGA - {liga.upper()}**
* **Perfil da Liga:** [Resumo sobre o estilo de jogo.]
* **Dominância na Década:** [Análise da distribuição de poder.]
* **Principais Rivalidades:** [Descrição dos clássicos.]
* **Lendas da Liga:** [Menção aos jogadores e seus clubes.]
* **Curiosidades e Recordes:** [Apresentação dos factos interessantes com detalhes.]
---
"""
                            resultado_p1 = gerar_dossie_com_ia(prompt_p1)
                            if resultado_p1:
                                st.session_state['dossie_p1_resultado'] = resultado_p1
                                st.session_state['contexto_liga'] = {'liga': liga, 'pais': pais}
        
        # --- EXIBIÇÃO DA PARTE 1 E FORMULÁRIO DA PARTE 2 ---
        if 'dossie_p1_resultado' in st.session_state:
            st.markdown("---")
            st.success("Parte 1 (Panorama da Liga) gerada com sucesso!")
            st.markdown(st.session_state['dossie_p1_resultado'])
            
            st.markdown("---")
            st.subheader("Parte 2: Análise Técnica para Identificar Clubes Dominantes")
            with st.form("form_dossie_1_p2"):
                st.write("Para uma análise precisa da dominância na última década, por favor, forneça a tabela de classificação final para cada uma das últimas 10 temporadas.")
                
                # --- FORMULÁRIO GRANULAR PARA 10 TEMPORADAS ---
                st.markdown("**Recolha de Dados da Década:**")
                
                dados_temporadas = {}
                # Loop para criar 10 campos de temporada
                for i in range(1, 11):
                    with st.expander(f"Dados da Temporada {i}"):
                        temporada_ano = st.text_input(f"Temporada {i} (Ex: 2024-2025)*", key=f"ano_{i}")
                        prints_classificacao = st.file_uploader(f"Print(s) da Classificação para a Temporada {i}*", 
                                                                help="Sugestão: No FBref, Sofascore ou Transfermarkt, capture a tabela de classificação completa, incluindo a legenda de qualificação europeia.", 
                                                                accept_multiple_files=True, 
                                                                key=f"prints_{i}")
                        # Armazena os dados apenas se ambos os campos estiverem preenchidos
                        if temporada_ano and prints_classificacao:
                            dados_temporadas[temporada_ano] = prints_classificacao

                if st.form_submit_button("Analisar Dados da Década e Gerar Dossiê Final"):
                    if not dados_temporadas:
                        st.error("Por favor, preencha os dados de pelo menos uma temporada.")
                    else:
                        with st.spinner("AGENTE DE DADOS a processar 'prints' e AGENTE DE INTELIGÊNCIA a finalizar o dossiê..."):
                            # Lógica de OCR
                            texto_ocr = ""
                            for temporada, prints in dados_temporadas.items():
                                texto_ocr += f"\n--- [DADOS DO UTILIZADOR PARA A TEMPORADA: {temporada}] ---\n"
                                for p in prints:
                                    texto_ocr += pytesseract.image_to_string(Image.open(p), lang='por+eng') + "\n"
                            
                            # Construção do Prompt Final
                            contexto = st.session_state['contexto_liga']
                            prompt_final = f"""
**PERSONA:** Você é um Analista de Dados Quantitativo...
**DADOS DISPONÍVEIS:**
1. **Análise Informativa (Gerada por si anteriormente):**
{st.session_state['dossie_p1_resultado']}
2. **Dados Técnicos Brutos (Extraídos de prints do utilizador para várias temporadas):**
{texto_ocr}
**MISSÃO FINAL:**
Use a **Análise Informativa** para a Parte 1 e os **Dados Técnicos Brutos** para a Parte 2 para gerar o dossiê consolidado. Na Parte 2, analise as tabelas de classificação de cada temporada para inferir títulos, posições no Top 4 e qualificações europeias. Calcule um 'Placar de Dominância' (5 pts para título, 3 pts para Top 2, 1 pt para Top 4, +2 pts bónus para Champions, +1 pt bónus para Liga Europa), apresente a tabela e justifique a sua 'Playlist de Monitoramento' final.
**MODELO DE SAÍDA:**
---
### **DOSSIÊ ESTRATÉGICO DE LIGA: {contexto['liga'].upper()}**
**DATA:** {datetime.now().strftime('%d/%m/%Y')}
---
#### **PARTE 1: VISÃO GERAL E HISTÓRICA**
[Copie e cole a análise informativa que você já gerou aqui.]
#### **PARTE 2: ANÁLISE TÉCNICA E IDENTIFICAÇÃO DE ALVOS**
* **Placar de Dominância (Última Década):**
| Posição | Equipa | Pontuação |
| :--- | :--- | :--- |
| 1 | [Sua análise aqui] | [Pts] |
...
* **Análise do Analista:** [Sua justificativa aqui.]
#### **VEREDITO FINAL: PLAYLIST DE MONITORAMENTO PARA O DOSSIÊ 2**
* **1. [Equipe 1]**
* **2. [Equipe 2]**
* **3. [Equipe 3]**
---
"""
                            dossie_final = gerar_dossie_com_ia(prompt_final)
                            if dossie_final:
                                st.session_state['dossie_final_completo'] = dossie_final
            
            if 'dossie_final_completo' in st.session_state:
                st.markdown("---")
                st.header("Dossiê Final Consolidado")
                st.markdown(st.session_state['dossie_final_completo'])
                if st.button("Limpar e Iniciar Nova Análise"):
                    for key in list(st.session_state.keys()):
                        if key not in ['password_correct']:
                            del st.session_state[key]
                    st.rerun()

    with tab2:
        st.info("Formulário para o Dossiê 2 em desenvolvimento.")
    with tab3:
        st.info("Formulário para o Dossiê 3 em desenvolvimento.")
    with tab4:
        st.info("Formulário para o Dossiê 4 em desenvolvimento.")

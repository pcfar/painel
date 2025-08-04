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
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Modelo Print-First)")

        # Inicializa o estado do fluxo de trabalho
        if 'club_dossier_step_pf' not in st.session_state:
            st.session_state.club_dossier_step_pf = 1

        # ETAPA 1: DEFINIR ALVO E PRINTS DOS PLANTEIS
        if st.session_state.club_dossier_step_pf == 1:
            with st.form("form_clube_etapa1_pf"):
                st.markdown("**ETAPA 1: DEFINIR O ALVO E OS PLANTEIS**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior",
                                 help="Tire um ou mais prints da sua fonte de dados para o plantel da época passada (ex: 24/25).")
                
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual",
                                 help="Tire um ou mais prints da sua fonte de dados mais fiável para o plantel da nova época (ex: 25/26).")
                
                if st.form_submit_button("Analisar Transferências"):
                    if not all([equipa_nome, st.session_state.prints_plantel_anterior, st.session_state.prints_plantel_atual]):
                        st.error("Por favor, preencha o nome da equipa e carregue os prints de ambos os planteis.")
                    else:
                        st.session_state.equipa_alvo_pf = equipa_nome
                        st.session_state.club_dossier_step_pf = 2
                        st.rerun()

        # ETAPA 2: ANÁLISE DE TRANSFERÊNCIAS E APROFUNDAMENTO INDIVIDUAL
        if st.session_state.club_dossier_step_pf == 2:
            with st.spinner(f"AGENTE DE INTELIGÊNCIA a comparar os planteis..."):
                
                imagens_bytes_anterior = [p.getvalue() for p in st.session_state.prints_plantel_anterior]
                imagens_bytes_atual = [p.getvalue() for p in st.session_state.prints_plantel_atual]
                todas_imagens = imagens_bytes_anterior + imagens_bytes_atual

                prompt_transferencias = f"""
**TAREFA:** Analise os dois conjuntos de imagens de planteis fornecidos e compare-os.
- O primeiro conjunto de imagens representa o plantel da temporada anterior.
- O segundo conjunto de imagens representa o plantel da nova temporada.

**ALGORITMO:**
1.  Leia os nomes dos jogadores de ambos os conjuntos de imagens.
2.  Compare as duas listas de nomes para identificar TODAS as chegadas e TODAS as saídas.
3.  Escreva a secção "1. EVOLUÇÃO DO PLANTEL" em Markdown, incluindo a sua análise de impacto.
4.  **IMPORTANTE:** Após o Markdown, adicione um separador `---JSON_CHEGADAS---` e depois um bloco de código JSON com uma lista dos nomes dos jogadores que chegaram. Ex: {{"chegadas": ["Jogador A", "Jogador B"]}}
"""
                analise_transferencias_raw = gerar_resposta_ia(prompt_transferencias, todas_imagens)
                
                if analise_transferencias_raw and "---JSON_CHEGADAS---" in analise_transferencias_raw:
                    parts = analise_transferencias_raw.split("---JSON_CHEGADAS---")
                    st.session_state.analise_transferencias_md_pf = parts[0]
                    
                    json_str = parts[1].strip()
                    try:
                        chegadas_data = json.loads(json_str)
                        st.session_state.lista_chegadas_pf = chegadas_data.get("chegadas", [])
                    except json.JSONDecodeError:
                        st.session_state.lista_chegadas_pf = []
                else:
                    st.session_state.analise_transferencias_md_pf = "Falha ao analisar as transferências. Verifique os prints."
                    st.session_state.lista_chegadas_pf = []

                st.session_state.club_dossier_step_pf = 3
                st.rerun()

        if st.session_state.club_dossier_step_pf == 3:
            st.markdown("### Parte 1: Evolução do Plantel")
            st.markdown(st.session_state.analise_transferencias_md_pf)
            st.divider()

            with st.form("form_clube_etapa2_pf"):
                st.markdown("**ETAPA 2: APROFUNDAMENTO INDIVIDUAL (OPCIONAL)**")
                st.info("Para quais das novas contratações você gostaria de fornecer dados para um 'Mini Dossiê'?")
                
                jogadores_selecionados = st.multiselect("Selecione os reforços a analisar:", 
                                                       options=st.session_state.get('lista_chegadas_pf', []))
                
                for jogador in jogadores_selecionados:
                    st.file_uploader(f"Carregar print de estatísticas para **{jogador}** (época anterior)", 
                                     key=f"print_{jogador}_pf", 
                                     type=['png', 'jpg', 'jpeg'])

                if st.form_submit_button("Próximo Passo: Dados Coletivos"):
                    st.session_state.prints_jogadores_pf = {}
                    for jogador in jogadores_selecionados:
                        if st.session_state[f"print_{jogador}_pf"]:
                            st.session_state.prints_jogadores_pf[jogador] = st.session_state[f"print_{jogador}_pf"].getvalue()
                    
                    st.session_state.club_dossier_step_pf = 4
                    st.rerun()

        # ETAPA 3: COLETA DE DADOS COLETIVOS
        if st.session_state.club_dossier_step_pf == 4:
            st.markdown("### ETAPA 3: DADOS DE DESEMPENHO COLETIVO")
            with st.form("form_clube_etapa3_pf"):
                st.markdown("""
                **Instruções:** Carregue os 3 prints sobre o desempenho da equipa na época passada.
                - **Print A:** Visão Geral e Performance Ofensiva (FBref)
                - **Print B:** Padrões de Construção de Jogo (FBref)
                - **Print C:** Análise Comparativa Casa vs. Fora (FBref)
                """)
                st.file_uploader("Carregar Prints da Equipa (A, B e C)*", 
                                 accept_multiple_files=True, 
                                 key="prints_equipa_pf")
                
                if st.form_submit_button("Gerar Dossiê Final Completo"):
                    if not st.session_state.prints_equipa_pf or len(st.session_state.prints_equipa_pf) < 3:
                        st.error("Por favor, carregue os 3 prints da equipa.")
                    else:
                        st.session_state.club_dossier_step_pf = 5
                        st.rerun()

        # ETAPA 4: GERAÇÃO FINAL
        if st.session_state.club_dossier_step_pf == 5:
            with st.spinner(f"AGENTE DE INTELIGÊNCIA a consolidar todos os dados e a redigir o dossiê final..."):
                
                todas_imagens_bytes = []
                prompt_imagens_info = []

                for jogador, img_bytes in st.session_state.get('prints_jogadores_pf', {}).items():
                    todas_imagens_bytes.append(img_bytes)
                    prompt_imagens_info.append(f"- A imagem para o 'Mini Dossiê' de **{jogador}** está incluída.")

                for i, print_file in enumerate(st.session_state.prints_equipa_pf):
                    todas_imagens_bytes.append(print_file.getvalue())
                    letra_print = chr(ord('A') + i)
                    prompt_imagens_info.append(f"- A imagem do Print da Equipa **{letra_print}** está incluída.")

                prompt_imagens_info_str = "\n".join(prompt_imagens_info)

                prompt_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite. Com base em TODA a informação fornecida (análise de transferências pré-processada e dados visuais), redija um dossiê profundo e coeso sobre o '{st.session_state.equipa_alvo_pf}'.

**INFORMAÇÃO DISPONÍVEL:**
1.  **Análise de Transferências Inicial:**
    {st.session_state.analise_transferencias_md_pf}
2.  **Dados Visuais (Prints):**
    {prompt_imagens_info_str}

**ALGORITMO DE EXECUÇÃO:**
1.  **Mini Dossiês:** Para cada jogador com um print fornecido, analise as suas estatísticas da época passada e escreva o "Mini Dossiê de Contratação".
2.  **Análise Coletiva:** Analise os prints da equipa (A, B, C) para escrever a secção "DNA DO DESEMPENHO".
3.  **Consolidação:** Junte tudo no **MODELO OBRIGATÓRIO** abaixo, garantindo que a sua análise conecta todos os pontos de forma inteligente.

---
**MODELO OBRIGATÓRIO:**

### **DOSSIÊ ESTRATÉGICO DE CLUBE: {st.session_state.equipa_alvo_pf.upper()}**

{st.session_state.analise_transferencias_md_pf}

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
                st.session_state.dossie_clube_final_pf = dossie_final or "Falha na geração final."
                st.session_state.club_dossier_step_pf = 6
                st.rerun()

        if st.session_state.club_dossier_step_pf == 6:
            st.header(f"Dossiê Final: {st.session_state.equipa_alvo_pf}")
            st.markdown(st.session_state.dossie_clube_final_pf)
            if st.button("Limpar e Analisar Outro Clube"):
                keys_to_delete = [k for k in st.session_state if k.endswith('_pf')]
                for key in keys_to_delete:
                    del st.session_state[key]
                st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

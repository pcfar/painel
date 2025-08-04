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
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Processamento por Etapas)")

        # Inicializa o estado do fluxo de trabalho
        if 'club_dossier_step_staged' not in st.session_state:
            st.session_state.club_dossier_step_staged = 1

        # ETAPA 1: DEFINIR ALVO
        if st.session_state.club_dossier_step_staged == 1:
            with st.form("form_clube_etapa1_staged"):
                st.markdown("**ETAPA 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                if st.form_submit_button("Próximo Passo: Plantel Anterior"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo_staged = equipa_nome
                        st.session_state.club_dossier_step_staged = 2
                        st.rerun()
        
        # ETAPA 2: PROCESSAR PLANTEL ANTERIOR
        if st.session_state.club_dossier_step_staged == 2:
            st.markdown(f"### Etapa 2: Processamento do Plantel Anterior ({st.session_state.equipa_alvo_staged})")
            with st.form("form_clube_etapa2_staged"):
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior_staged")
                if st.form_submit_button("Extrair Plantel Anterior"):
                    if not st.session_state.prints_plantel_anterior_staged:
                        st.error("Por favor, carregue os prints do plantel anterior.")
                    else:
                        with st.spinner("Lendo os prints do plantel anterior..."):
                            imagens_bytes = [p.getvalue() for p in st.session_state.prints_plantel_anterior_staged]
                            prompt = "Leia estas imagens e retorne uma lista JSON com os nomes de todos os jogadores. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_anterior_staged = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_staged = 3
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao extrair a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar os prints.")

        # ETAPA 3: PROCESSAR PLANTEL ATUAL
        if st.session_state.club_dossier_step_staged == 3:
            st.success(f"Plantel anterior processado. Encontrados {len(st.session_state.lista_anterior_staged)} jogadores.")
            st.markdown(f"### Etapa 3: Processamento do Plantel da Nova Temporada ({st.session_state.equipa_alvo_staged})")
            with st.form("form_clube_etapa3_staged"):
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual_staged")
                if st.form_submit_button("Extrair Plantel da Nova Temporada"):
                    if not st.session_state.prints_plantel_atual_staged:
                        st.error("Por favor, carregue os prints do plantel da nova temporada.")
                    else:
                        with st.spinner("Lendo os prints do novo plantel..."):
                            imagens_bytes = [p.getvalue() for p in st.session_state.prints_plantel_atual_staged]
                            prompt = "Leia estas imagens e retorne uma lista JSON com os nomes de todos os jogadores. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_atual_staged = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_staged = 4
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao extrair a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar os prints.")

        # ETAPA 4: ANÁLISE COMPARATIVA
        if st.session_state.club_dossier_step_staged == 4:
            st.success(f"Novo plantel processado. Encontrados {len(st.session_state.lista_atual_staged)} jogadores.")
            with st.spinner("Comparando planteis e gerando a análise de impacto..."):
                prompt_comparativo = f"""
**TAREFA:** Com base nestas duas listas de jogadores, identifique as chegadas e saídas e escreva a "Parte 1: Evolução do Plantel".
**Plantel Anterior:** {json.dumps(st.session_state.lista_anterior_staged)}
**Plantel Atual:** {json.dumps(st.session_state.lista_atual_staged)}

**ALGORITMO:**
1. Compare as duas listas para identificar as diferenças.
2. Escreva a secção "1. EVOLUÇÃO DO PLANTEL" em Markdown, incluindo a sua análise de impacto.
3. **IMPORTANTE:** Após o Markdown, adicione um separador `---JSON_CHEGADAS---` e depois um bloco de código JSON com a lista de nomes das chegadas. Ex: {{"chegadas": ["Jogador A", "Jogador B"]}}
"""
                resposta = gerar_resposta_ia(prompt_comparativo)
                if resposta and "---JSON_CHEGADAS---" in resposta:
                    parts = resposta.split("---JSON_CHEGADAS---")
                    st.session_state.analise_transferencias_md_staged = parts[0]
                    try:
                        dados = json.loads(parts[1].strip())
                        st.session_state.lista_chegadas_staged = dados.get("chegadas", [])
                    except json.JSONDecodeError:
                        st.session_state.lista_chegadas_staged = []
                else:
                    st.session_state.analise_transferencias_md_staged = "Falha ao gerar a análise comparativa."
                    st.session_state.lista_chegadas_staged = []
                st.session_state.club_dossier_step_staged = 5
                st.rerun()

        # ETAPAS FINAIS (Aprofundamento, Dados Coletivos, Geração Final)
        if st.session_state.club_dossier_step_staged >= 5:
            st.markdown(st.session_state.analise_transferencias_md_staged)
            st.divider()

            if st.session_state.club_dossier_step_staged == 5:
                with st.form("form_clube_etapa5_staged"):
                    st.markdown("**ETAPA SEGUINTE: APROFUNDAMENTO INDIVIDUAL (OPCIONAL)**")
                    jogadores_selecionados = st.multiselect("Selecione os reforços a analisar:", options=st.session_state.get('lista_chegadas_staged', []))
                    for jogador in jogadores_selecionados:
                        st.file_uploader(f"Carregar print de estatísticas para **{jogador}**", key=f"print_{jogador}_staged")
                    if st.form_submit_button("Próximo Passo: Dados Coletivos"):
                        st.session_state.prints_jogadores_staged = {}
                        for jogador in jogadores_selecionados:
                            if st.session_state[f"print_{jogador}_staged"]:
                                st.session_state.prints_jogadores_staged[jogador] = st.session_state[f"print_{jogador}_staged"].getvalue()
                        st.session_state.club_dossier_step_staged = 6
                        st.rerun()

            if st.session_state.club_dossier_step_staged == 6:
                with st.form("form_clube_etapa6_staged"):
                    st.markdown("**ETAPA SEGUINTE: DADOS DE DESEMPENHO COLETIVO**")
                    st.file_uploader("Carregar Prints da Equipa (A, B e C)*", accept_multiple_files=True, key="prints_equipa_staged")
                    if st.form_submit_button("Gerar Dossiê Final Completo"):
                        if not st.session_state.prints_equipa_staged or len(st.session_state.prints_equipa_staged) < 3:
                            st.error("Por favor, carregue os 3 prints da equipa.")
                        else:
                            st.session_state.club_dossier_step_staged = 7
                            st.rerun()

            if st.session_state.club_dossier_step_staged == 7:
                with st.spinner("AGENTE DE INTELIGÊNCIA a redigir o dossiê final..."):
                    todas_imagens_bytes = []
                    prompt_imagens_info = []
                    for jogador, img_bytes in st.session_state.get('prints_jogadores_staged', {}).items():
                        todas_imagens_bytes.append(img_bytes)
                        prompt_imagens_info.append(f"- Imagem para 'Mini Dossiê' de **{jogador}**.")
                    for i, print_file in enumerate(st.session_state.prints_equipa_staged):
                        todas_imagens_bytes.append(print_file.getvalue())
                        prompt_imagens_info.append(f"- Imagem do Print da Equipa **{chr(ord('A') + i)}**.")
                    
                    prompt_final = f"""
**TAREFA:** Redija um dossiê profundo sobre o '{st.session_state.equipa_alvo_staged}'.
**INFORMAÇÃO DISPONÍVEL:**
1. **Análise de Transferências:** {st.session_state.analise_transferencias_md_staged}
2. **Dados Visuais (Prints):** {", ".join(prompt_imagens_info)}
**ALGORITMO:** Analise os prints individuais e coletivos e junte tudo no modelo obrigatório, conectando os pontos de forma inteligente.
---
**MODELO OBRIGATÓRIO:**
### **DOSSIÊ ESTRATÉGICO DE CLUBE: {st.session_state.equipa_alvo_staged.upper()}**
{st.session_state.analise_transferencias_md_staged}
* **Mini Dossiês de Contratação:** [Análise dos prints individuais]
**2. DNA DO DESEMPENHO (TEMPORADA ANTERIOR)** [Análise dos prints da equipa]
**3. O PLANO DE JOGO (ANÁLISE TÁTICA)** [Projeção tática]
**4. VEREDITO FINAL E CENÁRIOS DE OBSERVAÇÃO** [Síntese e cenários]
"""
                    dossie_final = gerar_resposta_ia(prompt_final, todas_imagens_bytes)
                    st.session_state.dossie_clube_final_staged = dossie_final or "Falha na geração final."
                    st.session_state.club_dossier_step_staged = 8
                    st.rerun()

            if st.session_state.club_dossier_step_staged == 8:
                st.header(f"Dossiê Final: {st.session_state.equipa_alvo_staged}")
                st.markdown(st.session_state.dossie_clube_final_staged)
                if st.button("Limpar e Analisar Outro Clube"):
                    keys_to_delete = [k for k in st.session_state if k.endswith('_staged')]
                    for key in keys_to_delete:
                        del st.session_state[key]
                    st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

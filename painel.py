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
    
    # Usamos o modelo Pro para as tarefas mais complexas, Flash pode ser usado para tarefas mais simples se necessário.
    model_name = "gemini-1.5-pro-latest" 
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
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube (Verificação por Etapas)")

        if 'club_dossier_step_final' not in st.session_state:
            st.session_state.club_dossier_step_final = 1

        # ETAPA 1: DEFINIR ALVO
        if st.session_state.club_dossier_step_final == 1:
            with st.form("form_clube_etapa1_final"):
                st.markdown("**FASE 1: DEFINIR O ALVO**")
                equipa_nome = st.text_input("Nome da Equipa Alvo*", placeholder="Ex: Manchester City")
                if st.form_submit_button("Próximo Passo: Plantel Anterior"):
                    if not equipa_nome:
                        st.error("Por favor, insira o nome da equipa.")
                    else:
                        st.session_state.equipa_alvo_final = equipa_nome
                        st.session_state.club_dossier_step_final = 2
                        st.rerun()
        
        # ETAPA 2: PROCESSAR PLANTEL ANTERIOR
        if st.session_state.club_dossier_step_final == 2:
            st.markdown(f"### Fase 2: Processamento do Plantel Anterior ({st.session_state.equipa_alvo_final})")
            with st.form("form_clube_etapa2_final"):
                st.file_uploader("Carregar Print(s) do Plantel (Temporada Anterior)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_anterior_final")
                if st.form_submit_button("1. Extrair Plantel Anterior"):
                    if not st.session_state.prints_plantel_anterior_final:
                        st.error("Por favor, carregue os prints do plantel anterior.")
                    else:
                        with st.spinner("Lendo os prints do plantel anterior..."):
                            imagens_bytes = [p.getvalue() for p in st.session_state.prints_plantel_anterior_final]
                            prompt = "Leia estas imagens e retorne uma lista JSON com os nomes de todos os jogadores. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_anterior_final = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_final = 3
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao extrair a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar os prints.")

        # ETAPA 3: PROCESSAR PLANTEL ATUAL
        if st.session_state.club_dossier_step_final == 3:
            st.success(f"**Verificação:** Plantel anterior processado. Encontrados {len(st.session_state.lista_anterior_final)} jogadores.")
            st.markdown(f"### Fase 3: Processamento do Plantel da Nova Temporada ({st.session_state.equipa_alvo_final})")
            with st.form("form_clube_etapa3_final"):
                st.file_uploader("Carregar Print(s) do Plantel (Nova Temporada)*", 
                                 accept_multiple_files=True, 
                                 key="prints_plantel_atual_final")
                if st.form_submit_button("2. Extrair Plantel da Nova Temporada"):
                    if not st.session_state.prints_plantel_atual_final:
                        st.error("Por favor, carregue os prints do plantel da nova temporada.")
                    else:
                        with st.spinner("Lendo os prints do novo plantel..."):
                            imagens_bytes = [p.getvalue() for p in st.session_state.prints_plantel_atual_final]
                            prompt = "Leia estas imagens e retorne uma lista JSON com os nomes de todos os jogadores. Exemplo: {\"jogadores\": [\"Nome A\", \"Nome B\"]}"
                            resposta = gerar_resposta_ia(prompt, imagens_bytes)
                            if resposta:
                                try:
                                    json_str = resposta[resposta.find('{'):resposta.rfind('}')+1]
                                    dados = json.loads(json_str)
                                    st.session_state.lista_atual_final = dados.get("jogadores", [])
                                    st.session_state.club_dossier_step_final = 4
                                    st.rerun()
                                except (json.JSONDecodeError, IndexError):
                                    st.error("Falha ao extrair a lista de jogadores. Verifique os prints ou tente novamente.")
                                    st.text_area("Resposta da IA:", resposta)
                            else:
                                st.error("A IA não conseguiu processar os prints.")

        # ETAPA 4: ANÁLISE COMPARATIVA
        if st.session_state.club_dossier_step_final == 4:
            st.success(f"**Verificação:** Novo plantel processado. Encontrados {len(st.session_state.lista_atual_final)} jogadores.")
            st.markdown("### Fase 4: Análise de Transferências")
            if st.button("3. Comparar Planteis e Gerar Análise de Impacto"):
                with st.spinner("Comparando planteis e gerando a análise de impacto..."):
                    prompt_comparativo = f"""
**TAREFA:** Com base nestas duas listas de jogadores, identifique as chegadas e saídas e escreva a "Parte 1: Evolução do Plantel".
**Plantel Anterior:** {json.dumps(st.session_state.lista_anterior_final)}
**Plantel Atual:** {json.dumps(st.session_state.lista_atual_final)}
**ALGORITMO:** Compare as duas listas para identificar as diferenças. Escreva a secção "1. EVOLUÇÃO DO PLANTEL" em Markdown, incluindo a sua análise de impacto. **IMPORTANTE:** Após o Markdown, adicione um separador `---JSON_CHEGADAS---` e depois um bloco de código JSON com a lista de nomes das chegadas. Ex: {{"chegadas": ["Jogador A", "Jogador B"]}}
"""
                    resposta = gerar_resposta_ia(prompt_comparativo)
                    if resposta and "---JSON_CHEGADAS---" in resposta:
                        parts = resposta.split("---JSON_CHEGADAS---")
                        st.session_state.analise_transferencias_md_final = parts[0]
                        try:
                            dados = json.loads(parts[1].strip())
                            st.session_state.lista_chegadas_final = dados.get("chegadas", [])
                        except json.JSONDecodeError:
                            st.session_state.lista_chegadas_final = []
                    else:
                        st.session_state.analise_transferencias_md_final = "Falha ao gerar a análise comparativa."
                        st.session_state.lista_chegadas_final = []
                    st.session_state.club_dossier_step_final = 5
                    st.rerun()

        # ETAPAS FINAIS (Aprofundamento, Dados Coletivos, Geração Final)
        if st.session_state.club_dossier_step_final >= 5:
            st.markdown(st.session_state.analise_transferencias_md_final)
            st.divider()

            if st.session_state.club_dossier_step_final == 5:
                with st.form("form_clube_etapa5_final"):
                    st.markdown("**Fase 5: Aprofundamento Individual (Opcional)**")
                    jogadores_selecionados = st.multiselect("Selecione os reforços a analisar:", options=st.session_state.get('lista_chegadas_final', []))
                    for jogador in jogadores_selecionados:
                        st.file_uploader(f"Carregar print de estatísticas para **{jogador}**", key=f"print_{jogador}_final")
                    if st.form_submit_button("Próximo Passo: Dados Coletivos"):
                        st.session_state.prints_jogadores_final = {}
                        for jogador in jogadores_selecionados:
                            if st.session_state[f"print_{jogador}_final"]:
                                st.session_state.prints_jogadores_final[jogador] = st.session_state[f"print_{jogador}_final"].getvalue()
                        st.session_state.club_dossier_step_final = 6
                        st.rerun()

            if st.session_state.club_dossier_step_final == 6:
                st.success("**Verificação:** Dados de aprofundamento individual guardados.")
                st.markdown("### Fase 6: Dados de Desempenho Coletivo")
                with st.form("form_clube_etapa6_final"):
                    st.markdown("""
                    **Instruções:** Carregue os 3 prints sobre o desempenho da equipa na época passada.
                    - **Print A:** Visão Geral e Performance Ofensiva (FBref)
                    - **Print B:** Padrões de Construção de Jogo (FBref)
                    - **Print C:** Análise Comparativa Casa vs. Fora (FBref)
                    """)
                    st.file_uploader("Carregar Prints da Equipa (A, B e C)*", accept_multiple_files=True, key="prints_equipa_final")
                    if st.form_submit_button("4. Gerar Dossiê Final Completo"):
                        if not st.session_state.prints_equipa_final or len(st.session_state.prints_equipa_final) < 3:
                            st.error("Por favor, carregue os 3 prints da equipa.")
                        else:
                            st.session_state.club_dossier_step_final = 7
                            st.rerun()

            if st.session_state.club_dossier_step_final == 7:
                with st.spinner("AGENTE DE INTELIGÊNCIA a redigir o dossiê final..."):
                    todas_imagens_bytes = []
                    prompt_imagens_info = []
                    for jogador, img_bytes in st.session_state.get('prints_jogadores_final', {}).items():
                        todas_imagens_bytes.append(img_bytes)
                        prompt_imagens_info.append(f"- Imagem para 'Mini Dossiê' de **{jogador}**.")
                    for i, print_file in enumerate(st.session_state.prints_equipa_final):
                        todas_imagens_bytes.append(print_file.getvalue())
                        prompt_imagens_info.append(f"- Imagem do Print da Equipa **{chr(ord('A') + i)}**.")
                    
                    prompt_final = f"""
**TAREFA:** Redija um dossiê profundo sobre o '{st.session_state.equipa_alvo_final}'.
**INFORMAÇÃO DISPONÍVEL:**
1. **Análise de Transferências:** {st.session_state.analise_transferencias_md_final}
2. **Dados Visuais (Prints):** {", ".join(prompt_imagens_info)}
**ALGORITMO:** Analise os prints individuais e coletivos e junte tudo no modelo obrigatório, conectando os pontos de forma inteligente.
---
**MODELO OBRIGÁTICO:**
### **DOSSIÊ ESTRATÉGICO DE CLUBE: {st.session_state.equipa_alvo_final.upper()}**
{st.session_state.analise_transferencias_md_final}
* **Mini Dossiês de Contratação:** [Análise dos prints individuais]
**2. DNA DO DESEMPENHO (TEMPORADA ANTERIOR)** [Análise dos prints da equipa]
**3. O PLANO DE JOGO (ANÁLISE TÁTICA)** [Projeção tática]
**4. VEREDITO FINAL E CENÁRIOS DE OBSERVAÇÃO** [Síntese e cenários]
"""
                    dossie_final = gerar_resposta_ia(prompt_final, todas_imagens_bytes)
                    st.session_state.dossie_clube_final_final = dossie_final or "Falha na geração final."
                    st.session_state.club_dossier_step_final = 8
                    st.rerun()

            if st.session_state.club_dossier_step_final == 8:
                st.header(f"Dossiê Final: {st.session_state.equipa_alvo_final}")
                st.markdown(st.session_state.dossie_clube_final_final)
                if st.button("Limpar e Analisar Outro Clube"):
                    keys_to_delete = [k for k in st.session_state if k.endswith('_final')]
                    for key in keys_to_delete:
                        del st.session_state[key]
                    st.rerun()

    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

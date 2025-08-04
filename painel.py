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
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt}]
    if imagens_bytes:
        for imagem_bytes in imagens_bytes:
            encoded_image = base64.b64encode(imagem_bytes).decode('utf-8')
            parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})
            
    data = {"contents": [{"parts": parts}]}
    
    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates']:
            return result['candidates'][0]['content']['parts'][0]['text']
    except Exception as e:
        st.error(f"Erro na chamada à API: {e}")
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

    with tab1:
        st.subheader("Criar Dossiê 1: Análise Geral da Liga")

        # FASE 1: GERAÇÃO DO PANORAMA DA LIGA
        if 'dossie_p1_resultado' not in st.session_state:
            with st.form("form_dossie_1_p1"):
                st.markdown("**Parte 1: Panorama da Liga (Pesquisa Autónoma da IA)**")
                liga = st.text_input("Liga (nome completo)*", placeholder="Ex: Premier League")
                pais = st.text_input("País*", placeholder="Ex: Inglaterra")
                if st.form_submit_button("Gerar Panorama da Liga"):
                    if not all([liga, pais]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("AGENTE DE INTELIGÊNCIA a pesquisar e a redigir o relatório..."):
                            prompt_p1 = f"""**TAREFA CRÍTICA:** Gere um relatório sobre a liga de futebol '{liga}' do país '{pais}', seguindo o modelo de saída obrigatório. Fale apenas sobre futebol.
**MODELO DE SAÍDA OBRIGATÓRIO:**
---
### **DOSSIÊ ESTRATÉGICO DE LIGA: {liga.upper()}**
#### **PARTE 1: VISÃO GERAL E HISTÓRICA**
* **Perfil da Liga:** [Resumo]
* **Dominância na Década:** [Análise]
* **Principais Rivalidades:** [Descrição]
* **Lendas da Liga:** [Menção]
* **Curiosidades e Recordes:** [Factos]
---"""
                            resultado_p1 = gerar_resposta_ia(prompt_p1)
                            if resultado_p1 and "dossiê estratégico" in resultado_p1.lower() and "parte 1" in resultado_p1.lower():
                                st.session_state['dossie_p1_resultado'] = resultado_p1
                                st.session_state['contexto_liga'] = {'liga': liga, 'pais': pais}
                                st.rerun()
                            else:
                                st.error("A geração da Parte 1 falhou. Tente novamente.")
                                st.text_area("Resposta recebida:", resultado_p1 or "Nenhuma resposta.", height=150)

        # FASE 2: UPLOAD DAS IMAGENS E GERAÇÃO FINAL
        if 'dossie_p1_resultado' in st.session_state and 'dossie_final_completo' not in st.session_state:
            st.markdown("---"); st.success("Parte 1 gerada!"); st.markdown(st.session_state['dossie_p1_resultado']); st.markdown("---")
            st.subheader("Parte 2: Análise Técnica via Upload de Imagens")
            with st.form("form_dossie_1_p2"):
                prints_classificacao = st.file_uploader("Prints das Classificações*", accept_multiple_files=True, key="prints_gerais")
                if st.form_submit_button("Analisar Imagens e Gerar Dossiê Final"):
                    if not prints_classificacao:
                        st.error("Por favor, faça o upload de pelo menos uma imagem.")
                    else:
                        lista_imagens_bytes = [p.getvalue() for p in prints_classificacao]
                        
                        with st.spinner("Etapa 2.1: Lendo as imagens e extraindo dados..."):
                            prompt_extracao = """**TAREFA:** Analise cada imagem fornecida... [Resto do prompt de extração]..."""
                            json_data_str = gerar_resposta_ia(prompt_extracao, lista_imagens_bytes)

                        if json_data_str:
                            try:
                                with st.spinner("Etapa 2.2: Calculando dominância e escrevendo a análise..."):
                                    start_index = json_data_str.find('[')
                                    if start_index == -1: start_index = json_data_str.find('{')
                                    
                                    if start_index != -1:
                                        json_only_str = json_data_str[start_index:].strip().replace("```", "")
                                        dados_temporadas = json.loads(json_only_str)
                                    else:
                                        raise json.JSONDecodeError("Nenhum bloco JSON encontrado.", json_data_str, 0)
                                    
                                    placar = {}
                                    for temp in dados_temporadas:
                                        for item in temp.get("classificacao", []):
                                            equipa = item.get("equipa")
                                            pos = item.get("posicao")
                                            if not equipa or not isinstance(pos, int): continue
                                            placar.setdefault(equipa, 0)
                                            if pos == 1: placar[equipa] += 5
                                            elif pos == 2: placar[equipa] += 3
                                            elif pos in [3, 4]: placar[equipa] += 1
                                    
                                    placar_ordenado = sorted(placar.items(), key=lambda x: x[1], reverse=True)
                                    
                                    tabela_md = "| Posição | Equipa | Pontuação Total |\n| :--- | :--- | :--- |\n"
                                    for i, (equipa, pontos) in enumerate(placar_ordenado):
                                        tabela_md += f"| {i+1} | {equipa} | {pontos} |\n"
                                        
                                    df_grafico = pd.DataFrame(placar_ordenado, columns=['Equipa', 'Pontuacao'])
                                    st.session_state['dominancia_df'] = df_grafico

                                    contexto = st.session_state['contexto_liga']
                                    prompt_final = f"""**TAREFA:** Você é um analista de futebol... [Resto do prompt de geração final]..."""
                                    dossie_final = gerar_resposta_ia(prompt_final)
                                    st.session_state['dossie_final_completo'] = dossie_final
                                    st.rerun()

                            except (json.JSONDecodeError, TypeError) as e:
                                st.error(f"Falha ao processar os dados extraídos das imagens: {e}")
                                st.text_area("Dados recebidos (para depuração):", json_data_str)
                        else:
                            st.error("A extração de dados das imagens falhou.")

        # EXIBIÇÃO DO DOSSIÊ FINAL E GRÁFICO
        if 'dossie_final_completo' in st.session_state:
            st.markdown("---"); st.header("Dossiê Final Consolidado"); st.success("Dossiê gerado com sucesso!")
            dossie_markdown = st.session_state['dossie_final_completo']
            dominancia_df = st.session_state.get('dominancia_df')
            col1, col2 = st.columns([2, 1.2])
            with col1: st.markdown(dossie_markdown)
            with col2:
                if dominancia_df is not None and not dominancia_df.empty:
                    st.subheader("Visualização da Dominância")
                    
                    # --- CORREÇÃO APLICADA AQUI ---
                    # Define uma cor explícita para as barras para garantir a visibilidade em temas escuros.
                    chart = alt.Chart(dominancia_df).mark_bar(
                        color='#4a90e2', # Uma cor azul clara e visível
                        stroke='black', # Adiciona um contorno para definição
                        strokeWidth=0.5
                    ).encode(
                        x=alt.X('Pontuacao:Q', title='Pontuação Total'),
                        y=alt.Y('Equipa:N', sort='-x', title='Equipa'),
                        tooltip=['Equipa', 'Pontuacao']
                    ).properties(
                        title='Placar de Dominância na Liga'
                    ).configure_axis(
                        labelColor='white', # Cor dos rótulos dos eixos
                        titleColor='white'  # Cor dos títulos dos eixos
                    ).configure_title(
                        color='white' # Cor do título do gráfico
                    ).configure_legend(
                        labelColor='white', # Cor da legenda
                        titleColor='white'
                    )

                    st.altair_chart(chart, use_container_width=True)
            if st.button("Limpar e Iniciar Nova Análise"):
                password_state = st.session_state.get("password_correct", False)
                st.session_state.clear()
                st.session_state["password_correct"] = password_state
                st.rerun()

    with tab2: st.info("Em desenvolvimento.")
    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

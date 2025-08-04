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

# --- FUNÇÕES DE CHAMADA À IA (ESPECIALIZADAS) ---

# Função Otimizada APENAS para gerar texto
def gerar_texto_com_ia(prompt):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada.")
        return None
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    data = {"contents": [{"parts": [{"text": prompt}]}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=180)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error("Resposta da IA recebida, mas em formato inesperado.")
            st.json(result)
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na chamada à API: {e}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Erro ao processar a resposta da IA: {e}")
        return None

# Função Otimizada para gerar texto A PARTIR DE TEXTO + IMAGENS
def gerar_dossie_com_ia_multimodal(prompt_texto, lista_imagens_bytes):
    api_key = st.secrets.get("GEMINI_API_KEY")
    if not api_key:
        st.error("Chave da API do Gemini não encontrada.")
        return None

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={api_key}"
    headers = {'Content-Type': 'application/json'}
    
    parts = [{"text": prompt_texto}]
    for imagem_bytes in lista_imagens_bytes:
        encoded_image = base64.b64encode(imagem_bytes).decode('utf-8')
        parts.append({"inline_data": {"mime_type": "image/jpeg", "data": encoded_image}})

    data = {"contents": [{"parts": parts}]}

    try:
        response = requests.post(url, headers=headers, data=json.dumps(data), timeout=300)
        response.raise_for_status()
        result = response.json()
        if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            st.error("Resposta da IA (multimodal) em formato inesperado.")
            st.json(result)
            return None
    except requests.exceptions.RequestException as e:
        st.error(f"Erro na chamada à API (multimodal): {e}")
        return None
    except (KeyError, IndexError) as e:
        st.error(f"Erro ao processar a resposta da IA (multimodal): {e}")
        return None

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    st.sidebar.success("Autenticado com sucesso.")
    st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")

    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception as e:
            st.error(f"Erro ao conectar com o GitHub: {e}")
            st.stop()
    repo = get_github_connection()

    st.header("Central de Comando")
    tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

    with tab1:
        st.subheader("Criar Dossiê 1: Análise Geral da Liga")

        # --- FASE 1: GERAÇÃO DO PANORAMA DA LIGA ---
        if 'dossie_p1_resultado' not in st.session_state:
            with st.form("form_dossie_1_p1"):
                st.markdown("**Parte 1: Panorama da Liga (Pesquisa Autónoma da IA)**")
                liga = st.text_input("Liga (nome completo)*", placeholder="Ex: Premier League")
                pais = st.text_input("País*", placeholder="Ex: Inglaterra")
                
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
                            resultado_p1 = gerar_texto_com_ia(prompt_p1)
                            
                            # --- CORREÇÃO APLICADA AQUI ---
                            # Validação mais flexível, baseada no conteúdo e não na formatação exata.
                            # Verifica se a resposta contém os elementos chave esperados para a Parte 1.
                            if resultado_p1 and "parte 1" in resultado_p1.lower() and "visão geral" in resultado_p1.lower():
                                st.session_state['dossie_p1_resultado'] = resultado_p1
                                st.session_state['contexto_liga'] = {'liga': liga, 'pais': pais}
                                st.rerun()
                            else:
                                st.error("A geração da Parte 1 falhou ou retornou uma resposta inválida. Por favor, tente novamente.")
                                st.text_area("Resposta recebida da IA:", resultado_p1 or "Nenhuma resposta.", height=150)

        # --- FASE 2: UPLOAD DAS IMAGENS E GERAÇÃO FINAL ---
        if 'dossie_p1_resultado' in st.session_state and 'dossie_final_completo' not in st.session_state:
            st.markdown("---")
            st.success("Parte 1 (Panorama da Liga) gerada com sucesso!")
            st.markdown(st.session_state['dossie_p1_resultado'])
            st.markdown("---")
            st.subheader("Parte 2: Análise Técnica via Upload de Imagens")
            with st.form("form_dossie_1_p2"):
                st.write("Faça o upload das imagens das tabelas de classificação. A IA irá analisá-las diretamente.")
                prints_classificacao = st.file_uploader(
                    "Prints das Classificações das Últimas Temporadas*",
                    help="Capture as tabelas de classificação completas. A IA irá 'ler' as imagens.",
                    accept_multiple_files=True,
                    key="prints_gerais"
                )
                if st.form_submit_button("Analisar Imagens e Gerar Dossiê Final"):
                    if not prints_classificacao:
                        st.error("Por favor, faça o upload de pelo menos uma imagem.")
                    else:
                        with st.spinner("AGENTE DE INTELIGÊNCIA a 'ler' as imagens e a finalizar o dossiê..."):
                            lista_imagens_bytes = [p.getvalue() for p in prints_classificacao]
                            contexto = st.session_state['contexto_liga']
                            prompt_final = f"""
**PERSONA:** Você é um Analista de Dados Quantitativo e um Especialista em Futebol, com uma capacidade excecional para interpretar dados visuais (imagens de tabelas) e apresentar conclusões claras.
**CONTEXTO:** Você recebeu duas fontes de informação para criar um dossiê sobre a liga '{contexto['liga']}':
1.  **Análise Qualitativa (Parte 1):** Um resumo textual sobre a liga que você mesmo gerou.
2.  **Dados Visuais (Imagens):** Uma série de imagens, cada uma contendo uma tabela de classificação de uma temporada diferente.
**MISSÃO FINAL:** Sua missão é analisar CADA imagem fornecida, extrair os dados quantitativos, e consolidar tudo num único dossiê coerente.
**PROCESSO PASSO A PASSO (SIGA RIGOROSAMENTE):**
**PASSO 1: Análise Visual e Extração de Dados**
* Para CADA imagem que eu lhe enviei:
    * **Identifique a temporada** (ex: 2022/2023, 2021-22) olhando para o conteúdo da imagem.
    * **Extraia a classificação final.** Foque-se em: **Posição, Nome da Equipa**. Ignore colunas de pontos, golos, etc., a menos que precise delas para desempatar.
    * Se uma imagem for ilegível ou não contiver uma tabela de classificação, ignore-a e faça uma nota mental.
**PASSO 2: Cálculo do 'Placar de Dominância'**
* Depois de analisar TODAS as imagens e extrair os dados, crie uma pontuação para cada equipa com base na seguinte regra:
    * **1º Lugar (Campeão):** 5 pontos
    * **2º Lugar:** 3 pontos
    * **3º ou 4º Lugar:** 1 ponto
* Some os pontos de cada equipa ao longo de todas as temporadas que conseguiu analisar.
**PASSO 3: Geração do Dossiê Final**
* Use o modelo de saída abaixo para estruturar a sua resposta.
* **Parte 1:** Copie na íntegra a análise qualitativa que você já possui.
* **Parte 2:**
    * Apresente a tabela do **'Placar de Dominância'** que você calculou, ordenada da maior para a menor pontuação.
    * Escreva uma **'Análise do Analista'**, justificando as conclusões tiradas da tabela.
* **Veredito Final:** Com base em TUDO (análise qualitativa e a sua nova análise quantitativa das imagens), liste as 3 a 5 equipas mais relevantes para monitorização.
**DADOS DISPONÍVEIS PARA A SUA ANÁLISE:**
**1. Análise Qualitativa (Parte 1 - Texto):**
{st.session_state['dossie_p1_resultado']}
**2. Dados Visuais (Parte 2 - Imagens):**
[As imagens que lhe enviei a seguir a este texto são os seus dados visuais. Analise-as agora.]
**MODELO DE SAÍDA OBRIGATÓRIO:**
---
### **DOSSIÊ ESTRATÉGICO DE LIGA: {contexto['liga'].upper()}**
**DATA DE GERAÇÃO:** {datetime.now().strftime('%d/%m/%Y')}
---
#### **PARTE 1: VISÃO GERAL E HISTÓRICA**
[Copie e cole a análise informativa da Parte 1 aqui.]
---
#### **PARTE 2: ANÁLISE TÉCNICA E IDENTIFICAÇÃO DE ALVOS**
**Placar de Dominância (Baseado na análise das imagens fornecidas):**
| Posição | Equipa | Pontuação Total |
| :--- | :--- | :--- |
| 1 | [Sua análise aqui] | [Pts] |
| 2 | [Sua análise aqui] | [Pts] |
| ... | ... | ... |
**Análise do Analista:**
[A sua análise e justificativa aqui. Comente os resultados da tabela de dominância.]
---
#### **VEREDITO FINAL: PLAYLIST DE MONITORAMENTO**
* **1. [Equipa 1]:** [Breve justificativa baseada na sua análise completa.]
* **2. [Equipa 2]:** [Breve justificativa baseada na sua análise completa.]
* **3. [Equipa 3]:** [Breve justificativa baseada na sua análise completa.]
---
"""
                            dossie_final = gerar_dossie_com_ia_multimodal(prompt_final, lista_imagens_bytes)
                            if dossie_final:
                                st.session_state['dossie_final_completo'] = dossie_final
                                st.rerun()
                            else:
                                st.error("A geração do dossiê final falhou. Verifique os logs de erro.")

        # --- EXIBIÇÃO DO DOSSIÊ FINAL ---
        if 'dossie_final_completo' in st.session_state:
            st.markdown("---")
            st.header("Dossiê Final Consolidado")
            st.success("Dossiê gerado com sucesso!")
            st.markdown(st.session_state['dossie_final_completo'])
            if st.button("Limpar e Iniciar Nova Análise"):
                password_state = st.session_state.get("password_correct", False)
                st.session_state.clear()
                st.session_state["password_correct"] = password_state
                st.rerun()

    with tab2: st.info("Em desenvolvimento.")
    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

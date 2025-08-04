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
    if st.session_state.get("password_correct", False):
        return True

    def password_entered():
        if st.session_state.get("password") == st.secrets.get("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

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
            response = requests.post(url, headers=headers, data=json.dumps(data), timeout=180) # Aumentado o timeout
            response.raise_for_status()
            result = response.json()
            # Validação mais robusta da resposta
            if 'candidates' in result and result['candidates'] and 'content' in result['candidates'][0] and 'parts' in result['candidates'][0]['content'] and result['candidates'][0]['content']['parts']:
                return result['candidates'][0]['content']['parts'][0]['text']
            else:
                st.error(f"Resposta da IA recebida, mas em formato inesperado.")
                st.json(result)
                return None
        except requests.exceptions.RequestException as e:
            st.error(f"Erro na chamada à API (tentativa {attempt + 1}/{max_retries}): {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
            else:
                st.error(f"Resposta da API: {response.text if 'response' in locals() else 'Sem resposta'}")
                return None
        except (KeyError, IndexError, json.JSONDecodeError) as e:
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
        except Exception as e:
            st.error(f"Erro ao conectar com o GitHub: {e}")
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
                                st.rerun() # Força o recarregamento para mostrar a próxima fase
        
        # --- EXIBIÇÃO DA PARTE 1 E FORMULÁRIO DA PARTE 2 (LÓGICA OTIMIZADA) ---
        if 'dossie_p1_resultado' in st.session_state and 'dossie_final_completo' not in st.session_state:
            st.markdown("---")
            st.success("Parte 1 (Panorama da Liga) gerada com sucesso!")
            st.markdown(st.session_state['dossie_p1_resultado'])
            
            st.markdown("---")
            st.subheader("Parte 2: Análise Técnica para Identificar Clubes Dominantes")
            with st.form("form_dossie_1_p2"):
                st.write("Para uma análise precisa da dominância na última década, por favor, faça o upload das imagens das tabelas de classificação final para cada uma das últimas temporadas que deseja analisar.")
                
                # --- CAMPO ÚNICO PARA UPLOAD DE MÚLTIPLOS ARQUIVOS ---
                st.markdown("**Recolha de Dados da Década:**")
                
                prints_classificacao = st.file_uploader(
                    "Prints das Classificações das Últimas Temporadas*",
                    help="Sugestão: Capture as tabelas de classificação completas (FBref, Sofascore, etc.). A IA tentará identificar o ano de cada tabela a partir do conteúdo da imagem.",
                    accept_multiple_files=True,
                    key="prints_gerais"
                )

                if st.form_submit_button("Analisar Dados e Gerar Dossiê Final"):
                    if not prints_classificacao:
                        st.error("Por favor, faça o upload de pelo menos uma imagem de classificação.")
                    else:
                        with st.spinner("AGENTE DE DADOS a processar 'prints' e AGENTE DE INTELIGÊZA a finalizar o dossiê..."):
                            # Lógica de OCR otimizada
                            texto_ocr_formatado = ""
                            st.write(f"A processar {len(prints_classificacao)} imagens...")
                            progress_bar = st.progress(0)
                            for i, p in enumerate(prints_classificacao):
                                texto_ocr_formatado += f"\n--- INÍCIO DADOS IMAGEM {i+1} ---\n"
                                try:
                                    img = Image.open(p)
                                    texto_ocr_formatado += pytesseract.image_to_string(img, lang='por+eng') + "\n"
                                except Exception as e:
                                    texto_ocr_formatado += f"[ERRO AO LER IMAGEM {i+1}: {e}]\n"
                                texto_ocr_formatado += f"--- FIM DADOS IMAGEM {i+1} ---\n"
                                progress_bar.progress((i + 1) / len(prints_classificacao))
                            
                            # Construção do Prompt Final Otimizado
                            contexto = st.session_state['contexto_liga']
                            prompt_final = f"""
**PERSONA:** Você é um Analista de Dados Quantitativo e um Especialista em Futebol, com uma capacidade excecional para extrair informações de dados não estruturados e apresentar conclusões claras e objetivas.

**CONTEXTO:** Você recebeu duas fontes de informação para criar um dossiê sobre a liga '{contexto['liga']}':
1.  **Análise Qualitativa (Parte 1):** Um resumo histórico e cultural da liga, que você mesmo gerou.
2.  **Dados Brutos de OCR (Parte 2):** Um conjunto de textos extraídos de várias imagens de tabelas de classificação. Cada bloco de texto, separado por "--- INÍCIO/FIM DADOS IMAGEM ---", representa uma temporada diferente. Estes dados podem conter ruído e erros de extração.

**MISSÃO FINAL:** Sua missão é consolidar estas informações num único dossiê coerente. Você deve usar os dados brutos de OCR para realizar uma análise quantitativa e, em seguida, apresentar um veredito.

**PROCESSO PASSO A PASSO (SIGA RIGOROSAMENTE):**

**PASSO 1: Extração e Estruturação dos Dados de OCR**
* Para cada bloco de texto de imagem, a sua primeira tarefa é identificar a **temporada** (ex: 2022/2023, 2021-22). Procure por anos no texto.
* Em seguida, extraia a classificação final. Foque-se em: **Posição, Nome da Equipa**.
* Se o texto de uma imagem for ilegível ou não contiver uma tabela de classificação, ignore-o e mencione que os dados daquela imagem não puderam ser processados.

**PASSO 2: Cálculo do 'Placar de Dominância'**
* Depois de estruturar os dados de todas as temporadas legíveis, crie uma pontuação para cada equipa com base na seguinte regra:
    * **1º Lugar (Campeão):** 5 pontos
    * **2º Lugar:** 3 pontos
    * **3º ou 4º Lugar:** 1 ponto
* Some os pontos de cada equipa ao longo de todas as temporadas analisadas.

**PASSO 3: Geração do Dossiê Final**
* Use o modelo de saída abaixo para estruturar a sua resposta.
* **Parte 1:** Copie na íntegra a análise qualitativa que você já possui.
* **Parte 2:**
    * Apresente a tabela do **'Placar de Dominância'** que você calculou, ordenada da maior para a menor pontuação.
    * Escreva uma breve **'Análise do Analista'**, explicando as conclusões tiradas da tabela. Justifique por que certas equipas dominaram, se houve surpresas ou se o poder é bem distribuído.
* **Veredito Final:** Com base em TUDO (análise qualitativa e quantitativa), liste as 3 a 5 equipas mais relevantes para monitorização. Justifique brevemente cada escolha.

**DADOS DISPONÍVEIS PARA A SUA ANÁLISE:**

**1. Análise Qualitativa (Parte 1):**
{st.session_state['dossie_p1_resultado']}

**2. Dados Brutos de OCR (Parte 2):**
{texto_ocr_formatado}

**MODELO DE SAÍDA OBRIGATÓRIO:**
---
### **DOSSIÊ ESTRATÉGICO DE LIGA: {contexto['liga'].upper()}**
**DATA DE GERAÇÃO:** {datetime.now().strftime('%d/%m/%Y')}
---
#### **PARTE 1: VISÃO GERAL E HISTÓRICA**
[Copie e cole a análise informativa da Parte 1 aqui, mantendo a formatação original.]
---
#### **PARTE 2: ANÁLISE TÉCNICA E IDENTIFICAÇÃO DE ALVOS**

**Placar de Dominância (Baseado nos dados fornecidos):**
| Posição | Equipa | Pontuação Total |
| :--- | :--- | :--- |
| 1 | [Sua análise aqui] | [Pts] |
| 2 | [Sua análise aqui] | [Pts] |
| ... | ... | ... |

**Análise do Analista:**
[A sua análise e justificativa aqui. Comente os resultados da tabela de dominância. Ex: "O clube X demonstra uma clara hegemonia, conquistando o título em Y das Z temporadas analisadas. A equipa Y surge como a principal concorrente, mantendo-se consistentemente no Top 2..."]

---
#### **VEREDITO FINAL: PLAYLIST DE MONITORAMENTO**
* **1. [Equipa 1]:** [Breve justificativa baseada na sua análise completa.]
* **2. [Equipa 2]:** [Breve justificativa baseada na sua análise completa.]
* **3. [Equipa 3]:** [Breve justificativa baseada na sua análise completa.]
---
"""
                            dossie_final = gerar_dossie_com_ia(prompt_final)
                            if dossie_final:
                                st.session_state['dossie_final_completo'] = dossie_final
                                st.rerun()

        # --- EXIBIÇÃO DO DOSSIÊ FINAL ---
        if 'dossie_final_completo' in st.session_state:
            st.markdown("---")
            st.header("Dossiê Final Consolidado")
            st.success("Dossiê gerado com sucesso!")
            st.markdown(st.session_state['dossie_final_completo'])
            if st.button("Limpar e Iniciar Nova Análise"):
                # Guarda o estado da senha
                password_state = st.session_state.get("password_correct", False)
                # Limpa tudo
                st.session_state.clear()
                # Restaura o estado da senha
                st.session_state["password_correct"] = password_state
                st.rerun()

    with tab2:
        st.info("Formulário para o Dossiê 2 em desenvolvimento.")
    with tab3:
        st.info("Formulário para o Dossiê 3 em desenvolvimento.")
    with tab4:
        st.info("Formulário para o Dossiê 4 em desenvolvimento.")

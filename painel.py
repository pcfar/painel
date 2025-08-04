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

    # --- ABA 1: DOSSIÊ DE LIGA ---
    with tab1:
        # ... (Todo o código da Aba 1, que já está estável, permanece aqui)
        st.info("O Dossiê de Liga está funcional. Use esta aba para analisar uma liga inteira.")


    # --- ABA 2: DOSSIÊ DE CLUBE ---
    with tab2:
        st.subheader("Criar Dossiê 2: Análise Profunda de Clube")

        # --- Etapa 1: Seleção do Alvo e Geração do Briefing ---
        if 'dossie_clube_final' not in st.session_state:
            with st.form("form_clube_p1"):
                st.markdown("**Etapa 1: Selecione o alvo e gere o briefing de dados para validação.**")
                
                # Placeholder para a lista de equipas. Idealmente, viria do Dossiê 1.
                # Se o dataframe do Dossiê 1 existir, usa-o. Senão, usa uma lista padrão.
                if 'dominancia_df' in st.session_state and st.session_state.dominancia_df is not None:
                    lista_equipas = st.session_state.dominancia_df['Equipa'].tolist()
                else:
                    lista_equipas = ["Manchester City", "Liverpool", "Arsenal", "Chelsea", "Manchester United"]

                equipa_alvo = st.selectbox("Selecione a Equipa Alvo*", options=lista_equipas)
                
                fontes_prioritarias = st.text_area("Fontes Prioritárias (Opcional)", 
                                                   help="Insira URLs (uma por linha) de fontes que a IA deve priorizar na pesquisa (ex: página do plantel no Transfermarkt).")

                if st.form_submit_button("Gerar Briefing de Dados"):
                    if not equipa_alvo:
                        st.error("Por favor, selecione uma equipa.")
                    else:
                        with st.spinner(f"AGENTE DE INTELIGÊNCIA a pesquisar dados sobre o {equipa_alvo}..."):
                            prompt_briefing = f"""
**TAREFA CRÍTICA:** Aja como um pesquisador de dados desportivos. Realize uma pesquisa aprofundada na web sobre o clube '{equipa_alvo}'.

**FONTES A PRIORIZAR (se fornecidas):**
{fontes_prioritarias}

**DADOS A ENCONTRAR (OBRIGATÓRIO CITAR A FONTE PARA CADA DADO):**
1.  **Treinador Atual:** Nome e há quanto tempo está no cargo.
2.  **Principais Transferências (Entradas):** Liste 2-3 reforços chave para a temporada atual/próxima.
3.  **Principais Transferências (Saídas):** Liste 2-3 saídas importantes.
4.  **Estatísticas Chave (Temporada Anterior):** Encontre o xG (Gols Esperados) a favor e contra por jogo, e a posse de bola média.
5.  **Onze Titular Provável:** Com base nas notícias mais recentes, qual a formação e os 11 jogadores mais prováveis?

**FORMATO DE SAÍDA OBRIGATÓRIO (BRIEFING DE VALIDAÇÃO):**
Use Markdown para apresentar os dados de forma clara, citando a fonte com um link para cada informação factual. Exemplo:
- **Treinador:** Nome do Treinador (Fonte: https://www.dafont.com/pt/)
"""
                            briefing = gerar_resposta_ia(prompt_briefing)
                            if briefing:
                                st.session_state['briefing_dados'] = briefing
                                st.session_state['equipa_alvo_selecionada'] = equipa_alvo
                                st.rerun()
                            else:
                                st.error("A pesquisa de dados falhou. A IA não retornou um briefing. Tente novamente.")

        # --- Etapa 2: Validação e Geração do Dossiê Final ---
        if 'briefing_dados' in st.session_state and 'dossie_clube_final' not in st.session_state:
            st.markdown("---")
            st.subheader("Etapa 2: Validação do Briefing e Geração do Dossiê Final")
            
            st.info("Por favor, valide os dados encontrados pela IA. Se estiverem corretos, aprove para gerar o dossiê completo.")
            st.markdown(st.session_state['briefing_dados'])

            if st.button("Aprovar Dados e Gerar Dossiê Completo"):
                with st.spinner(f"AGENTE DE INTELIGÊNCIA a redigir o dossiê completo sobre o {st.session_state['equipa_alvo_selecionada']}..."):
                    prompt_dossie_final = f"""
**TAREFA CRÍTICA:** Aja como um Analista de Futebol de elite. Com base nos factos validados abaixo, escreva um dossiê profundo sobre o '{st.session_state['equipa_alvo_selecionada']}', seguindo a estrutura detalhada.

**FACTOS VALIDADOS (Use apenas esta informação para a base factual):**
---
{st.session_state['briefing_dados']}
---

**ESTRUTURA DO DOSSIÊ (MODELO OBRIGATÓRIO):**

### **DOSSIÊ ESTRATÉGICO DE CLUBE: {st.session_state['equipa_alvo_selecionada'].upper()}**

**1. O DNA DO CLUBE (A IDENTIDADE)**
* **Fotografia do Elenco Atual:**
    * **Onze Titular Provável (Tabela):** [Crie uma tabela com a formação e os 11 titulares]
    * **Análise de Transferências:** [Descreva o impacto dos reforços e saídas listados nos factos]
* **Raio-X da Temporada Anterior:**
    * **Padrões Estatísticos:** [Analise os dados de xG e posse de bola dos factos. O que eles nos dizem sobre o estilo da equipa?]

**2. A MÁQUINA TÁTICA (COMO A EQUIPA JOGA)**
* **O Comandante e a Sua Filosofia:** [Analise o perfil do treinador listado nos factos]
* **Decodificando o Sistema:**
    * **O Jogador-Sistema:** [Com base no onze titular, identifique e analise o jogador tático mais fundamental]
    * **Flexibilidade e Variações:** [Discuta como a equipa pode variar taticamente com base no plantel]

**3. O VEREDITO ACIONÁVEL (O QUE OBSERVAR)**
* **Síntese Analítica (O Resumo Inteligente):** [Conecte todos os pontos: como as transferências impactam o sistema do treinador, refletido nos padrões estatísticos]
* **Cenários de Monitoramento In-Live (Os Gatilhos):** [Crie 3 cenários práticos para observar durante os jogos]
"""
                    dossie_final = gerar_resposta_ia(prompt_dossie_final)
                    if dossie_final:
                        st.session_state['dossie_clube_final'] = dossie_final
                        st.rerun()
                    else:
                        st.error("A geração do dossiê final falhou. Tente novamente.")

        # --- Exibição do Dossiê de Clube Final ---
        if 'dossie_clube_final' in st.session_state:
            st.markdown("---")
            st.header(f"Dossiê Final: {st.session_state['equipa_alvo_selecionada']}")
            st.success("Dossiê de clube gerado com sucesso!")
            st.markdown(st.session_state['dossie_clube_final'])

            if st.button("Limpar e Analisar Outro Clube"):
                # Limpa apenas as chaves relacionadas ao Dossiê de Clube
                for key in ['briefing_dados', 'dossie_clube_final', 'equipa_alvo_selecionada']:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()


    with tab3: st.info("Em desenvolvimento.")
    with tab4: st.info("Em desenvolvimento.")

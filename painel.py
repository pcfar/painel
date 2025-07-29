import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Painel de Inteligência Tática", page_icon="🧠", layout="wide")

# --- SISTEMA DE SENHA ÚNICA ---
def check_password():
    def password_entered():
        if st.session_state["password"] == st.secrets.get("APP_PASSWORD"):
            st.session_state["password_correct"] = True
            st.session_state["role"] = "admin" # Acesso total com a senha única
            del st.session_state["password"]
        else:
            st.session_state["password_correct"] = False

    if st.session_state.get("password_correct", False):
        return True

    st.text_input("Password", type="password", on_change=password_entered, key="password")
    if "password_correct" in st.session_state and not st.session_state["password_correct"]:
        st.error("😕 Senha incorreta.")
    return False

# --- APLICAÇÃO PRINCIPAL ---
if check_password():
    role = st.session_state.get("role", "visitor")
    st.sidebar.write(f"Bem-vindo! Perfil: **{role.upper()}**")
    st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
    st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

    # --- Conexão com o GitHub ---
    @st.cache_resource
    def get_github_connection():
        try:
            g = Github(st.secrets["GITHUB_TOKEN"])
            repo = g.get_repo("pcfar/painel")
            return repo
        except Exception:
            st.error("Erro ao conectar com o GitHub. Verifique o GITHUB_TOKEN.")
            st.stop()
    repo = get_github_connection()

    # --- Funções Auxiliares ---
    @st.cache_data(ttl=300)
    def listar_conteudo_pasta(caminho):
        try:
            return [item for item in repo.get_contents(caminho) if not item.name.startswith('.')]
        except UnknownObjectException:
            return []

    # --- CENTRAL DE UPLOAD ---
    st.header("1. Central de Upload Guiado")
    with st.expander("Clique aqui para enviar novos 'prints' para análise"):
        # (Aqui entrará a interface de upload com abas que planejamos)
        st.info("Interface de upload guiado em desenvolvimento.")

    # --- CENTRAL DE ANÁLISE ---
    st.markdown("---")
    st.header("2. Central de Análise: Gerar Dossiês")

    temporadas = [item.path for item in listar_conteudo_pasta("") if item.type == "dir"]
    if not temporadas:
        st.info("Nenhum dado disponível. Use a Central de Upload para enviar 'prints'.")
    else:
        sel_temporada = st.selectbox("Passo 1: Selecione a Temporada", [""] + temporadas)
        if sel_temporada:
            ligas = [item.name for item in listar_conteudo_pasta(sel_temporada) if item.type == "dir"]
            if ligas:
                sel_liga = st.selectbox("Passo 2: Selecione a Liga", [""] + ligas)
                if sel_liga:
                    path_liga = os.path.join(sel_temporada, sel_liga)
                    clubes = [item.name for item in listar_conteudo_pasta(path_liga) if item.type == "dir"]
                    if clubes:
                        sel_clube = st.selectbox("Passo 3: Selecione o Clube/Alvo", [""] + clubes)
                        if sel_clube:
                            path_final = os.path.join(path_liga, sel_clube)
                            st.success(f"Seleção: **{path_final}**")

                            if st.button(f"Gerar Dossiê para {sel_clube} ({sel_liga})"):
                                with st.spinner(f"AGENTE DE COLETA a extrair dados de '{path_final}'..."):
                                    imagens = [f for f in listar_conteudo_pasta(path_final) if f.name.lower().endswith(('.png', '.jpg'))]
                                    if not imagens:
                                        st.warning("Nenhuma imagem encontrada nesta pasta para análise.")
                                    else:
                                        texto_bruto_completo = ""
                                        for img_obj in imagens:
                                            conteudo_img = io.BytesIO(img_obj.decoded_content)
                                            imagem = Image.open(conteudo_img)
                                            texto_bruto_completo += f"\n\n--- [INÍCIO DO PRINT: {img_obj.name}] ---\n"
                                            texto_bruto_completo += pytesseract.image_to_string(imagem, lang='por+eng')
                                            texto_bruto_completo += f"\n--- [FIM DO PRINT: {img_obj.name}] ---\n"

                                        st.session_state['texto_bruto_pronto'] = texto_bruto_completo
                                        st.session_state['contexto'] = {'liga': sel_liga, 'temporada': sel_temporada}
                                        st.rerun()

    # --- SEÇÃO DE RESULTADO FINAL ---
    if 'texto_bruto_pronto' in st.session_state:
        st.markdown("---")
        st.header("3. Dossiê Final Gerado")

        # Monta o Prompt Mestre
        contexto = st.session_state['contexto']
        prompt = f"""
        **PERSONA:** Você é um Analista de Dados de Futebol Sênior.
        **CONTEXTO:** Liga: {contexto['liga']}, Temporada de Referência: {contexto['temporada']}
        **DADOS BRUTOS PARA ANÁLISE:**
        {st.session_state['texto_bruto_pronto']}
        **TAREFA:** Analise o texto bruto e gere um relatório conciso em Markdown.
        **MODELO DE SAÍDA:**
        ---
        ### **DOSSIÊ DE LIGA: {contexto['liga'].upper()}**
        **Temporada de Referência:** {contexto['temporada']}
        #### **1. Visão Histórica**
        * **Principais Campeões:** [Liste as equipes e o número de títulos encontrados.]
        #### **2. Análise da Última Temporada**
        * **Campeão:** [Extraia o nome do campeão.]
        * **Top 4:** [Liste as 4 primeiras equipes.]
        #### **3. Veredito do Analista**
        Com base nos dados, as seguintes equipes são selecionadas para monitoramento:
        * **1. [Nome da Equipe 1]**
        * **2. [Nome da Equipe 2]**
        * **3. [Nome da Equipe 3]**
        ---
        """

        with st.spinner("AGENTE REDATOR TÉCNICO a processar o dossiê..."):
            # AQUI SERIA A CHAMADA REAL PARA A IA. POR AGORA, MOSTRAMOS UMA SIMULAÇÃO.
            # No futuro, o resultado de uma chamada a uma API de LLM com o prompt acima entraria aqui.
            st.markdown("### **DOSSIÊ DE LIGA: HOL**")
            st.markdown("**Temporada de Referência:** 2025-2026")
            st.markdown("#### **1. Visão Histórica**")
            st.markdown("* **Principais Campeões:** PSV (3), Ajax (3), Feyenoord (2)")
            st.markdown("#### **2. Análise da Última Temporada**")
            st.markdown("* **Campeão:** PSV Eindhoven")
            st.markdown("* **Top 4:** 1. PSV, 2. Feyenoord, 3. Ajax, 4. AZ")
            st.markdown("#### **3. Veredito do Analista**")
            st.markdown("Com base nos dados, as seguintes equipes são selecionadas para monitoramento:")
            st.markdown("* **1. PSV Eindhoven**")
            st.markdown("* **2. Feyenoord**")
            st.markdown("* **3. Ajax**")

        # Limpa a memória para a próxima análise
        del st.session_state['texto_bruto_pronto']
        del st.session_state['contexto']

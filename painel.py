import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException
from PIL import Image
import pytesseract
import io
from datetime import datetime

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v5.0", page_icon="🧠", layout="wide")

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

    # --- CENTRAL DE COMANDO ---
    st.header("Central de Comando")
    acao_usuario = st.selectbox("O que deseja fazer?", ["Selecionar...", "Criar um Novo Dossiê", "Visualizar Dossiês Existentes"])

    if acao_usuario == "Criar um Novo Dossiê":
        tipo_dossie = st.selectbox("Qual dossiê deseja criar?", ["Selecionar...", "Dossiê 1: Análise Geral da Liga"])

        # --- FLUXO PARA DOSSIÊ 1 ---
        if tipo_dossie == "Dossiê 1: Análise Geral da Liga":
            with st.form("form_dossie_1"):
                st.subheader("Formulário do Dossiê 1: Análise Geral da Liga")
                st.write("Preencha os campos e envie os 'prints' necessários. O sistema só irá processar quando todos os campos obrigatórios forem preenchidos.")

                temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
                liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")

                st.markdown("---")

                # Campos de Upload Guiados
                prints_campeoes = st.file_uploader("1) Print(s) dos Últimos Campeões da Década*", accept_multiple_files=True, type=['png', 'jpg'])
                print_classificacao = st.file_uploader("2) Print(s) da Classificação Final da Última Temporada*", accept_multiple_files=True, type=['png', 'jpg'])
                prints_curiosidades = st.file_uploader("3) Print(s) de Curiosidades ou Estatísticas Gerais (Opcional)", accept_multiple_files=True, type=['png', 'jpg'])

                submitted = st.form_submit_button("Processar e Gerar Dossiê 1")

                if submitted:
                    if not all([temporada, liga, prints_campeoes, print_classificacao]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("Iniciando processo... AGENTE COORDENADOR ativado."):
                            # 1. Lógica de Upload
                            st.write("AGENTE DE COLETA: Enviando arquivos para o repositório...")
                            try:
                                temporada_fmt = temporada.replace('/', '-')
                                caminho_base = f"{temporada_fmt}/{liga.upper()}/GERAL/Dossie_1"

                                todos_os_prints = prints_campeoes + [print_classificacao] + prints_curiosidades
                                arquivos_subidos = []

                                for i, arq in enumerate(todos_os_prints):
                                    nome_padronizado = f"D1_Print_{i+1}_{arq.name}"
                                    caminho_repo = os.path.join(caminho_base, nome_padronizado)
                                    repo.create_file(caminho_repo, f"Upload Dossiê 1: {arq.name}", arq.getvalue())
                                    arquivos_subidos.append(caminho_repo)
                                st.success(f"{len(arquivos_subidos)} arquivos salvos com sucesso em `{caminho_base}`")
                            except Exception as e:
                                st.error("Ocorreu um erro durante o upload para o GitHub.")
                                st.exception(e)
                                st.stop()

                            # 2. Lógica de OCR e Análise
                            st.write("AGENTE ESTATÍSTICO: Extraindo texto dos arquivos com OCR...")
                            texto_bruto_completo = ""
                            try:
                                for i, arq_path in enumerate(arquivos_subidos):
                                    st.write(f"Lendo print {i+1}/{len(arquivos_subidos)}...")
                                    conteudo_img_obj = repo.get_contents(arq_path)
                                    conteudo_img = io.BytesIO(conteudo_img_obj.decoded_content)
                                    imagem = Image.open(conteudo_img)
                                    texto_bruto_completo += f"\n\n--- [INÍCIO DO PRINT: {os.path.basename(arq_path)}] ---\n"
                                    texto_bruto_completo += pytesseract.image_to_string(imagem, lang='por+eng')
                                    texto_bruto_completo += f"\n--- [FIM DO PRINT] ---\n"
                                st.success("Extração de texto concluída.")
                            except Exception as e:
                                st.error("Ocorreu um erro durante a análise OCR.")
                                st.exception(e)
                                st.stop()

                            # 3. Lógica de Geração do Dossiê
                            st.write("AGENTE REDATOR TÉCNICO: Gerando o dossiê estruturado...")
                            prompt = f"""
                            **PERSONA:** Você é um Analista de Dados de Futebol Sênior.
                            **CONTEXTO:** Liga: {liga.upper()}, Temporada de Referência: {temporada}
                            **DADOS BRUTOS:** {texto_bruto_completo}
                            **TAREFA:** Analise os dados brutos e gere um relatório em Markdown.
                            **MODELO DE SAÍDA:**
                            ---
                            ### **DOSSIÊ DE LIGA: {liga.upper()}**
                            **Temporada de Referência:** {temporada}
                            #### **1. Visão Histórica**
                            * **Principais Campeões:** [Liste as equipes e o número de títulos encontrados.]
                            #### **2. Análise da Última Temporada**
                            * **Campeão:** [Extraia o nome do campeão.]
                            * **Top 4:** [Liste as 4 primeiras equipes.]
                            #### **3. Veredito do Analista**
                            Com base nos dados, as seguintes equipes são selecionadas para monitoramento:
                            * **1. [Equipe 1]**
                            * **2. [Equipe 2]**
                            * **3. [Equipe 3]**
                            ---
                            """

                            # Simulação da resposta da IA
                            st.markdown("---")
                            st.header("Dossiê Gerado com Sucesso!")
                            st.markdown(f"### **DOSSIÊ DE LIGA: {liga.upper()}**")
                            st.markdown(f"**Temporada de Referência:** {temporada}")
                            st.markdown("#### **1. Visão Histórica**")
                            st.markdown("* **Principais Campeões (Simulação):** PSV (3), Ajax (3), Feyenoord (2)")
                            st.markdown("#### **2. Análise da Última Temporada**")
                            st.markdown("* **Campeão (Simulação):** PSV Eindhoven")
                            st.markdown("* **Top 4 (Simulação):** 1. PSV, 2. Feyenoord, 3. Ajax, 4. AZ")
                            st.markdown("#### **3. Veredito do Analista**")
                            st.markdown("Com base nos dados, as seguintes equipes são selecionadas para monitoramento:")
                            st.markdown("* **1. PSV Eindhoven**")
                            st.markdown("* **2. Feyenoord**")
                            st.markdown("* **3. Ajax**")
                            st.balloons()

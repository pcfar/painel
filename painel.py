import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException

# --- Configuração da Página ---
st.set_page_config(page_title="Painel Tático v5.4", page_icon="🧠", layout="wide")

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
    acao_usuario = st.selectbox("O que deseja fazer?", ["Selecionar...", "Criar um Novo Dossiê"])

    if acao_usuario == "Criar um Novo Dossiê":
        tipo_dossie = st.selectbox("Qual dossiê deseja criar?", ["Selecionar...", "Dossiê 1: Análise Geral da Liga", "Dossiê 2: Análise Aprofundada do Clube"])
        
        # --- FLUXO PARA DOSSIÊ 1 ---
        if tipo_dossie == "Dossiê 1: Análise Geral da Liga":
            # (Lógica do Dossiê 1 permanece aqui, omitida por brevidade)
            st.info("Formulário do Dossiê 1.")

        # --- FLUXO PARA DOSSIÊ 2 (AGORA COM LÓGICA COMPLETA) ---
        elif tipo_dossie == "Dossiê 2: Análise Aprofundada do Clube":
            with st.form("form_dossie_2"):
                st.subheader("Formulário do Dossiê 2: Análise Aprofundada do Clube")
                temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
                liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
                clube = st.text_input("Clube (código)*", placeholder="Ex: FEY")

                st.markdown("---")

                print_stats_gerais = st.file_uploader("1) Print da Visão Geral de Estatísticas do Clube (FBref)*", accept_multiple_files=False, type=['png', 'jpg'])
                print_elenco = st.file_uploader("2) Print dos Detalhes do Elenco (Transfermarkt/Sofascore)*", accept_multiple_files=False, type=['png', 'jpg'])
                prints_analise_tatica = st.file_uploader("3) Print(s) de Análises Táticas / Mapas de Calor (Opcional)", accept_multiple_files=True, type=['png', 'jpg'])

                if st.form_submit_button("Processar e Gerar Dossiê 2"):
                    if not all([temporada, liga, clube, print_stats_gerais, print_elenco]):
                        st.error("Por favor, preencha todos os campos obrigatórios (*).")
                    else:
                        with st.spinner("Iniciando processo completo do Dossiê 2..."):
                            # Juntar todos os arquivos numa lista
                            todos_os_prints = [print_stats_gerais, print_elenco] + (prints_analise_tatica or [])
                            
                            # 1. Lógica de Upload Inteligente
                            st.write("AGENTE DE COLETA: Verificando e salvando arquivos no GitHub...")
                            try:
                                temporada_fmt = temporada.replace('/', '-')
                                caminho_base = f"{temporada_fmt}/{liga.upper()}/{clube.upper()}/Dossie_2"
                                
                                for arq in todos_os_prints:
                                    conteudo_arquivo = arq.getvalue()
                                    caminho_repo = os.path.join(caminho_base, arq.name)
                                    commit_message = f"Upload Dossiê 2: {arq.name}"
                                    
                                    try:
                                        arquivo_existente = repo.get_contents(caminho_repo)
                                        repo.update_file(caminho_repo, commit_message, conteudo_arquivo, arquivo_existente.sha)
                                    except UnknownObjectException:
                                        repo.create_file(caminho_repo, commit_message, conteudo_arquivo)
                                st.success(f"Upload de {len(todos_os_prints)} arquivos concluído para `{caminho_base}`.")
                            except Exception as e:
                                st.error(f"Ocorreu um erro durante o upload: {e}")
                                st.stop()

                            # (As lógicas de OCR e Geração de Dossiê viriam aqui)
                            # Por enquanto, vamos mostrar uma simulação do dossiê final
                            st.markdown("---")
                            st.header("Dossiê Estratégico Gerado (Simulação)")
                            st.markdown(f"#### **ALVO: {clube.upper()}**")
                            st.markdown("**CAMADA 1: SUMÁRIO ESTRATÉGICO**")
                            st.info("""
                            > **Identidade Principal:** Equipe de alta posse de bola que busca controlar o jogo através de passes curtos.
                            > **Padrão Quantitativo Chave:** Maior número de passes no terço final do campo na liga.
                            > **Principal Fator Tático:** Pressão pós-perda agressiva para rápida recuperação da posse.
                            > **Principal Fator Contextual:** Chegada do novo treinador com ideias ofensivas.
                            > **Top 3 Cenários de Monitoramento In-Live:**
                            > 1.  Domínio territorial nos primeiros 20 minutos.
                            > 2.  Vulnerabilidade a contra-ataques rápidos.
                            > 3.  Aumento de volume ofensivo após os 60 minutos com substituições.
                            """)
                            st.balloons()

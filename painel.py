import streamlit as stimport osfrom github import Githubfrom github.GithubException import UnknownObjectExceptionfrom datetime import datetimeimport pytesseractfrom PIL import Imageimport io--- Configuração da Página ---st.set_page_config(page_title="Painel Tático v7.0", page_icon="🧠", layout="wide")--- SISTEMA DE SENHA ÚNICA ---def check_password():if st.session_state.get("password_correct", False): return Truedef password_entered():if st.session_state.get("password") == st.secrets.get("APP_PASSWORD"):st.session_state["password_correct"] = Truedel st.session_state["password"]else: st.session_state["password_correct"] = Falsest.text_input("Password", type="password", on_change=password_entered, key="password")if "password_correct" in st.session_state and not st.session_state["password_correct"]:st.error("😕 Senha incorreta.")return False--- APLICAÇÃO PRINCIPAL ---if check_password():st.sidebar.success("Autenticado com sucesso.")st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")# --- Conexão com o GitHub ---
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

# --- CENTRAL DE COMANDO COM ABAS ---
st.header("Central de Comando")

tab1, tab2, tab3, tab4 = st.tabs(["Dossiê 1 (Liga)", "Dossiê 2 (Clube)", "Dossiê 3 (Pós-Jogo)", "Dossiê 4 (Pré-Jogo)"])

with tab1:
    st.subheader("Criar Dossiê 1: Análise Geral da Liga (Modelo Híbrido)")
    with st.form("form_dossie_1_hibrido"):
        st.write("Forneça o contexto e os 'prints' com dados técnicos. A IA será responsável pela pesquisa de dados históricos e contextuais.")
        
        # Inputs de Contexto
        temporada = st.text_input("Temporada de Referência*", placeholder="Ex: 2024-2025")
        liga = st.text_input("Liga (código)*", placeholder="Ex: HOL")
        pais = st.text_input("País*", placeholder="Ex: Holanda")
        st.markdown("---")

        # Campos de Upload Guiados (agora apenas para dados técnicos)
        print_classificacao = st.file_uploader("1) Print da Tabela de Classificação Final*", help="Sugestão: No Sofascore ou FBref, capture a tabela de classificação completa da última temporada.", accept_multiple_files=True)
        print_stats = st.file_uploader("2) Print das Estatísticas Avançadas das Equipes*", help="Sugestão: No FBref, na página da temporada, capture a tabela 'Squad Advanced Stats'.", accept_multiple_files=True)
        
        if st.form_submit_button("Processar Prints e Preparar Prompt Híbrido para IA"):
            if not all([temporada, liga, pais, print_classificacao, print_stats]):
                st.error("Por favor, preencha todos os campos obrigatórios (*).")
            else:
                with st.spinner("AGENTE DE COLETA a processar 'prints' técnicos..."):
                    try:
                        # Agrupar e fazer OCR dos prints técnicos
                        grupos_de_prints = {
                            "TABELA DE CLASSIFICAÇÃO FINAL": print_classificacao,
                            "ESTATÍSTICAS AVANÇADAS": print_stats
                        }
                        texto_final_para_prompt = ""
                        for nome_grupo, prints in grupos_de_prints.items():
                            if prints:
                                texto_final_para_prompt += f"\n--- [INÍCIO DOS DADOS DO UTILIZADOR: {nome_grupo}] ---\n"
                                for print_file in prints:
                                    imagem = Image.open(print_file)
                                    texto_final_para_prompt += pytesseract.image_to_string(imagem, lang='por+eng') + "\n"
                                texto_final_para_prompt += f"--- [FIM DOS DADOS DO UTILIZADOR: {nome_grupo}] ---\n"

                        # Construir o Prompt Mestre Híbrido
                        data_hoje = datetime.now().strftime("%d/%m/%Y")
                        prompt_mestre = f"""
PERSONA: Você é um Analista de Futebol Sênior, com dupla especialidade: pesquisa de contexto histórico e análise de dados de performance.CONTEXTO:Liga para Análise: {liga.upper()}País: {pais}Temporada de Referência: {temporada}TAREFAS:Sua missão é gerar um Dossiê de Liga completo. Execute as seguintes tarefas em ordem:TAREFA 1 (Pesquisa Autónoma): Realize buscas na web para obter as informações necessárias para a "PARTE 1" do dossiê. Fontes prioritárias: Wikipedia, site oficial da liga, principais media desportivos do {pais}. Foque em encontrar:A lista de campeões da {liga.upper()} na última década.Curiosidades, recordes ou factos históricos relevantes sobre a liga.TAREFA 2 (Análise de Dados Fornecidos): Abaixo estão os dados brutos extraídos via OCR de "prints" fornecidos pelo utilizador. Use estes dados para realizar a "PARTE 2" do dossiê.{texto_final_para_prompt}TAREFA 3 (Consolidação): Junte os resultados das Tarefas 1 e 2 e preencha o "MODELO DE SAÍDA" abaixo de forma completa e estruturada.MODELO DE SAÍDA (Use esta estrutura Markdown):DOSSIÊ ESTRATÉGICO DE LIGA: {liga.upper()}TEMPORADA DE REFERÊNCIA PARA ANÁLISE: {temporada} DATA DA GERAÇÃO DO RELATÓRIO: {data_hoje}PARTE 1: VISÃO GERAL E HISTÓRICA DA LIGA (Dados da Pesquisa Autónoma)Dominância Histórica (Última Década): [Liste os campeões encontrados na sua pesquisa.]Fatos e Curiosidades Relevantes: [Resuma os factos interessantes encontrados na sua pesquisa.]PARTE 2: ANÁLISE TÉCNICA (Dados dos Prints do Utilizador)Panorama da Última Temporada: [Faça um breve resumo com base na tabela de classificação fornecida.]Identificação de Equipes Dominantes: [Com base na tabela E nas estatísticas avançadas fornecidas, liste as 3-4 equipes que se destacaram e justifique brevemente.]VEREDITO FINAL: PLAYLIST DE MONITORAMENTOAs seguintes equipes são selecionadas como alvos primários para monitoramento:1. [Nome da Equipe 1]2. [Nome da Equipe 2]3. [Nome da Equipe 3]"""st.session_state['prompt_gerado'] = prompt_mestreexcept Exception as e:st.error(f"Ocorreu um erro durante o OCR ou construção do prompt: {e}")    if 'prompt_gerado' in st.session_state:
        st.success("Processamento concluído. O 'Prompt Mestre Híbrido' está pronto.")
        st.info("Copie o prompt abaixo e envie para o seu assistente de IA para a geração final do dossiê.")
        st.text_area("Prompt Mestre para IA:", st.session_state['prompt_gerado'], height=400)
        if st.button("Limpar e Iniciar Nova Análise"):
            del st.session_state['prompt_gerado']
            st.rerun()

with tab2:
    st.info("Formulário para o Dossiê 2 em desenvolvimento.")
with tab3:
    st.info("Formulário para o Dossiê 3 em desenvolvimento.")
with tab4:
    st.info("Formulário para o Dossiê 4 em desenvolvimento.")

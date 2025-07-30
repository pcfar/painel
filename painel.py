import streamlit as st
import os
from github import Github
from github.GithubException import UnknownObjectException, GithubException--- Configuração da Página ---st.set_page_config(page_title="Painel Tático v5.2", page_icon="🧠", layout="wide")--- SISTEMA DE SENHA ÚNICA ---def check_password():
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
return False--- APLICAÇÃO PRINCIPAL ---if check_password():
st.sidebar.success("Autenticado com sucesso.")
st.title("SISTEMA DE INTELIGÊNCIA TÁTICA")# --- Conexão com o GitHub ---
@st.cache_resource
def get_github_connection():
    try:
        g = Github(st.secrets[&quot;GITHUB_TOKEN&quot;])
        repo = g.get_repo(&quot;pcfar/painel&quot;)
        return repo
    except Exception:
        st.error(&quot;Erro ao conectar com o GitHub.&quot;)
        st.stop()
repo = get_github_connection()

# --- CENTRAL DE COMANDO ---
st.header(&quot;Central de Comando&quot;)
acao_usuario = st.selectbox(&quot;O que deseja fazer?&quot;, [&quot;Selecionar...&quot;, &quot;Criar um Novo Dossiê&quot;])

if acao_usuario == &quot;Criar um Novo Dossiê&quot;:
    tipo_dossie = st.selectbox(&quot;Qual dossiê deseja criar?&quot;, [&quot;Selecionar...&quot;, &quot;Dossiê 1: Análise Geral da Liga&quot;])
    
    if tipo_dossie == &quot;Dossiê 1: Análise Geral da Liga&quot;:
        with st.form(&quot;form_dossie_1&quot;):
            st.subheader(&quot;Formulário do Dossiê 1: Análise Geral da Liga&quot;)
            temporada = st.text_input(&quot;Temporada de Referência*&quot;, placeholder=&quot;Ex: 2024-2025&quot;)
            liga = st.text_input(&quot;Liga (código)*&quot;, placeholder=&quot;Ex: HOL&quot;)
            
            prints_campeoes = st.file_uploader(&quot;1) Print(s) dos Últimos Campeões da Década*&quot;, accept_multiple_files=True, type=[&#39;png&#39;, &#39;jpg&#39;])
            prints_classificacao = st.file_uploader(&quot;2) Print(s) da Classificação Final da Última Temporada*&quot;, accept_multiple_files=True, type=[&#39;png&#39;, &#39;jpg&#39;])
            prints_curiosidades = st.file_uploader(&quot;3) Print(s) de Curiosidades (Opcional)&quot;, accept_multiple_files=True, type=[&#39;png&#39;, &#39;jpg&#39;])
            
            submitted = st.form_submit_button(&quot;Processar e Gerar Dossiê 1&quot;)

            if submitted:
                todos_os_prints = []
                if prints_campeoes: todos_os_prints.extend(prints_campeoes)
                if prints_classificacao: todos_os_prints.extend(prints_classificacao)
                if prints_curiosidades: todos_os_prints.extend(prints_curiosidades)

                if not all([temporada, liga, todos_os_prints]):
                    st.error(&quot;Por favor, preencha todos os campos obrigatórios (*).&quot;)
                else:
                    with st.spinner(&quot;Iniciando processo... AGENTE DE COLETA ativado.&quot;):
                        try:
                            temporada_fmt = temporada.replace(&#39;/&#39;, &#39;-&#39;)
                            caminho_base = f&quot;{temporada_fmt}/{liga.upper()}/GERAL/Dossie_1&quot;
                            
                            for arq in todos_os_prints:
                                conteudo_arquivo = arq.getvalue()
                                caminho_repo = os.path.join(caminho_base, arq.name)
                                commit_message = f&quot;Upload/Update Dossiê 1: {arq.name}&quot;

                                # --- LÓGICA DE UPLOAD INTELIGENTE ---
                                try:
                                    # Tenta obter o arquivo para ver se ele já existe
                                    arquivo_existente = repo.get_contents(caminho_repo)
                                    # Se existir, atualiza
                                    repo.update_file(caminho_repo, commit_message, conteudo_arquivo, arquivo_existente.sha)
                                    st.info(f&quot;Arquivo `{arq.name}` atualizado com sucesso!&quot;)
                                except UnknownObjectException:
                                    # Se não existir, cria
                                    repo.create_file(caminho_repo, commit_message, conteudo_arquivo)
                                    st.success(f&quot;Arquivo `{arq.name}` criado com sucesso!&quot;)
                            
                            st.balloons()
                            st.header(&quot;Upload Concluído!&quot;)

                        except GithubException as e:
                            st.error(f&quot;Ocorreu um erro na API do GitHub: {e.data[&#39;message&#39;]}&quot;)
                        except Exception as e:
                            st.error(f&quot;Ocorreu um erro inesperado durante o upload: {e}&quot;)
                            st.stop()

import streamlit as st
import os
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="🗂️", layout="wide")

# Função para aplicar o CSS avançado
def apply_custom_styling():
    """Aplica CSS personalizado para uma visualização de dossiê moderna e atraente."""
    st.markdown("""
        <style>
            /* Importa a fonte Inter do Google Fonts */
            @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');

            .dossier-viewer {
                font-family: 'Inter', sans-serif;
                line-height: 1.7;
                color: #d1d5db;
            }
            .dossier-viewer h1 {
                font-size: 2.5rem; font-weight: 700; color: #ffffff;
                border-bottom: 2px solid #4f46e5; padding-bottom: 0.5rem; margin-bottom: 1.5rem;
            }
            .dossier-viewer blockquote {
                border-left: 4px solid #6366f1; padding: 1rem 1.5rem; margin-left: 0;
                font-style: italic; color: #e5e7eb; background-color: rgba(49, 46, 129, 0.2);
                border-radius: 0.5rem;
            }
            .dossier-viewer h3 {
                font-size: 1.75rem; font-weight: 600; color: #f9fafb;
                margin-top: 3rem; margin-bottom: 1.5rem; border-bottom: 1px solid #4b5563;
                padding-bottom: 0.5rem;
            }
            .dossier-viewer h3::before { content: '📂 '; }
            .dossier-viewer h4 {
                font-size: 1.25rem; font-weight: 600; color: #e5e7eb;
                margin-top: 2rem; margin-bottom: 1rem;
            }
            .dossier-viewer strong { color: #a5b4fc; }
            /* --- NOVO: Estilo para Tabelas --- */
            .dossier-viewer table {
                width: 100%; border-collapse: collapse; margin-top: 1.5rem; margin-bottom: 1.5rem;
            }
            .dossier-viewer th, .dossier-viewer td {
                padding: 0.75rem 1rem; text-align: left; border-bottom: 1px solid #374151;
            }
            .dossier-viewer th {
                background-color: #1f2937; color: #e5e7eb; font-weight: 600;
            }
            .dossier-viewer tr:nth-child(even) {
                background-color: #111827;
            }
            .dossier-viewer tr:hover {
                background-color: #374151;
            }
        </style>
    """, unsafe_allow_html=True)

# --- 2. AUTENTICAÇÃO E CONEXÃO COM GITHUB ---
def check_password():
    """Verifica se a senha do usuário está correta. Usa st.secrets."""
    if "password_correct" in st.session_state and st.session_state["password_correct"]:
        return True

    # Layout para centralizar o campo de senha
    col1, col2, col3 = st.columns([1,2,1])
    with col2:
        st.title("🔐 Painel de Inteligência")
        st.write("Por favor, insira a senha para acessar o sistema.")
        password = st.text_input("Senha", type="password", key="password_input")
        if st.button("Acessar"):
            if password == st.secrets.get("APP_PASSWORD"):
                st.session_state["password_correct"] = True
                st.rerun()
            else:
                st.error("😕 Senha incorreta.")
    return False

@st.cache_resource
def get_github_repo():
    """Conecta-se ao repositório do GitHub usando as secrets."""
    try:
        if not all(k in st.secrets for k in ["GITHUB_TOKEN", "GITHUB_USERNAME", "GITHUB_REPO_NAME"]):
            st.error("Secrets do GitHub (TOKEN, USERNAME, REPO_NAME) não configuradas.")
            return None
        g = Github(st.secrets["GITHUB_TOKEN"])
        repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"
        return g.get_repo(repo_name)
    except Exception as e:
        st.error(f"Erro ao conectar com o GitHub: {e}")
        return None

# --- 3. FUNÇÕES DE GERENCIAMENTO DE ARQUIVOS (LÓGICA PRINCIPAL) ---

def parse_path_to_form(path):
    """Analisa o caminho do arquivo para preencher o formulário de edição."""
    parts = path.split('/')
    try:
        st.session_state.pais = parts[0].replace("_", " ")
        st.session_state.liga = parts[1].replace("_", " ")
        st.session_state.temporada = parts[2]
        
        # Lógica para diferenciar os tipos de dossiê
        if "Dossiê_Clube.md" in path and len(parts) == 4:
            st.session_state.tipo_dossie = "Dossiê de Clube"
            st.session_state.clube = parts[3].replace("_", " ")
        elif "Dossiê_Liga.md" in path:
            st.session_state.tipo_dossie = "Dossiê de Liga"
        elif "Briefing_Pre-Jogo.md" in path or "Relatorio_Pos-Jogo.md" in path:
            st.session_state.tipo_dossie = "Briefing Pré-Jogo" if "Briefing" in path else "Relatório Pós-Jogo"
            st.session_state.clube = parts[3].replace("_", " ")
            st.session_state.rodada = parts[4].replace("_", " ")
    except IndexError:
        st.warning("Não foi possível extrair todos os dados do caminho do arquivo. Preencha manualmente.")

def display_repo_contents(repo, path="", search_term=""):
    """Exibe o conteúdo do repositório com busca, edição e exclusão."""
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([c for c in contents if c.type == 'file'], key=lambda x: x.name)

        # Filtra arquivos e diretórios com base na busca
        if search_term:
            files = [f for f in files if search_term.lower() in f.name.lower()]
            # Não filtramos diretórios para permitir a navegação completa

        for content in dirs:
            with st.expander(f"📁 {content.name}"):
                display_repo_contents(repo, content.path, search_term)

        for content in files:
            if content.name.endswith(".md"):
                col1, col2, col3 = st.columns([3, 1, 1])
                with col1:
                    if st.button(f"📄 {content.name}", key=f"view_{content.path}", use_container_width=True):
                        st.session_state.viewing_file_content = base64.b64decode(content.content).decode('utf-8')
                        st.session_state.viewing_file_name = content.name
                        # Limpa o estado de exclusão ao visualizar outro arquivo
                        if 'file_to_delete' in st.session_state:
                            del st.session_state['file_to_delete']

                with col2:
                    if st.button("✏️", key=f"edit_{content.path}", help="Editar este arquivo"):
                        # Prepara para o modo de edição
                        st.session_state.edit_mode = True
                        st.session_state.file_to_edit_path = content.path
                        st.session_state.conteudo_md = base64.b64decode(content.content).decode('utf-8')
                        parse_path_to_form(content.path)
                        st.success(f"Modo de edição ativado para {content.name}. Verifique o formulário.")
                        st.rerun()

                with col3:
                    if st.button("🗑️", key=f"delete_{content.path}", help="Excluir este arquivo"):
                         st.session_state['file_to_delete'] = {'path': content.path, 'sha': content.sha}

                # Lógica de confirmação de exclusão
                if st.session_state.get('file_to_delete', {}).get('path') == content.path:
                    st.warning(f"**Você tem certeza que quer excluir `{content.path}`?** Esta ação não pode ser desfeita.")
                    c1, c2, c3 = st.columns([2,2,3])
                    with c1:
                        if st.button("Sim, excluir!", key=f"confirm_delete_{content.path}", type="primary"):
                            try:
                                file_info = st.session_state['file_to_delete']
                                repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                                st.success(f"Arquivo '{file_info['path']}' excluído com sucesso.")
                                del st.session_state['file_to_delete']
                                # Limpa visualização se o arquivo excluído estava sendo visto
                                if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']):
                                    del st.session_state['viewing_file_content']
                                    del st.session_state['viewing_file_name']
                                st.rerun()
                            except Exception as e:
                                st.error(f"Erro ao excluir: {e}")
                    with c2:
                        if st.button("Cancelar", key=f"cancel_delete_{content.path}"):
                            del st.session_state['file_to_delete']
                            st.rerun()

    except UnknownObjectException:
        st.info("Este diretório está vazio ou o repositório não foi encontrado.")
    except Exception as e:
        st.error(f"Erro ao listar conteúdo: {e}")


# --- 4. APLICAÇÃO PRINCIPAL ---

if not check_password():
    st.stop()

# Uma vez autenticado, executa o resto da aplicação
apply_custom_styling()
st.sidebar.success("Autenticado com sucesso.")
st.title("🗂️ Sistema de Inteligência Tática")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Dossiê Liga", "Dossiê Clube", "Pós-Jogo", "Pré-Jogo", "ARQUIVO CENTRAL"])

# Placeholder para as outras abas
with tab1: st.info("Funcionalidade de geração do Dossiê de Liga.")
with tab2: st.info("Funcionalidade de geração do Dossiê de Clube.")
with tab3: st.info("Funcionalidade de geração do Dossiê Pós-Jogo.")
with tab4: st.info("Funcionalidade de geração do Dossiê Pré-Jogo.")

# --- ABA 5: ARQUIVO CENTRAL (FUNCIONALIDADE PRINCIPAL) ---
with tab5:
    st.header("Painel de Arquivo de Inteligência")
    
    repo = get_github_repo()
    if repo:
        col1, col2 = st.columns([1, 2]) # Define as colunas principais

        with col1: # Coluna da Esquerda: Ações
            
            # Módulo de Upload/Edição dentro de um expander
            is_edit_mode = st.session_state.get('edit_mode', False)
            expander_label = "✏️ Editando Dossiê" if is_edit_mode else "📤 Adicionar Novo Dossiê"
            
            with st.expander(expander_label, expanded=is_edit_mode):
                form_key = "form_edit" if is_edit_mode else "form_add"
                with st.form(form_key, clear_on_submit=True):
                    
                    st.selectbox("Tipo de Dossiê*", ["Dossiê de Liga", "Dossiê de Clube", "Briefing Pré-Jogo", "Relatório Pós-Jogo"], key="tipo_dossie")
                    st.text_input("País*", placeholder="Ex: Brasil", key="pais")
                    st.text_input("Liga*", placeholder="Ex: Serie A", key="liga")
                    st.text_input("Temporada*", placeholder="Ex: 2025", key="temporada")
                    st.text_input("Clube (se aplicável)", placeholder="Ex: Flamengo", key="clube")
                    st.text_input("Rodada / Adversário (se aplicável)", placeholder="Ex: Rodada_01_vs_Palmeiras", key="rodada")
                    st.text_area("Conteúdo Markdown*", height=250, placeholder="Cole aqui o dossiê completo...", key="conteudo_md")

                    submit_label = "Atualizar Dossiê" if is_edit_mode else "Salvar Novo Dossiê"
                    if st.form_submit_button(submit_label, type="primary"):
                        # Validar campos obrigatórios
                        if not all([st.session_state.pais, st.session_state.liga, st.session_state.temporada, st.session_state.conteudo_md]):
                            st.error("Campos com * são obrigatórios.")
                        else:
                            # Construir caminho do arquivo
                            path_parts = [st.session_state.pais.replace(" ", "_"), st.session_state.liga.replace(" ", "_"), st.session_state.temporada]
                            file_name = ""
                            tipo = st.session_state.tipo_dossie
                            
                            if tipo == "Dossiê de Liga": file_name = "Dossiê_Liga.md"
                            elif tipo == "Dossiê de Clube":
                                if not st.session_state.clube: st.error("O campo 'Clube' é obrigatório.")
                                else:
                                    path_parts.append(st.session_state.clube.replace(" ", "_"))
                                    file_name = "Dossiê_Clube.md"
                            elif tipo in ["Briefing Pré-Jogo", "Relatório Pós-Jogo"]:
                                if not st.session_state.clube or not st.session_state.rodada: st.error("Os campos 'Clube' e 'Rodada / Adversário' são obrigatórios.")
                                else:
                                    path_parts.append(st.session_state.clube.replace(" ", "_"))
                                    path_parts.append(st.session_state.rodada.replace(" ", "_"))
                                    file_name = "Briefing_Pre-Jogo.md" if tipo == "Briefing Pré-Jogo" else "Relatorio_Pos-Jogo.md"
                            
                            if file_name:
                                full_path = "/".join(path_parts) + "/" + file_name
                                content_bytes = st.session_state.conteudo_md.encode('utf-8')
                                commit_message = f"Atualiza dossiê via painel: {file_name}" if is_edit_mode else f"Adiciona dossiê via painel: {file_name}"
                                
                                with st.spinner(f"Processando '{full_path}' no GitHub..."):
                                    try:
                                        if is_edit_mode:
                                            # Lógica de atualização
                                            original_path = st.session_state.file_to_edit_path
                                            existing_file = repo.get_contents(original_path)
                                            repo.update_file(original_path, commit_message, st.session_state.conteudo_md, existing_file.sha)
                                            st.success(f"Dossiê '{original_path}' atualizado com sucesso!")
                                        else:
                                            # Lógica de criação (verifica se já existe para evitar erro)
                                            try:
                                                existing_file = repo.get_contents(full_path)
                                                st.error(f"Erro: O arquivo '{full_path}' já existe. Use o modo de edição.")
                                            except UnknownObjectException:
                                                repo.create_file(full_path, commit_message, st.session_state.conteudo_md)
                                                st.success(f"Dossiê '{full_path}' salvo com sucesso!")
                                    
                                    except Exception as e:
                                        st.error(f"Ocorreu um erro: {e}")
                                
                                # Limpa o modo de edição após a submissão
                                if 'edit_mode' in st.session_state:
                                    del st.session_state['edit_mode']
                                if 'file_to_edit_path' in st.session_state:
                                    del st.session_state['file_to_edit_path']
                                st.rerun()

            # Botão para sair do modo de edição manualmente
            if is_edit_mode:
                if st.button("Cancelar Edição"):
                    st.session_state.edit_mode = False
                    if 'file_to_edit_path' in st.session_state:
                        del st.session_state['file_to_edit_path']
                    # Limpa os campos do formulário
                    keys_to_clear = ['pais', 'liga', 'temporada', 'clube', 'rodada', 'conteudo_md']
                    for key in keys_to_clear:
                        if key in st.session_state:
                            del st.session_state[key]
                    st.rerun()

            # Módulo do Navegador de Arquivos dentro de outro expander
            with st.expander("📂 Navegador do Repositório", expanded=not is_edit_mode):
                search_term = st.text_input("🔎 Filtrar por nome do arquivo...", key="search_term")
                st.divider()
                display_repo_contents(repo, search_term=search_term)

        with col2: # Coluna da Direita: Visualizador
            st.subheader("Visualizador de Dossiês")
            if "viewing_file_content" in st.session_state:
                st.markdown(f"#### {st.session_state.viewing_file_name}")
                st.divider()
                
                cleaned_content = re.sub(r':contentReference\[.*?\]\{.*?\}', '', st.session_state.viewing_file_content)
                html_content = f"<div class='dossier-viewer'>{cleaned_content}</div>"
                st.markdown(html_content, unsafe_allow_html=True)
            else:
                st.info("Selecione um arquivo no navegador à esquerda para visualizá-lo aqui.")
    else:
        st.warning("A conexão com o GitHub não foi estabelecida. Verifique as suas secrets.")

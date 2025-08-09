# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v18.2: Teste do Novo Modelo Visual D1P1
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import os
from streamlit_option_menu import option_menu
import markdown2

# --- 1. CONFIGURAÇÃO E FUNÇÕES AUXILIARES ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

# Mantém a estilização original do painel
def apply_custom_styling():
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

@st.cache_resource
def get_github_repo():
    try:
        g = Github(st.secrets["GITHUB_TOKEN"])
        return g.get_repo(f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}")
    except Exception as e:
        st.error(f"Falha na conexão com o GitHub: {e}")
        return None

def check_password():
    if st.session_state.get("password_correct", False): return True
    _, center_col, _ = st.columns([1, 1, 1])
    with center_col:
        st.title("Painel de Inteligência")
        st.write(" ")
        with st.container(border=True):
            st.subheader("Login de Acesso")
            password = st.text_input("Senha de Acesso", type="password", key="password_input", label_visibility="collapsed", placeholder="Digite sua senha")
            if st.button("Acessar Painel", type="primary", use_container_width=True):
                with st.spinner("Verificando..."):
                    if password == st.secrets.get("APP_PASSWORD"):
                        st.session_state["password_correct"] = True
                        st.rerun()
                    else:
                        st.error("Senha incorreta.")
    return False

def display_repo_structure(repo, path=""):
    try:
        contents = repo.get_contents(path)
        dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name)
        files = sorted([f for f in contents if f.name.endswith(".md")], key=lambda x: x.name)
        
        search_term = st.session_state.get("search_term", "")
        if search_term:
            files = [f for f in files if search_term.lower() in f.name.lower()]

        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"):
                display_repo_structure(repo, content_dir.path)
        
        for content_file in files:
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15])
            with col1:
                if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8")
                    st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
            with col2:
                if st.button("✏️", key=f"edit_{content_file.path}", help="Editar Dossiê"):
                    st.warning("Função de edição em desenvolvimento.")
            with col3:
                if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir Dossiê"):
                    st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}
                    st.rerun()
            
            if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                st.warning(f"Excluir `{content_file.path}`?")
                btn_c1, btn_c2 = st.columns(2)
                if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                    file_info = st.session_state.pop('file_to_delete')
                    repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                    if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']):
                        st.session_state.pop('viewing_file_content', None)
                        st.session_state.pop('viewing_file_name', None)
                    st.success(f"Arquivo '{file_info['path']}' excluído.")
                    st.rerun()
                if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"):
                    st.session_state.pop('file_to_delete')
                    st.rerun()
    except Exception as e:
        st.error(f"Erro ao listar arquivos: {e}")

def save_dossier(repo, file_name_template: str, path_parts: list, content: str, required_fields: dict):
    if not all(required_fields.values()):
        st.error("Todos os campos marcados com * são obrigatórios.")
        return
    
    format_dict = {k: v.replace(' ', '_') for k, v in required_fields.items()}
    file_name = file_name_template.format(**format_dict) + ".md"
    
    final_path_parts = [p.replace(" ", "_") for p in path_parts]
    full_path = "/".join(final_path_parts) + "/" + file_name
    commit_message = f"Adiciona: {file_name}"

    with st.spinner("Salvando dossiê..."):
        try:
            repo.create_file(full_path, commit_message, content)
            st.success(f"Dossiê '{full_path}' salvo com sucesso!")
        except Exception as e:
            st.error(f"Ocorreu um erro ao salvar: {e}")
            st.info("Verifique se um arquivo com este nome já não existe.")

# --- NOVO MODELO VISUAL PARA D1P1 ---
D1P1_VISUAL_MODEL = """
<style>
    /* Estilos específicos para este template, não afetam o resto do painel */
    .dossier-wrapper-light-theme {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #f8f9fa;
        color: #333;
        margin: 0;
        padding: 0;
    }
    .dossier-wrapper-light-theme header {
        background: linear-gradient(90deg, #004080, #0073e6);
        color: white;
        padding: 20px;
        text-align: center;
        border-bottom: 4px solid #003366;
    }
    .dossier-wrapper-light-theme header h1 { margin: 0; font-size: 28px; }
    .dossier-wrapper-light-theme header p { margin: 5px 0 0; font-size: 16px; opacity: 0.9; }
    .dossier-wrapper-light-theme main { max-width: 900px; margin: 30px auto; padding: 20px; background: white; border-radius: 12px; box-shadow: 0px 4px 15px rgba(0,0,0,0.1); }
    .dossier-wrapper-light-theme h2 { border-left: 6px solid #0073e6; padding-left: 10px; margin-top: 30px; color: #004080; }
    .dossier-wrapper-light-theme table { width: 100%; border-collapse: collapse; margin-top: 15px; }
    .dossier-wrapper-light-theme table th, .dossier-wrapper-light-theme table td { padding: 10px; border-bottom: 1px solid #ddd; text-align: left; }
    .dossier-wrapper-light-theme table th { background-color: #f1f5f9; color: #004080; font-weight: bold; }
    .dossier-wrapper-light-theme table tr:hover { background-color: #f9fafb; }
    .dossier-wrapper-light-theme .highlight { background-color: #e6f0ff; font-weight: bold; }
    .dossier-wrapper-light-theme footer { text-align: center; font-size: 14px; padding: 20px; color: #777; }
</style>

<div class="dossier-wrapper-light-theme">
    <header>
        <h1>📊 Dossiê de Liga – Superliga da Dinamarca</h1>
        <p>Um mergulho quantitativo na competitividade da elite do futebol dinamarquês (última década)</p>
    </header>
    <main>
        <h2>Placar de Dominância (Últimas 10 Temporadas)</h2>
        <table>
            <tr><th>Posição</th><th>Equipe</th><th>Pontuação Total</th></tr>
            <tr class="highlight"><td>1</td><td>FC Copenhagen</td><td>256</td></tr>
            <tr><td>2</td><td>FC Midtjylland</td><td>198</td></tr>
            <tr><td>3</td><td>Brøndby IF</td><td>165</td></tr>
            <tr><td>4</td><td>AGF Aarhus</td><td>122</td></tr>
            <tr><td>5</td><td>Randers FC</td><td>95</td></tr>
        </table>
        <h2>Análise Resumida</h2>
        <p>O <strong>FC Copenhagen</strong> consolidou-se como a força dominante na Dinamarca, liderando com ampla vantagem sobre seus concorrentes. A disputa pelo segundo lugar é mais equilibrada, com o <em>Midtjylland</em> mantendo constância, enquanto o <em>Brøndby</em> alterna boas temporadas.</p>
    </main>
    <footer>Painel de Inteligência – Dados de fontes oficiais | Última atualização: Agosto/2025</footer>
</div>
"""

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---
if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês")
    default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index, key="main_menu")
    st.session_state.selected_action = selected_action

st.title("Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório")
            st.text_input("Filtrar...", label_visibility="collapsed", placeholder="Filtrar por nome do arquivo...", key="search_term")
            st.divider()
            display_repo_structure(repo, search_term=st.session_state.get("search_term", ""))
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_name"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}")
                st.divider()

                # --- LÓGICA DE TESTE DO NOVO MODELO ---
                if file_name.startswith("D1P1_"):
                    # Renderiza o novo modelo visual que você forneceu
                    st.markdown(D1P1_VISUAL_MODEL, unsafe_allow_html=True)
                else:
                    # Para outros arquivos, mostra um aviso
                    st.info(f"Visualizador padrão para {file_name}.")
                    st.text(st.session_state.get("viewing_file_content", ""))
            else:
                st.info("Selecione um dossiê para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê")
    st.info("Selecione o tipo de dossiê, preencha as informações e o conteúdo em Markdown.")
    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes da Liga", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")
    help_text_md = "Guia Rápido de Formatação:\n- Título: # Título\n- Subtítulo: ## Subtítulo\n- Destaque: **texto**"
    
    if dossier_type == "D1 P1 - Análise da Liga":
        with st.form("d1_p1_form", clear_on_submit=True):
            st.subheader("Template: Análise da Liga")
            c1, c2, c3 = st.columns(3)
            pais = c1.text_input("País*")
            liga = c2.text_input("Liga*")
            temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Resumo (Conteúdo do Dossiê)*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"):
                save_dossier(repo, "D1P1_Analise_Liga_{liga}_{pais}", [pais, liga, temporada], conteudo, {"liga": liga, "pais": pais, "temporada": temporada, "conteudo": conteudo})
    
    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

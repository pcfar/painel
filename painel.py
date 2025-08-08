# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v15.3: Implementação do Template "Dark Pro"
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO E ESTILOS FINAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    # CSS agora inclui as classes do novo template "Dark Pro"
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;700&display=swap');

            html, body, [class*="css"]  {
                font-family: 'Roboto', sans-serif;
                background-color: #0F172A;
                color: #E2E8F0;
            }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }

            /* --- ESTILOS PARA O NOVO TEMPLATE "DARK PRO" --- */
            .report-container { padding: 1rem; }
            .report-title { font-size: 2.3rem; font-weight: 700; color: #FACC15; margin-bottom: 0.5rem; }
            .report-sub { font-size: 1rem; color: #94A3B8; margin-bottom: 2rem; }
            .section { background: rgba(255, 255, 255, 0.05); padding: 1.2rem; margin-bottom: 1rem; border-radius: 12px; border: 1px solid rgba(255,255,255,0.1); box-shadow: 0 4px 20px rgba(0,0,0,0.4); }
            .section h2 { font-size: 1.4rem; color: #38BDF8; margin-bottom: 1rem; }
            .section h3 { font-size: 1.1rem; color: #FACC15; margin-top: 1rem; margin-bottom: 0.5rem;}
            .section ul { list-style-position: inside; padding-left: 10px; }
            .section li { margin-bottom: 0.5rem; line-height: 1.6; }
            .section hr { border: none; border-top: 1px solid rgba(255,255,255,0.1); margin: 1.5rem 0; }
            .section table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 1rem; }
            .section th, .section td { border: 1px solid #4A5568; padding: 10px; text-align: left; }
            .section th { background-color: #1E293B; color: #94A3B8; }

            /* Outros estilos de componentes do painel */
            .stButton>button { border-radius: 8px; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADORES E FUNÇÕES AUXILIARES ---
def render_dark_pro_liga_dossier(data: dict):
    """Renderizador específico que usa o novo template 'Dark Pro'."""
    
    # Processa sub-listas aninhadas
    def process_list_items(items):
        html = "<ul>"
        for item in items:
            if isinstance(item, dict):
                for key, sub_items in item.items():
                    html += f"<li>{key}<ul>"
                    html += "".join([f"<li>{sub_item}</li>" for sub_item in sub_items])
                    html += "</ul></li>"
            else:
                html += f"<li>{item}</li>"
        html += "</ul>"
        return html
    
    # Constrói o HTML para cada seção
    sections_html = ""
    for secao in data.get('secoes', []):
        sections_html += f"<div class='section'><h2>{secao.get('titulo_secao', '')}</h2>"
        for sub in secao.get('subsecoes', []):
            sections_html += f"<h3>{sub.get('titulo_sub', '')}</h3>"
            if 'conteudo' in sub: sections_html += process_list_items(sub['conteudo'])
            if 'tabela' in sub:
                sections_html += "<table>"
                headers = sub['tabela'].get('cabecalho', [])
                sections_html += "<tr>" + "".join([f"<th>{h}</th>" for h in headers]) + "</tr>"
                for row in sub['tabela'].get('linhas', []):
                    sections_html += "<tr>" + "".join([f"<td>{cell}</td>" for cell in row]) + "</tr>"
                sections_html += "</table>"
        sections_html += "</div>"

    # Monta o HTML final
    dossier_html = f"""
    <div class="report-container">
        <div class='report-title'>{data.get('titulo_geral', '')}</div>
        <div class='report-sub'>📅 Atualizado em: {data.get('data_atualizacao', 'N/D')}</div>
        {sections_html}
    </div>
    """
    st.markdown(dossier_html, unsafe_allow_html=True)

# (O restante das funções auxiliares como get_github_repo, check_password, etc. permanecem as mesmas)
@st.cache_resource
def get_github_repo():
    # ...
    pass
def check_password():
    # ...
    pass
def display_repo_structure(repo, path="", search_term=""):
    # ...
    pass

# --- CÓDIGO PRINCIPAL COMPLETO E FUNCIONAL ---
# (Colando o código completo abaixo para garantir)

@st.cache_resource
def get_github_repo_full():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password_full():
    if st.session_state.get("password_correct", False): return True
    _, center_col, _ = st.columns([1, 1, 1]);
    with center_col:
        st.title("Painel de Inteligência"); st.write(" ")
        with st.container(border=True):
            st.subheader("Login de Acesso"); password = st.text_input("Senha de Acesso", type="password", key="password_input", label_visibility="collapsed", placeholder="Digite sua senha")
            if st.button("Acessar Painel", type="primary", use_container_width=True):
                with st.spinner("Verificando..."):
                    if password == st.secrets.get("APP_PASSWORD"): st.session_state["password_correct"] = True; st.rerun()
                    else: st.error("Senha incorreta.")
    return False
def display_repo_structure_full(repo, path=""):
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".yml")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure_full(repo, content_dir.path)
        for content_file in files:
            col1, col2, col3 = st.columns([0.7, 0.15, 0.15]) 
            with col1:
                if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                    file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
            with col2:
                if st.button("✏️", key=f"edit_{content_file.path}", help="Editar Dossiê", use_container_width=True): st.warning("Edição em desenvolvimento.")
            with col3:
                if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir Dossiê", use_container_width=True): st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
            if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                st.warning(f"Excluir `{content_file.path}`?"); btn_c1, btn_c2 = st.columns(2)
                if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                    file_info = st.session_state.pop('file_to_delete'); repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                    if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content', None); st.session_state.pop('viewing_file_name', None)
                    st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
    except Exception as e: st.error(f"Erro ao listar arquivos: {e}")

if not check_password_full(): st.stop()
apply_custom_styling()
repo = get_github_repo_full()

with st.sidebar:
    st.info(f"Autenticado. {datetime.now(tz=datetime.now().astimezone().tzinfo).strftime('%d/%m/%Y %H:%M')}")
    default_action = st.session_state.get("selected_action", "Leitor de Dossiês"); default_index = ["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"].index(default_action)
    selected_action = option_menu(menu_title="Menu Principal", options=["Leitor de Dossiês", "Carregar Dossiê", "Gerar com IA"], icons=["book-half", "cloud-arrow-up-fill", "cpu-fill"], menu_icon="collection-play", default_index=default_index, key="main_menu")
    st.session_state.selected_action = selected_action

st.title("Sistema de Inteligência Tática")

if selected_action == "Leitor de Dossiês":
    st.header("📖 Leitor de Dossiês"); st.text("Navegue e visualize os dossiês salvos no repositório.")
    if repo:
        col1, col2 = st.columns([1, 2], gap="large")
        with col1:
            st.subheader("Navegador do Repositório"); st.text_input("Filtrar...", label_visibility="collapsed", placeholder="Filtrar por nome do arquivo...", key="search_term"); st.divider()
            display_repo_structure_full(repo, search_term=st.session_state.search_term)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}"); st.divider()
                try:
                    dossier_data = yaml.safe_load(st.session_state.viewing_file_content)
                    if isinstance(dossier_data, dict):
                        if dossier_data.get("template_type") == "liga_dark_pro":
                            render_dark_pro_liga_dossier(dossier_data)
                        else: st.warning("Template desconhecido."); st.json(dossier_data)
                    else: st.warning("⚠️ Formato Inesperado"); st.code(st.session_state.viewing_file_content, language="yaml")
                except yaml.YAMLError: st.error("⚠️ Formato de Arquivo Inválido"); st.code(st.session_state.viewing_file_content, language="text")
            else: st.info("Selecione um dossiê para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê"); st.info("Selecione o tipo de dossiê para ver os campos específicos.")
    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes da Liga"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")

    if dossier_type == "D1 P1 - Análise da Liga":
        st.subheader("Template: Análise da Liga (Modelo Dark Pro)")
        with st.form("d1_p1_form", clear_on_submit=True):
            st.write("**Metadados**"); c1, c2, c3 = st.columns(3); pais = c1.text_input("País*"); liga = c2.text_input("Liga*"); temporada = c3.text_input("Temporada*")
            data_atualizacao = st.text_input("Data de Atualização*", value=datetime.now().strftime("%d de %B de %Y"))
            st.divider()
            st.write("**Seções de Conteúdo**"); help_text = "Para sub-itens, use dois espaços no início da linha. Para tabelas, separe colunas com ';'. Ex: Posição;Competição"
            
            secao1_titulo = st.text_input("Título da Seção 1", "⚽ Estrutura e Identidade da Liga")
            secao1_sub1_titulo = st.text_input("Título do Subitem 1.1", "📋 Visão Geral")
            secao1_sub1_conteudo = st.text_area("Conteúdo do Subitem 1.1 (lista)", "País: Portugal\nNúmero de clubes: 18", help=help_text)
            secao1_sub2_titulo = st.text_input("Título do Subitem 1.2", "🏆 Vagas Europeias")
            secao1_sub2_tabela = st.text_area("Tabela do Subitem 1.2", "Posição;Competição\n1º;Fase de grupos da UEFA Champions League", help=help_text)

            if st.form_submit_button("Gerar Dossiê", type="primary", use_container_width=True):
                # Processa os campos do formulário para o formato de dados esperado
                def parse_list(text): return [item.strip() for item in text.split('\n') if item.strip()]
                def parse_table(text):
                    lines = [line.strip() for line in text.split('\n') if line.strip()]
                    return {'cabecalho': [h.strip() for h in lines[0].split(';')], 'linhas': [[cell.strip() for cell in row.split(';')] for row in lines[1:]]}
                
                dossier_data = {
                    "template_type": "liga_dark_pro", "titulo_geral": f"Dossiê Técnico-Tático: {liga} – {pais} – Temporada {temporada}",
                    "data_atualizacao": data_atualizacao,
                    "secoes": [
                        {"titulo_secao": secao1_titulo,
                         "subsecoes": [
                             {"titulo_sub": secao1_sub1_titulo, "conteudo": parse_list(secao1_sub1_conteudo)},
                             {"titulo_sub": secao1_sub2_titulo, "tabela": parse_table(secao1_sub2_tabela)},
                         ]}
                    ]
                }
                yaml_string = yaml.dump(dossier_data, sort_keys=False, allow_unicode=True, indent=2)
                file_name = f"D1P1_Analise_Liga_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.yml"
                path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                with st.spinner("Salvando..."):
                    try:
                        repo.create_file(full_path, f"Adiciona: {file_name}", yaml_string); st.success(f"Dossiê salvo: {full_path}")
                    except Exception as e: st.error(f"Erro ao salvar: {e}")

    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

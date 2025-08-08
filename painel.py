# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v13.0: Estilização Avançada com Callouts e Tabelas
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml

# --- 1. CONFIGURAÇÃO E ESTILOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """CSS aprimorado conforme as sugestões para um visual moderno, interativo e com destaques."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            @import url('https://fonts.googleapis.com/css2?family=Noto+Emoji&display=swap');
            
            body, .main { 
                font-family: 'Roboto', sans-serif; 
                background-color: #1A202C; /* Fundo escuro para contraste */
            }
            
            .dossier-container { 
                padding: 1rem 2rem; 
                max-width: 1200px; 
                margin: 0 auto; 
            }
            
            /* Título Principal */
            .comp-main-title { 
                font-size: 2.2rem; 
                font-weight: 900; 
                color: #F3F4F6; 
                margin-bottom: 2.5rem; 
                background: linear-gradient(90deg, #3B82F6, #60A5FA); /* Gradiente azul */
                -webkit-background-clip: text; 
                -webkit-text-fill-color: transparent; 
                text-align: center; 
            }
            .comp-main-title span { 
                vertical-align: middle; 
                font-size: 3rem; 
                margin-right: 15px; 
                font-family: 'Noto Emoji', sans-serif; 
            }

            /* Títulos de Seção */
            .comp-section-title { 
                font-size: 1.7rem; 
                font-weight: 700; 
                text-transform: uppercase; 
                color: #FFFFFF; 
                margin-top: 3rem; 
                margin-bottom: 1.5rem; 
                padding-left: 10px; 
                border-left: 4px solid #3B82F6; /* Borda azul à esquerda */
            }
            .comp-section-title span { 
                vertical-align: middle; 
                font-size: 1.4rem; 
                margin-right: 12px; 
                font-family: 'Noto Emoji', sans-serif; 
            }

            /* Subtítulos com Ícone */
            .comp-subtitle-icon { 
                font-size: 1.3rem; 
                font-weight: 700; 
                color: #93C5FD; 
                margin-top: 2rem; 
                margin-bottom: 1rem; 
                transition: color 0.3s ease; 
            }
            .comp-subtitle-icon:hover { 
                color: #3B82F6; /* Hover azul vibrante */
            }
            .comp-subtitle-icon span { 
                vertical-align: middle; 
                margin-right: 10px; 
                font-family: 'Noto Emoji', sans-serif; 
            }

            /* Subtítulos de Itens */
            .comp-item-subtitle { 
                font-size: 1.2rem; 
                font-weight: 600; 
                color: #A5B4FC; /* Roxo claro */
                margin-top: 1.5rem; 
                margin-bottom: 0.8rem; 
                padding: 0.5rem 1rem; 
                background-color: #2D3748; /* Fundo escuro */
                border-radius: 6px; 
                box-shadow: 0 2px 4px rgba(0, 0, 0, 0.2); 
                transition: transform 0.2s ease; 
            }
            .comp-item-subtitle:hover { 
                transform: translateY(-2px); /* Efeito de elevação no hover */
            }

            /* Parágrafos */
            .comp-paragraph { 
                font-size: 1.15rem; 
                color: #CBD5E1; /* Cinza claro para maior legibilidade */
                line-height: 1.8; 
                margin-bottom: 1.2rem; 
                white-space: pre-wrap; 
            }

            /* Listas */
            .comp-simple-list ul { 
                list-style-type: none; 
                padding-left: 1.5rem; 
                margin-top: 1rem; 
            }
            .comp-simple-list li { 
                margin-bottom: 0.8rem; 
                color: #CBD5E1; 
                font-size: 1.15rem; 
                position: relative; 
                padding-left: 1.5rem; 
                transition: color 0.3s ease; 
            }
            .comp-simple-list li::before { 
                content: "➔"; /* Ícone de seta para listas */
                color: #60A5FA; 
                position: absolute; 
                left: 0; 
                font-size: 1.2rem; 
            }
            .comp-simple-list li:hover { 
                color: #F3F4F6; /* Destaque no hover */
            }

            /* Callouts */
            .comp-callout { 
                background-color: #1E3A8A; /* Fundo azul escuro */
                border-left: 4px solid #3B82F6; 
                padding: 1rem 1.5rem; 
                margin: 1rem 0; 
                border-radius: 6px; 
                box-shadow: 0 2px 6px rgba(0, 0, 0, 0.3); 
                color: #F3F4F6; 
                font-size: 1.1rem; 
            }
            .comp-callout::before { 
                content: "🔔"; 
                margin-right: 10px; 
                font-family: 'Noto Emoji', sans-serif; 
            }

            /* Tabelas */
            .comp-table { 
                width: 100%; 
                border-collapse: collapse; 
                margin: 1.5rem 0; 
                background-color: #2D3748; 
                border-radius: 8px; 
                overflow: hidden; 
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
            }
            .comp-table th, .comp-table td { 
                padding: 1rem; 
                text-align: left; 
                font-size: 1.1rem; 
                color: #F3F4F6; 
            }
            .comp-table th { 
                background-color: #3B82F6; 
                font-weight: 700; 
            }
            .comp-table tr:nth-child(even) { 
                background-color: #4A5568; /* Alternância de cores */
            }
            .comp-table tr:hover { 
                background-color: #6366F1; /* Hover nas linhas */
            }

            /* Sidebar */
            [data-testid="stSidebar"] { 
                border-right: 1px solid #4A5568; 
                background-color: #1F2937; 
            }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADOR E FUNÇÕES AUXILIARES ---
def parse_text_to_components(text_content: str) -> list:
    """Analisa um bloco de texto e o converte em uma lista de componentes, incluindo tabelas e callouts."""
    components = []; current_list_items = []; icon_map = {"1": "1️⃣", "2": "2️⃣", "3": "3️⃣", "4": "4️⃣", "5": "5️⃣"}
    
    def flush_list():
        if current_list_items:
            components.append({'tipo': 'lista_simples', 'itens': current_list_items.copy()})
            current_list_items.clear()
    
    lines = text_content.split('\n')
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue

        # Detectar Tabelas
        if line.startswith('|') and i + 1 < len(lines) and lines[i + 1].strip().startswith('|--'):
            flush_list()
            table_lines = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                table_lines.append(lines[i].strip())
                i += 1
            # Ignora a linha de separador (ex: |---|---|)
            headers = [h.strip() for h in table_lines[0].split('|')[1:-1]]
            rows = [[cell.strip() for cell in row.split('|')[1:-1]] for row in table_lines[2:]]
            components.append({'tipo': 'tabela', 'headers': headers, 'rows': rows})
            continue

        # Detectar Callouts
        if line.startswith('>'):
            flush_list()
            components.append({'tipo': 'callout', 'texto': line[1:].strip()})
            i += 1
            continue

        # Detectar Subtítulos de Itens
        if line.strip().endswith(':') and not re.match(r'^(\d+)\.\s(.+)', line):
            flush_list()
            components.append({'tipo': 'sub_item_titulo', 'texto': line})
            i += 1
            continue
        
        # Detectar Subtítulos com Ícone
        match = re.match(r'^(\d+)\.\s(.+)', line)
        if match:
            flush_list()
            num, text = match.groups()
            icon = icon_map.get(num, '•')
            components.append({'tipo': 'subtitulo_com_icone', 'icone': icon, 'texto': text})
            i += 1
            continue
        
        # Detectar Itens de Lista
        if line.startswith('• ') or line.startswith('- '):
            if not current_list_items: flush_list()
            current_list_items.append(line[2:].strip())
            i += 1
            continue
        
        # Parágrafos
        flush_list()
        components.append({'tipo': 'paragrafo', 'texto': line})
        i += 1

    flush_list()
    return components

def render_dossier_from_blueprint(data: dict):
    """Renderiza um dossiê a partir de um dicionário de dados, agora com suporte a tabelas e callouts."""
    st.markdown('<div class="dossier-container">', unsafe_allow_html=True)
    if 'metadata' in data:
        meta = data['metadata']
        st.markdown(f'<h1 class="comp-main-title"><span>{meta.get("icone_principal", "📄")}</span> {meta.get("titulo_principal", "Dossiê")}</h1>', unsafe_allow_html=True)
    if 'componentes' in data:
        for comp in data['componentes']:
            tipo = comp.get('tipo')
            if tipo == 'titulo_secao': st.markdown(f'<h2 class="comp-section-title"><span>{comp.get("icone", "■")}</span>{comp.get("texto", "")}</h2>', unsafe_allow_html=True)
            elif tipo == 'subtitulo_com_icone': st.markdown(f'<h3 class="comp-subtitle-icon"><span>{comp.get("icone", "•")}</span>{comp.get("texto", "")}</h3>', unsafe_allow_html=True)
            elif tipo == 'sub_item_titulo': st.markdown(f'<p class="comp-item-subtitle">{comp.get("texto", "")}</p>', unsafe_allow_html=True)
            elif tipo == 'paragrafo': st.markdown(f'<p class="comp-paragraph">{comp.get("texto", "")}</p>', unsafe_allow_html=True)
            elif tipo == 'lista_simples':
                list_items_html = "<div class='comp-simple-list'><ul>" + "".join([f"<li>{item}</li>" for item in comp.get('itens', [])]) + "</ul></div>"
                st.markdown(list_items_html, unsafe_allow_html=True)
            elif tipo == 'callout':
                st.markdown(f'<div class="comp-callout">{comp.get("texto", "")}</div>', unsafe_allow_html=True)
            elif tipo == 'tabela':
                headers = comp.get('headers', []); rows = comp.get('rows', [])
                table_html = '<table class="comp-table"><thead><tr>' + ''.join([f'<th>{h}</th>' for h in headers]) + '</tr></thead><tbody>'
                for row in rows: table_html += '<tr>' + ''.join([f'<td>{cell}</td>' for cell in row]) + '</tr>'
                table_html += '</tbody></table>'
                st.markdown(table_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

# (O restante do código principal e funções auxiliares permanecem os mesmos)
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None
def check_password():
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
def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".yml")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3, c4 = st.columns([4, 1, 1, 1])
                with c1:
                    if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                        file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                with c3:
                    if st.button("✏️", key=f"edit_{content_file.path}", help="Editar (desabilitado)", use_container_width=True): st.warning("A edição será reimplementada.")
                with c4:
                    if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir", use_container_width=True): st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
                if st.session_state.get('file_to_delete', {}).get('path') == content_file.path:
                    st.warning(f"Excluir `{content_file.path}`?"); btn_c1, btn_c2 = st.columns(2)
                    if btn_c1.button("Sim, excluir!", key=f"confirm_del_{content_file.path}", type="primary"):
                        file_info = st.session_state.pop('file_to_delete'); repo.delete_file(file_info['path'], f"Exclui {file_info['path']}", file_info['sha'])
                        if st.session_state.get('viewing_file_name') == os.path.basename(file_info['path']): st.session_state.pop('viewing_file_content', None); st.session_state.pop('viewing_file_name', None)
                        st.success(f"Arquivo '{file_info['path']}' excluído."); st.rerun()
                    if btn_c2.button("Cancelar", key=f"cancel_del_{content_file.path}"): st.session_state.pop('file_to_delete'); st.rerun()
    except Exception as e: st.error(f"Erro ao listar arquivos: {e}")

# --- CÓDIGO PRINCIPAL DA APLICAÇÃO ---
if not check_password(): st.stop()
apply_custom_styling()
repo = get_github_repo()

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
            st.subheader("Navegador do Repositório"); search_term = st.text_input("Filtrar...", label_visibility="collapsed", placeholder="Filtrar por nome do arquivo..."); st.divider()
            display_repo_structure(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}"); st.divider()
                try:
                    dossier_data = {'metadata': {}, 'componentes': parse_text_to_components(st.session_state.viewing_file_content)}
                    render_dossier_from_blueprint(dossier_data)
                except Exception as e:
                    st.error(f"Ocorreu um erro ao renderizar o dossiê: {e}")
                    st.code(st.session_state.viewing_file_content)
            else: st.info("Selecione um dossiê para visualizar.")

elif selected_action == "Carregar Dossiê":
    st.header("Criar Novo Dossiê"); st.info("Selecione o tipo de dossiê, preencha as informações e o conteúdo.")
    dossier_type_options = ["", "D1 P1 - Análise da Liga"] # Adicionar outros tipos aqui
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")

    if dossier_type == "D1 P1 - Análise da Liga":
        st.subheader("Template: Análise da Liga")
        with st.form("liga_form_final", clear_on_submit=True):
            st.subheader("Informações de Arquivo")
            c1, c2, c3 = st.columns(3); pais = c1.text_input("País*", key="pais"); liga = c2.text_input("Liga*", key="liga"); temporada = c3.text_input("Temporada*", key="temporada")
            st.divider(); st.subheader("Conteúdo do Dossiê")
            conteudo = st.text_area("Cole aqui a análise completa", height=400, key="conteudo", help="Use a sintaxe Markdown para formatar: # Título, > Callout, |Tabela|, etc.")
            
            if st.form_submit_button("Gerar e Salvar Dossiê", type="primary", use_container_width=True):
                if not all([pais, liga, temporada, conteudo]):
                    st.error("Todos os campos * são obrigatórios.")
                else:
                    file_name = f"D1P1_Analise_Liga_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.md" # Salvar como .md
                    path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                    with st.spinner("Verificando e salvando..."):
                        try:
                            existing_file = repo.get_contents(full_path)
                            repo.update_file(existing_file.path, f"Atualiza: {file_name}", conteudo, existing_file.sha)
                            st.success(f"Dossiê '{full_path}' ATUALIZADO!")
                        except UnknownObjectException:
                            repo.create_file(full_path, f"Adiciona: {file_name}", conteudo)
                            st.success(f"Dossiê '{full_path}' CRIADO!")
                        except Exception as e: st.error(f"Ocorreu um erro: {e}")
    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

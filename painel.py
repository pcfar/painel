# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v15.0: Versão Estável e Definitiva
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
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }

            /* --- ESTILOS PARA O RENDERIZADOR PADRÃO (BLUEPRINT) --- */
            .dossier-container { padding: 0 1rem; }
            .comp-main-title { font-size: 1.8rem; font-weight: 900; color: #E2E8F0; margin-bottom: 2rem; }
            .comp-main-title span { vertical-align: middle; font-size: 2.5rem; margin-right: 15px; }
            .comp-section-title { font-size: 1.5rem; font-weight: 700; text-transform: uppercase; color: #FFFFFF; margin-top: 3rem; margin-bottom: 1.5rem; }
            .comp-section-title span { vertical-align: middle; font-size: 1.2rem; margin-right: 12px; }
            .comp-subtitle-icon { font-size: 1.2rem; font-weight: 700; color: #E2E8F0; margin-top: 2rem; margin-bottom: 1rem; }
            .comp-subtitle-icon span { vertical-align: middle; margin-right: 10px; }
            .comp-paragraph { font-size: 1.1rem; color: #A0AEC0; line-height: 1.9; margin-bottom: 1rem; white-space: pre-wrap; }
            .comp-simple-list ul { list-style-type: none; padding-left: 1rem; margin-top: 1rem; }
            .comp-simple-list li { margin-bottom: 0.7rem; color: #A0AEC0; font-size: 1.1rem; }
            .comp-simple-list li::before { content: "▪"; color: #63B3ED; margin-right: 12px; font-size: 1.2rem; }

            /* --- ESTILOS PARA O TEMPLATE DE DOMINÂNCIA (TEMA ESCURO) --- */
            .dominance-box { background-color: #2D3748; border: 1px solid #4A5568; border-radius: 15px; padding: 25px; margin-bottom: 30px; color: #E2E8F0; }
            .dominance-box .title { font-size: 2rem; font-weight: 700; color: #FFFFFF; margin-bottom: 10px; }
            .dominance-box .subtitle { font-size: 1.1rem; color: #A0AEC0; margin-bottom: 25px; }
            .dominance-box .section-title { font-size: 1.4rem; color: #E2E8F0; margin-top: 25px; margin-bottom: 15px; border-bottom: 2px solid #4A5568; padding-bottom: 5px;}
            .dominance-box .highlight { background-color: #4A5568; padding: 6px 10px; border-radius: 8px; font-weight: 600; }
            .dominance-box .verdict { background-color: rgba(49, 130, 206, 0.1); border-left: 6px solid #3182CE; padding: 15px; border-radius: 10px; margin-top: 20px; }
            .dominance-box .verdict ul { padding-left: 20px; margin: 0; }
            .dominance-box .verdict li { margin-bottom: 10px; }
            .dominance-box table { width: 100%; border-collapse: collapse; margin-top: 10px; font-size: 1rem; }
            .dominance-box th, .dominance-box td { border: 1px solid #4A5568; padding: 10px; text-align: center; }
            .dominance-box th { background-color: #4A5568; color: #FFFFFF; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. RENDERIZADORES E FUNÇÕES AUXILIARES ---
def render_dossier_from_blueprint(data: dict):
    # Renderizador padrão para dossiês genéricos
    st.markdown('<div class="dossier-container">', unsafe_allow_html=True)
    if 'metadata' in data: meta = data['metadata']; st.markdown(f'<h1 class="comp-main-title"><span>{meta.get("icone_principal", "📄")}</span> {meta.get("titulo_principal", "Dossiê")}</h1>', unsafe_allow_html=True)
    if 'componentes' in data:
        for comp in data['componentes']:
            tipo = comp.get('tipo');
            if tipo == 'titulo_secao': st.markdown(f'<h2 class="comp-section-title"><span>{comp.get("icone", "■")}</span>{comp.get("texto", "")}</h2>', unsafe_allow_html=True)
            elif tipo == 'subtitulo_com_icone': st.markdown(f'<h3 class="comp-subtitle-icon"><span>{comp.get("icone", "•")}</span>{comp.get("texto", "")}</h3>', unsafe_allow_html=True)
            elif tipo == 'paragrafo': st.markdown(f'<p class="comp-paragraph">{comp.get("texto", "")}</p>', unsafe_allow_html=True)
            elif tipo == 'lista_simples': list_items_html = "<div class='comp-simple-list'><ul>" + "".join([f"<li>{item}</li>" for item in comp.get('itens', [])]) + "</ul></div>"; st.markdown(list_items_html, unsafe_allow_html=True)
    st.markdown('</div>', unsafe_allow_html=True)

def render_dominance_dossier(data: dict):
    """Renderizador específico para o dossiê de Análise de Dominância."""
    tabela_html = "".join([f"<tr><td>{i+1}</td><td>{item.get('equipe')}</td><td>{item.get('pontos')}</td></tr>" for i, item in enumerate(data.get('tabela_dominancia', []))])
    html = f"""
    <div class="dominance-box">
        <div class="title">⚽ Análise de Dominância: <span class="highlight">{data.get('liga_nome', '')}</span></div>
        <div class="subtitle">📍 Um mergulho quantitativo na estrutura de poder e competitividade da elite do futebol no(a) <b>{data.get('pais', '')}</b> na última década.</div>
        <div class="section-title">📊 Placar de Dominância (Últimas 10 Temporadas)</div>
        <table><tr><th>Posição</th><th>Equipe</th><th>Pontuação Total</th></tr>{tabela_html}</table>
        <div class="section-title">🎯 Análise do Estratega</div>
        <p><b>🔷 Estrutura de Poder:</b><br>{data.get('analise_poder', '')}</p>
        <p><b>📌 Índice de Concentração no Top 3:</b> <span class="highlight">{data.get('indice_top3', 'N/A')}%</span><br>{data.get('comentario_concentracao', '')}</p>
        <p><b>📈 Evolução da Competitividade:</b><br>{data.get('evolucao', '')}</p>
        <div class="section-title">📥 Veredito Final: Playlist de Monitoramento</div>
        <div class="verdict"><ul>
            <li><b>🥇 {data.get('veredicto1', {}).get('equipe', '')}</b> – {data.get('veredicto1', {}).get('comentario', '')}</li>
            <li><b>🥈 {data.get('veredicto2', {}).get('equipe', '')}</b> – {data.get('veredicto2', {}).get('comentario', '')}</li>
            <li><b>🥉 {data.get('veredicto3', {}).get('equipe', '')}</b> – {data.get('veredicto3', {}).get('comentario', '')}</li>
        </ul></div>
    </div>"""
    st.markdown(html, unsafe_allow_html=True)

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

def parse_yaml_to_form_state(data, dossier_type):
    """Preenche o st.session_state com dados de um dossiê para edição."""
    st.session_state.dossier_type_selector = dossier_type
    if dossier_type == "D1 P2 - Análise dos Clubes Dominantes da Liga":
        st.session_state.pais = data.get('pais', '')
        st.session_state.liga = data.get('liga_nome', '')
        st.session_state.tabela_raw = "\n".join([f"{item.get('equipe', '')}, {item.get('pontos', '')}" for item in data.get('tabela_dominancia', [])])
        st.session_state.analise_poder = data.get('analise_poder', '')
        st.session_state.indice_top3 = data.get('indice_top3', 0)
        st.session_state.comentario_concentracao = data.get('comentario_concentracao', '')
        st.session_state.evolucao = data.get('evolucao', '')
        st.session_state.veredicto1_equipe = data.get('veredicto1', {}).get('equipe', '')
        st.session_state.veredicto1_comentario = data.get('veredicto1', {}).get('comentario', '')
        st.session_state.veredicto2_equipe = data.get('veredicto2', {}).get('equipe', '')
        st.session_state.veredicto2_comentario = data.get('veredicto2', {}).get('comentario', '')
        st.session_state.veredicto3_equipe = data.get('veredicto3', {}).get('equipe', '')
        st.session_state.veredicto3_comentario = data.get('veredicto3', {}).get('comentario', '')

def display_repo_structure(repo, path="", search_term="", show_actions=False):
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and f.name.endswith(".yml")], key=lambda x: x.name)
        for content_dir in dirs:
            with st.expander(f"📁 {content_dir.name}"): display_repo_structure(repo, content_dir.path, search_term, show_actions)
        if search_term: files = [f for f in files if search_term.lower() in f.name.lower()]
        for content_file in files:
            if show_actions:
                c1, c2, c3 = st.columns([5, 1, 1])
                with c1:
                    if st.button(f"📄 {content_file.name}", key=f"view_{content_file.path}", use_container_width=True):
                        file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8"); st.session_state.update(viewing_file_content=file_content_raw, viewing_file_name=content_file.name)
                with c2:
                    if st.button("✏️", key=f"edit_{content_file.path}", help="Editar Dossiê", use_container_width=True):
                        with st.spinner("Carregando para edição..."):
                            file_to_edit = repo.get_contents(content_file.path)
                            dossier_data = yaml.safe_load(base64.b64decode(file_to_edit.content).decode("utf-8"))
                            
                            st.session_state.edit_sha = file_to_edit.sha
                            st.session_state.edit_path = file_to_edit.path
                            
                            # Inferir tipo e preencher o formulário
                            dossier_type_to_load = dossier_data.get("template_type", "genérico")
                            if dossier_type_to_load == "dominancia_liga":
                                parse_yaml_to_form_state(dossier_data, "D1 P2 - Análise dos Clubes Dominantes da Liga")
                            # Adicionar `elif` para outros tipos de dossiê aqui
                            
                            st.session_state.edit_mode = True
                            st.session_state.selected_action = "Carregar Dossiê"
                            st.rerun()
                with c3:
                    if st.button("🗑️", key=f"delete_{content_file.path}", help="Excluir Dossiê", use_container_width=True):
                        st.session_state['file_to_delete'] = {'path': content_file.path, 'sha': content_file.sha}; st.rerun()
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
            display_repo_structure_full(repo, search_term=search_term, show_actions=True)
        with col2:
            st.subheader("Visualizador de Conteúdo")
            if st.session_state.get("viewing_file_content"):
                file_name = st.session_state.get("viewing_file_name", "")
                st.markdown(f"#### {file_name}"); st.divider()
                try:
                    dossier_data = yaml.safe_load(st.session_state.viewing_file_content)
                    if isinstance(dossier_data, dict):
                        if dossier_data.get("template_type") == "dominancia_liga":
                            render_dominance_dossier(dossier_data)
                        else: render_dossier_from_blueprint(dossier_data)
                    else: st.warning("⚠️ Formato Inesperado"); st.code(st.session_state.viewing_file_content, language="yaml")
                except yaml.YAMLError: st.error("⚠️ Formato de Arquivo Inválido ou Corrompido"); st.info("Este arquivo não pôde ser lido."); st.code(st.session_state.viewing_file_content, language="text")
            else: st.info("Selecione um dossiê para visualizar.")

elif selected_action == "Carregar Dossiê":
    is_edit_mode = st.session_state.get("edit_mode", False)
    st.header("Editar Dossiê" if is_edit_mode else "Criar Novo Dossiê")
    
    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes da Liga", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Tipo de Dossiê**", dossier_type_options, key="dossier_type_selector", disabled=is_edit_mode)

    if dossier_type == "D1 P2 - Análise dos Clubes Dominantes da Liga":
        st.subheader("Template: Análise de Dominância")
        with st.form("dominance_form"):
            st.write("**Informações Gerais**"); c1, c2, c3 = st.columns(3); pais = c1.text_input("País*", key="pais"); liga = c2.text_input("Liga*", key="liga"); temporada = c3.text_input("Temporada*", key="temporada")
            st.divider(); st.write("**Placar de Dominância**"); tabela_raw = st.text_area("Dados da Tabela*", key="tabela_raw", help="Um time e sua pontuação por linha, separados por vírgula. Ex: FC Copenhagen, 50")
            st.divider(); st.write("**Análise do Estratega**"); analise_poder = st.text_area("Análise da Estrutura de Poder*", key="analise_poder"); c1, c2 = st.columns(2); indice_top3 = c1.number_input("Índice de Concentração no Top 3 (%)*", min_value=0, max_value=100, key="indice_top3"); comentario_concentracao = c2.text_area("Comentário sobre a Concentração*", key="comentario_concentracao"); evolucao = st.text_area("Análise da Evolução da Competitividade*", key="evolucao")
            st.divider(); st.write("**Veredito Final** (Top 3)"); c1, c2 = st.columns(2); veredicto1_equipe = c1.text_input("🥇 1º Lugar (Equipe)*", key="veredicto1_equipe"); veredicto1_comentario = c2.text_area("Comentário sobre o 1º Lugar*", key="veredicto1_comentario"); c1, c2 = st.columns(2); veredicto2_equipe = c1.text_input("🥈 2º Lugar (Equipe)*", key="veredicto2_equipe"); veredicto2_comentario = c2.text_area("Comentário sobre o 2º Lugar*", key="veredicto2_comentario"); c1, c2 = st.columns(2); veredicto3_equipe = c1.text_input("🥉 3º Lugar (Equipe)*", key="veredicto3_equipe"); veredicto3_comentario = c2.text_area("Comentário sobre o 3º Lugar*", key="veredicto3_comentario")
            
            submit_label = "Atualizar Dossiê" if is_edit_mode else "Gerar Dossiê de Dominância"
            if st.form_submit_button(submit_label, type="primary", use_container_width=True):
                tabela_dominancia = [{'equipe': parts[0].strip(), 'pontos': parts[1].strip()} for line in tabela_raw.split('\n') if ',' in line and (parts := line.split(',', 1))]
                dossier_data = {"template_type": "dominancia_liga", "pais": pais, "liga_nome": liga, "tabela_dominancia": tabela_dominancia, "analise_poder": analise_poder, "indice_top3": indice_top3, "comentario_concentracao": comentario_concentracao, "evolucao": evolucao, "veredicto1": {"equipe": veredicto1_equipe, "comentario": veredicto1_comentario}, "veredicto2": {"equipe": veredicto2_equipe, "comentario": veredicto2_comentario}, "veredicto3": {"equipe": veredicto3_equipe, "comentario": veredicto3_comentario}}
                yaml_string = yaml.dump(dossier_data, sort_keys=False, allow_unicode=True, indent=2)
                
                with st.spinner("Salvando..."):
                    try:
                        if is_edit_mode:
                            file_name = os.path.basename(st.session_state.edit_path)
                            repo.update_file(st.session_state.edit_path, f"Atualiza: {file_name}", yaml_string, st.session_state.edit_sha); st.success(f"Dossiê ATUALIZADO com sucesso: {st.session_state.edit_path}")
                        else:
                            file_name = f"D1P2_Analise_Dominancia_{liga.replace(' ', '_')}_{pais.replace(' ', '_')}.yml"
                            path_parts = [pais, liga, temporada]; full_path = "/".join(p.replace(" ", "_") for p in path_parts) + "/" + file_name
                            repo.create_file(full_path, f"Adiciona: {file_name}", yaml_string); st.success(f"Dossiê CRIADO com sucesso: {full_path}")

                        # Limpa o estado e volta ao leitor
                        for key in list(st.session_state.keys()):
                            if key not in ['password_correct', 'main_menu']: del st.session_state[key]
                        st.session_state.selected_action = "Leitor de Dossiês"; st.rerun()

                    except Exception as e: st.error(f"Erro ao salvar: {e}")
    elif dossier_type:
        st.warning(f"O template para '{dossier_type}' ainda está em desenvolvimento.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")

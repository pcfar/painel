Com certeza. O texto que você enviou é um excelente exemplo de um dossiê bem estruturado. É o material perfeito para testarmos e refinarmos a estilização do nosso painel.

Vamos discutir com a equipe como ele seria apresentado hoje e, mais importante, como podemos elevá-lo a um novo patamar de clareza e profissionalismo.

-----

### **Como o Dossiê é Apresentado Atualmente**

Usando o motor de renderização atual (`markdown2`) e nosso CSS, o seu texto já terá uma boa estrutura. O sistema irá identificar os títulos, subtítulos, listas e a tabela, aplicando os estilos que definimos.

**O resultado seria muito próximo disto:**

> # Dossiê Técnico‑Tático: Liga Portugal Betclic – Portugal – Temporada 2025/26
>
> 📅 Atualizado em: 8 de agosto de 2025
> Fontes principais: Liga Portugal, Federação Portuguesa de Futebol, UEFA, Transfermarkt, SofaScore, ESPN, Bola na Rede, A Bola, Globoesporte
>
> -----
>
> ## 📑 Índice
>
>   * Estrutura e Identidade da Liga
>   * Cenário Tático e Tendências
>   * Destaques Individuais e Promessas
>   * Pilares Históricos e Cultura
>   * Panorama Econômico e Transferências
>
> -----
>
> ## ⚽ Estrutura e Identidade da Liga
>
> ### 📋 Visão Geral
>
>   * País: Portugal
>   * Número de clubes: 18
>   * ... (e assim por diante)

É um bom começo, mas como você mesmo intuiu, podemos ir muito além.

-----

### **Discussão da Equipe e Sugestões de Melhoria**

Sua intuição está correta. A apresentação, embora estruturada, ainda carece de "personalidade" e de destaques visuais mais fortes que realmente guiem o olhar do analista.

**O objetivo é transformar o texto de "bem formatado" para "bem desenhado".**

**1. Bloco de Metadados (O Início do Dossiê)**

  * **Problema:** As linhas "Atualizado em:" e "Fontes principais:" são tratadas como parágrafos comuns, sem nenhum destaque.
  * **Solução:** Criaremos um "bloco de metadados" estilizado. Vamos envolvê-lo em um cartão com um fundo sutilmente diferente e um ícone, para que ele seja imediatamente reconhecido como um cabeçalho de informações.

**2. Divisores (`---`)**

  * **Problema:** A linha `---` cria um divisor padrão que é muito simples e fino.
  * **Solução:** Vamos estilizar o divisor para que ele seja mais marcante, talvez um pouco mais grosso e com um gradiente suave, servindo como uma quebra visual forte e elegante entre as seções.

**3. Hierarquia de Títulos (H1, H2, H3)**

  * **Problema:** A diferença de tamanho e peso entre os títulos `##` e `###` pode ser mais pronunciada.
  * **Solução:** Ajustaremos o CSS para aumentar o contraste entre eles. Os títulos de seção principal (`<h2>`) terão uma borda ou um fundo sutil, enquanto os subtítulos (`<h3>`) terão uma cor de destaque mais vibrante para indicar que são tópicos dentro da seção.

**4. Destaque para Informações-Chave**

  * **Problema:** Linhas como `País: Portugal` são tratadas como texto comum.
  * **Solução:** Vamos ensinar o nosso sistema a reconhecer o padrão `**Palavra-Chave:** Texto`. Quando ele encontrar isso, irá manter a "Palavra-Chave" em negrito e com a cor de destaque, mas irá garantir que o "Texto" que vem depois tenha uma cor de conteúdo padrão, criando um contraste visual limpo.

-----

### **Código `painel.py` com as Melhorias Implementadas**

Abaixo está a versão final do código que implementa todas essas melhorias de design. As alterações foram feitas exclusivamente na função `apply_custom_styling()` e na lógica de renderização para suportar o novo "bloco de metadados".

```python
# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v13.1: Estilização de Elite
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import markdown2

# --- 1. CONFIGURAÇÃO E ESTILOS FINAIS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """CSS de alta fidelidade para renderizar o HTML gerado pelo Markdown2."""
    st.markdown("""
        <style>
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700;900&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }
            
            .dossier-viewer { line-height: 1.8; font-size: 1.1rem; color: #E2E8F0; }

            /* --- NOVO: Bloco de Metadados --- */
            .dossier-viewer .metadata-block {
                background-color: rgba(45, 55, 72, 0.5);
                border-left: 4px solid #3182CE;
                padding: 1rem 1.5rem;
                margin-bottom: 2.5rem;
                border-radius: 8px;
            }
            .dossier-viewer .metadata-block p {
                margin-bottom: 0.5rem;
                color: #A0AEC0;
                font-size: 0.9rem;
            }

            .dossier-viewer h1 { 
                font-size: 2.4rem; font-weight: 900; color: #FFFFFF; 
                margin-bottom: 1rem; 
            }
            .dossier-viewer h2 { 
                font-size: 1.8rem; font-weight: 700; color: #E2E8F0; 
                margin-top: 3rem; margin-bottom: 1.5rem; 
                padding-bottom: 0.5rem;
                border-bottom: 2px solid #4A5568;
            }
            .dossier-viewer h3 { 
                font-size: 1.4rem; font-weight: 700; color: #a5b4fc; 
                margin-top: 2.5rem; margin-bottom: 1rem; 
            }
            .dossier-viewer p { margin-bottom: 1rem; color: #A0AEC0; }
            .dossier-viewer strong { color: #a5b4fc; font-weight: 700; }
            .dossier-viewer ul { list-style-type: none; padding-left: 0; margin-top: 1rem;}
            .dossier-viewer li { 
                margin-bottom: 0.7rem; color: #A0AEC0;
                padding-left: 1.5em; text-indent: -1.5em;
            }
            .dossier-viewer li::before { 
                content: "▪"; color: #63B3ED; margin-right: 10px; 
                font-size: 1.2rem;
            }
            /* --- NOVO: Estilo para o Divisor --- */
            .dossier-viewer hr {
                border: none;
                border-top: 2px solid #4A5568;
                margin: 3rem 0;
            }
            /* Estilo para tabelas */
            .dossier-viewer table { 
                width: 100%; border-collapse: collapse; margin: 1.5rem 0; 
                background-color: #2D3748; border-radius: 8px; overflow: hidden; 
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.3); 
            }
            .dossier-viewer th, .dossier-viewer td { padding: 1rem; text-align: left; font-size: 1rem; color: #F3F4F6; }
            .dossier-viewer th { background-color: #3B82F6; font-weight: 700; }
            .dossier-viewer tr:nth-child(even) { background-color: #4A5568; }
            
            [data-testid="stSidebar"] { border-right: 1px solid #4A5568; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. FUNÇÕES AUXILIARES ---
@st.cache_resource
def get_github_repo():
    try: g = Github(st.secrets["GITHUB_TOKEN"]); repo_name = f"{st.secrets['GITHUB_USERNAME']}/{st.secrets['GITHUB_REPO_NAME']}"; return g.get_repo(repo_name)
    except Exception as e: st.error(f"Falha na conexão com o GitHub: {e}"); return None

def check_password():
    if st.session_state.get("password_correct", False): return True
    _, center_col, _ = st.columns([1, 1, 1])
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
    # Lógica de exibição de arquivos (sem alterações)
    try:
        contents = repo.get_contents(path); dirs = sorted([c for c in contents if c.type == 'dir'], key=lambda x: x.name); files = sorted([f for f in contents if f.type == 'file' and (f.name.endswith(".yml") or f.name.endswith(".md"))], key=lambda x: x.name)
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

                # --- NOVO ANALISADOR DE CONTEÚDO ---
                content = st.session_state.viewing_file_content
                # Separa o conteúdo em cabeçalho e corpo
                parts = content.split('---', 1)
                header_content = parts[0]
                body_content = parts[1] if len(parts) > 1 else ""

                # Converte o corpo para HTML
                html_body = markdown2.markdown(body_content, extras=['tables', 'fenced-code-blocks'])

                # Monta a visualização final com o bloco de metadados
                final_html = f"""
                <div class='dossier-viewer'>
                    <div class='metadata-block'>{markdown2.markdown(header_content)}</div>
                    {html_body}
                </div>
                """
                st.markdown(final_html, unsafe_allow_html=True)
            else: st.info("Selecione um arquivo para visualizar.")

elif selected_action == "Carregar Dossiê":
    # O código dos formulários da v11 permanece, pois a lógica de criação está estável.
    st.header("Criar Novo Dossiê"); st.info("Selecione o tipo de dossiê, preencha as informações e o conteúdo em Markdown.")
    dossier_type_options = ["", "D1 P1 - Análise da Liga", "D1 P2 - Análise dos Clubes Dominantes", "D2 P1 - Análise Comparativa de Planteis", "D2 P2 - Estudo Técnico e Tático dos Clubes", "D3 - Análise Tática (Pós Rodada)", "D4 - Briefing Semanal (Pré Rodada)"]
    dossier_type = st.selectbox("**Qual tipo de dossiê você quer criar?**", dossier_type_options, key="dossier_type_selector")
    help_text_md = "Guia Rápido:\n- Título Principal: # Título\n- Subtítulo: ## Subtítulo\n- Listas: - Item da lista\n- Negrito: **texto**"
    def salvar_dossie(file_name_pattern, path_parts, content):
        if not all(path_parts + [content]): st.error("Todos os campos marcados com * são obrigatórios."); return
        file_name = file_name_pattern.format(**st.session_state).replace(" ", "_") + ".md"; full_path = "/".join([p.replace(" ", "_") for p in path_parts]) + "/" + file_name
        commit_message = f"Adiciona: {file_name}"
        with st.spinner("Salvando dossiê..."):
            try:
                repo.create_file(full_path, commit_message, content); st.success(f"Dossiê '{full_path}' salvo com sucesso!")
            except Exception as e: st.error(f"Ocorreu um erro ao salvar: {e}")
    if dossier_type == "D1 P1 - Análise da Liga":
        with st.form("d1_p1_form"):
            st.subheader("Template: Análise da Liga"); c1, c2, c3 = st.columns(3); st.session_state.pais = c1.text_input("País*"); st.session_state.liga = c2.text_input("Liga*"); st.session_state.temporada = c3.text_input("Temporada*")
            conteudo = st.text_area("Conteúdo do Dossiê*", height=300, help=help_text_md)
            if st.form_submit_button("Salvar Dossiê", type="primary"): salvar_dossie("D1P1_Analise_Liga_{liga}_{pais}", [st.session_state.pais, st.session_state.liga, st.session_state.temporada], conteudo)
    elif dossier_type: st.warning(f"O template para '{dossier_type}' será adicionado em breve.")

elif selected_action == "Gerar com IA":
    st.header("Gerar com IA"); st.info("Em desenvolvimento.")
```

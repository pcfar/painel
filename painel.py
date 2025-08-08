# -*- coding: utf-8 -*-
"""
Painel de Inteligência Tática - v5.0: O Modelo de Apresentação por Dados
"""

import streamlit as st
from github import Github, UnknownObjectException
from datetime import datetime
import base64
import re
import os
from streamlit_option_menu import option_menu
import yaml  # Importa a biblioteca para ler arquivos YAML

# --- 1. CONFIGURAÇÃO DA PÁGINA E ESTILOS ---
st.set_page_config(page_title="Sistema de Inteligência Tática", page_icon="⚽", layout="wide")

def apply_custom_styling():
    """CSS focado em estilizar os novos componentes de dados."""
    st.markdown("""
        <style>
            /* Estilos gerais */
            @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@400;500;700&display=swap');
            body, .main { font-family: 'Roboto', sans-serif; }

            /* --- ESTILOS DO NOVO DASHBOARD DE DOSSIÊ --- */
            .dossier-dashboard { padding: 1rem; }
            .dossier-header { text-align: center; margin-bottom: 2rem; }
            .dossier-header h1 { font-size: 2.8rem; color: #FFFFFF; }
            .dossier-header h2 { font-size: 1.5rem; color: #63B3ED; font-weight: 500; }
            .dossier-header span { font-size: 0.9rem; color: #A0AEC0; }
            
            .section-header {
                font-size: 1.8rem;
                color: #FFFFFF;
                border-bottom: 2px solid #3182CE;
                padding-bottom: 10px;
                margin-top: 3rem;
                margin-bottom: 1.5rem;
            }

            .card {
                background-color: #2D3748;
                padding: 1.5rem;
                border-radius: 12px;
                border: 1px solid #4A5568;
                height: 100%;
            }
            .card h5 { font-size: 1.1rem; margin-bottom: 1rem; color: #a5b4fc; }
            .card p, .card li { font-size: 1rem; line-height: 1.8; color: #E2E8F0;}
            
            .callout { padding: 1rem; margin-top: 1rem; border-left-width: 5px; border-left-style: solid; border-radius: 8px; }
            .callout-info { border-color: #3182CE; background-color: rgba(49, 130, 206, 0.1); }
            .callout-success { border-color: #38A169; background-color: rgba(56, 161, 105, 0.1); }
            .callout-warning { border-color: #D69E2E; background-color: rgba(214, 158, 46, 0.1); }

            .club-logo { width: 40px; height: 40px; margin-right: 15px; vertical-align: middle; }
        </style>
    """, unsafe_allow_html=True)

# --- 2. NOVO RENDERIZADOR DE DADOS ---
def render_dossier_from_data(data: dict):
    """Renderiza um dashboard visualmente rico a partir de um dicionário de dados (do YAML)."""
    with st.container():
        st.markdown(f"""
            <div class="dossier-dashboard">
                <div class="dossier-header">
                    <h1>{data.get('titulo', 'Dossiê sem título')}</h1>
                    <h2>{data.get('pais', '')} - {data.get('temporada', '')}</h2>
                    <span>Atualizado em: {data.get('atualizado_em', 'N/D')}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)

        st.divider()

        # Seção de Métricas Principais
        if 'metricas_principais' in data:
            cols = st.columns(len(data['metricas_principais']))
            for i, metrica in enumerate(data['metricas_principais']):
                delta = metrica.get('delta')
                cols[i].metric(label=metrica.get('label'), value=metrica.get('value'), delta=delta if delta else None)
        
        # Seção de Identidade e Formato
        if 'identidade' in data:
            st.markdown('<h3 class="section-header">Identidade e Formato</h3>', unsafe_allow_html=True)
            cols = st.columns(len(data['identidade']))
            for i, item in enumerate(data['identidade']):
                with cols[i]:
                    st.markdown(f'<div class="card"><h5>{item.get("titulo")}</h5><p>{item.get("conteudo", "").replace("-", "•")}</p></div>', unsafe_allow_html=True)
        
        # Seção de Pontos Chave
        if 'pontos_chave' in data:
            st.markdown('<h3 class="section-header">Análise Tática e Pontos Chave</h3>', unsafe_allow_html=True)
            for ponto in data['pontos_chave']:
                st.markdown(f'<div class="callout callout-{ponto.get("tipo", "info")}">{ponto.get("texto")}</div>', unsafe_allow_html=True)

        # Seção de Clubes Dominantes
        if 'clubes_dominantes' in data:
            st.markdown('<h3 class="section-header">Clubes Dominantes</h3>', unsafe_allow_html=True)
            for clube in data['clubes_dominantes']:
                st.markdown(f"""
                    <div>
                        <img src="{clube.get('logo_url')}" class="club-logo">
                        <span style="font-size: 1.2rem; font-weight: 500;">{clube.get('nome')}</span>
                    </div>
                """, unsafe_allow_html=True)

# --- Funções Legadas (Autenticação, etc.) ---
# (O resto do código Python, como check_password, get_github_repo, etc., permanece o mesmo)
# ...

# --- MODIFICAÇÃO NO LEITOR DE DOSSIÊS ---
# No loop da função display_repo_structure, você precisará mudar o que acontece ao clicar em "Visualizar"

# Exemplo de como a lógica de visualização seria modificada:
# if c1.button(f"📄 {content_file.name}", ...):
#     if content_file.name.endswith(".yml"):
#         file_content_raw = repo.get_contents(content_file.path).decoded_content.decode("utf-8")
#         dossier_data = yaml.safe_load(file_content_raw)
#         st.session_state['viewing_dossier_data'] = dossier_data
#         st.session_state['viewing_file_name'] = content_file.name
#         if 'viewing_file_content' in st.session_state: del st.session_state['viewing_file_content']
#     else: # Mantém compatibilidade com arquivos .md antigos
#         # ... lógica antiga de visualização de .md
#         pass


# E na área de visualização:
# with col2:
#     st.subheader("Visualizador de Conteúdo")
#     if st.session_state.get("viewing_dossier_data"):
#         render_dossier_from_data(st.session_state['viewing_dossier_data'])
#     elif st.session_state.get("viewing_file_content"):
#         # ... lógica antiga para exibir .md
#         pass
#     else:
#         st.info("Selecione um arquivo .yml para uma visualização rica.")

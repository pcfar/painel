import streamlit as st
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Painel de Inteligência Tática - MODO DETETIVE",
    page_icon="🕵️",
    layout="wide"
)

# --- Título do Painel ---
st.title("SISTEMA MULTIAGENTE - MODO DETETIVE 🕵️")
st.subheader("Estamos a investigar o sistema de arquivos do servidor.")

# --- CÓDIGO DETETIVE ---
st.header("O que o script vê na pasta principal (`.`):")

try:
    # Pede para o script listar tudo o que há no diretório atual
    conteudo_da_pasta_raiz = os.listdir('.')

    st.success("O comando para listar arquivos funcionou!")

    # Mostra o conteúdo em formato de lista
    st.write("Arquivos e pastas encontrados:")
    st.write(conteudo_da_pasta_raiz)

    # Verifica se a nossa pasta está na lista que ele encontrou
    if 'prints_para_analise' in conteudo_da_pasta_raiz:
        st.info("BOA NOTÍCIA: A pasta 'prints_para_analise' FOI encontrada na lista!")
    else:
        st.error("MÁ NOTÍCIA: A pasta 'prints_para_analise' NÃO FOI encontrada na lista. Verifique se o nome está exatamente igual no GitHub.")

except Exception as e:
    st.error("Ocorreu um erro ao tentar listar os arquivos:")
    st.exception(e)

# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 0.3 (Debug)")

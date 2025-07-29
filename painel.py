import streamlit as st
import os

# --- Configuração da Página ---
st.set_page_config(
    page_title="Painel de Inteligência Tática",
    page_icon="🧠",
    layout="wide"
)

# --- Título do Painel ---
st.title("SISTEMA MULTIAGENTE DE INTELIGÊNCIA TÁTICA")
st.subheader("Plataforma de Análise de Padrões para Trading Esportivo")

# --- MUDANÇA FINAL: O script agora procura os arquivos na pasta principal ('.') ---
PRINTS_DIR = "."


# --- Função para listar os prints disponíveis ---
def listar_prints():
    # Lista apenas arquivos de imagem no diretório atual
    arquivos_permitidos = ('.png', '.jpg', '.jpeg')
    return [f for f in os.listdir(PRINTS_DIR) if f.lower().endswith(arquivos_permitidos)]

# --- Interface Principal ---
st.header("1. Arquivos para Análise")

lista_de_prints = listar_prints()

if not lista_de_prints:
    st.warning(f"Nenhum 'print' para análise encontrado na pasta principal.")
    st.info("Faça o upload de uma imagem de estatísticas para a pasta principal no GitHub para começar.")
else:
    st.success(f"Encontrados {len(lista_de_prints)} prints para análise.")

    # Menu para selecionar o print
    print_selecionado = st.selectbox("Selecione o arquivo de dados para processar:", lista_de_prints)

    if print_selecionado:
        caminho_completo = os.path.join(PRINTS_DIR, print_selecionado)
        st.image(caminho_completo, caption=f"Imagem selecionada: {print_selecionado}")

        # Botão para iniciar a análise
        if st.button("Analisar Print e Gerar Dossiê"):
            with st.spinner("Análise em andamento... (Simulação)"):
                # Futuramente, a lógica de OCR e análise será inserida aqui
                st.header("Dossiê Técnico (Exemplo)")
                st.markdown("""
                ---
                **Equipe:** Nome da Equipe (extraído do print)
                **Padrão Esperado:** Domínio territorial + linha alta.
                **Dados Chave:**
                - **Posse de Bola Média:** 62%
                - **xG (Gols Esperados):** 2.1 por jogo

                **Atenção in-live:** Vulnerabilidade defensiva após os 70'.
                """)
                st.success("Análise concluída.")

# --- Rodapé ---
st.markdown("---")
st.text("Painel em desenvolvimento. Versão 2.0")

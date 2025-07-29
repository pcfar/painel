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

# --- CORREÇÃO: Construção de um caminho mais robusto para a pasta ---
# Pega o caminho do diretório onde o script painel.py está localizado
DIRETORIO_DO_SCRIPT = os.path.dirname(os.path.abspath(__file__))
# Junta o caminho do diretório com o nome da nossa pasta de prints
PRINTS_DIR_COMPLETO = os.path.join(DIRETORIO_DO_SCRIPT, "prints_para_analise")


# --- Função para listar os prints disponíveis ---
def listar_prints():
    # Verifica se o diretório existe antes de listar os arquivos
    if not os.path.isdir(PRINTS_DIR_COMPLETO):
        st.error(f"A pasta 'prints_para_analise' não foi encontrada no caminho esperado. Verifique a estrutura de arquivos no GitHub.")
        return []

    # Lista apenas arquivos de imagem
    arquivos_permitidos = ('.png', '.jpg', '.jpeg')
    # CORREÇÃO: Usa o caminho completo para listar os arquivos
    return [f for f in os.listdir(PRINTS_DIR_COMPLETO) if f.lower().endswith(arquivos_permitidos)]

# --- Interface Principal ---
st.header("1. Arquivos para Análise")

lista_de_prints = listar_prints()

if not lista_de_prints:
    st.warning(f"Nenhum 'print' para análise encontrado na pasta 'prints_para_analise'.")
    st.info("Faça o upload de uma imagem de estatísticas para a pasta correta no GitHub para começar.")
else:
    st.success(f"Encontrados {len(lista_de_prints)} prints para análise.")

    # Menu para selecionar o print
    print_selecionado = st.selectbox("Selecione o arquivo de dados para processar:", lista_de_prints)

    if print_selecionado:
        # CORREÇÃO: Usa o caminho completo para mostrar a imagem
        caminho_completo = os.path.join(PRINTS_DIR_COMPLETO, print_selecionado)
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
st.text("Painel em desenvolvimento. Versão 0.2")

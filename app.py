import streamlit as st
import PyPDF2
import os
from openai import OpenAI
from dotenv import load_dotenv  # Para carregar variáveis do .env

# Carregar variáveis do .env
load_dotenv()

# Obter a chave da API do ambiente
api_key = os.getenv("OPENAI_API_KEY")

# Verificar se a API Key está definida
if not api_key:
    st.error("⚠️ A chave da API OpenAI não foi encontrada. Verifique o arquivo .env.")
    st.stop()

client = OpenAI(api_key=api_key)

# Diretório onde os PDFs estão armazenados
PDF_FOLDER = "pdfs/"

# Função para extrair texto do PDF
def extrair_texto_pdf(pdf_path):
    texto = ""
    with open(pdf_path, "rb") as arquivo:
        leitor = PyPDF2.PdfReader(arquivo)
        for pagina in range(len(leitor.pages)):
            texto += leitor.pages[pagina].extract_text() + "\n"
    return texto

# Configuração da página
st.set_page_config(page_title="RAG com IA e PDFs", page_icon="📄", layout="wide")

# Inicializar sessão para manter histórico e pergunta
if "historico" not in st.session_state:
    st.session_state.historico = []
if "pergunta" not in st.session_state:
    st.session_state.pergunta = ""

# Interface estilizada
st.markdown('<h1 class="main-title">📄🔍 RAG com IA e PDFs</h1>', unsafe_allow_html=True)
st.markdown('<p class="sub-title">Pesquise conteúdos em documentos PDF com ajuda da IA!</p>', unsafe_allow_html=True)

# Carregar PDFs da pasta
pdf_files = [f for f in os.listdir(PDF_FOLDER) if f.endswith(".pdf")]

if not pdf_files:
    st.error("⚠️ Nenhum PDF encontrado na pasta 'pdfs/'. Adicione arquivos e reinicie o app.")
else:
    col1, col2 = st.columns([2, 3])

    with col1:
        selected_pdf = st.selectbox("📂 Escolha um PDF para pesquisa:", pdf_files)

    if selected_pdf:
        pdf_path = os.path.join(PDF_FOLDER, selected_pdf)

        with col2:
            pergunta = st.text_input("❓ Digite sua pergunta:", value=st.session_state.pergunta, key="input_pergunta")

        if st.button("🔎 Pesquisar", key="pesquisar"):
            if pergunta:
                with st.spinner("Aguarde... Buscando resposta..."):
                    texto_pdf = extrair_texto_pdf(pdf_path)
                    contexto = "\n".join([f"Pergunta: {h['pergunta']}\nResposta: {h['resposta']}" for h in st.session_state.historico])

                    prompt = f"Baseado no seguinte documento:\n\n{texto_pdf}\n\nHistórico da conversa:\n{contexto}\n\nPergunta: {pergunta}\nResposta:"
                    
                    try:
                        completion = client.chat.completions.create(
                            model="gpt-4o-mini",
                            messages=[{"role": "user", "content": prompt}],
                            max_tokens=200
                        )
                        resposta = completion.choices[0].message.content

                        # Adicionar ao histórico
                        st.session_state.historico.append({"pergunta": pergunta, "resposta": resposta})

                        st.success("✅ Resposta gerada com sucesso!")
                        st.markdown(f'<div class="historico-box"><strong>❓ Pergunta:</strong> {pergunta}<br><strong>💡 Resposta:</strong> {resposta}</div>', unsafe_allow_html=True)

                        # 🔥 Limpar o campo de pergunta
                        st.session_state.pergunta = ""
                        st.rerun()

                    except Exception as e:
                        st.error(f"Erro ao consultar IA: {e}")
            else:
                st.warning("⚠️ Digite uma pergunta antes de pesquisar.")

        # Exibir histórico de perguntas e respostas
        if st.session_state.historico:
            st.subheader("📜 Histórico de Perguntas")
            for h in reversed(st.session_state.historico):
                st.markdown(f'<div class="historico-box"><strong>❓ {h["pergunta"]}</strong><br>💡 {h["resposta"]}</div>', unsafe_allow_html=True)
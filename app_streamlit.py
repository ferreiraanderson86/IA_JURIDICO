import streamlit as st
import tempfile
import os
from docx import Document
from analisador import ler_arquivo, gerar_analise, gerar_resposta_chat

st.set_page_config(page_title="Plataforma Jurídica IA", layout="wide")
st.title("⚖️ Plataforma Jurídica com IA")

# ------------------------------
# Session State
# ------------------------------
if "analises" not in st.session_state:
    st.session_state.analises = {}

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "area" not in st.session_state:
    st.session_state.area = "Civil"

# ------------------------------
# Área Jurídica
# ------------------------------
area = st.selectbox("Escolha a área jurídica:", ["Civil", "Criminal", "Bancário", "Tributário"])
st.session_state.area = area

def get_prompt_sistema(area: str) -> str:
    base = (
        "Você é um advogado brasileiro experiente, redator técnico jurídico, "
        "especializado em {area}. Você deve responder de forma clara, fundamentada, precisa e formal, "
        "utilizando linguagem adequada ao meio jurídico e considerando as normas vigentes no Brasil. "
        "Sempre que possível, fundamente suas respostas com base em legislação, jurisprudência atualizada, "
        "doutrina majoritária e boas práticas processuais."
    )

    if area == "Civil":
        return base.format(area="Direito Civil") + (
            " Foque no Código Civil, Código de Processo Civil, enunciados das Jornadas de Direito Civil do CJF, "
            "e jurisprudência do STJ e STF. Considere contratos, obrigações, responsabilidade civil, família e sucessões."
        )

    elif area == "Criminal":
        return base.format(area="Direito Penal") + (
            " Utilize o Código Penal, Código de Processo Penal, jurisprudência do STJ e STF, "
            "incluindo súmulas e precedentes relevantes. Fundamente defesas, recursos, habeas corpus e medidas cautelares."
        )

    elif area == "Bancário":
        return base.format(area="Direito Bancário e do Consumidor") + (
            " Baseie-se no Código de Defesa do Consumidor (CDC), resoluções do Banco Central (BACEN), "
            "jurisprudência do STJ, contratos bancários e práticas abusivas. Considere revisão de cláusulas, juros abusivos "
            "e ações revisionais de contrato."
        )

    elif area == "Tributário":
        return base.format(area="Direito Tributário") + (
            " Fundamente suas respostas no Código Tributário Nacional (CTN), Constituição Federal, "
            "legislação infraconstitucional, decisões do CARF, e jurisprudência do STJ e STF. "
            "Considere também princípios como legalidade, anterioridade e capacidade contributiva."
        )

    return base.format(area="Direito") + " Atue como um advogado generalista bem preparado e objetivo."


# Inicializa histórico com prompt da área
if not st.session_state.chat_history:
    st.session_state.chat_history.append({"role": "system", "content": get_prompt_sistema(area)})

# Se já houver análises feitas, adicione como contexto
if st.session_state.analises:
    for nome, analise in st.session_state.analises.items():
        st.session_state.chat_history.append({
            "role": "assistant",
            "content": (
                f"Análise anterior do documento **{nome}**:\n\n"
                f"{analise[:3000]}"
            )
        })

# ------------------------------
# Upload de Arquivos
# ------------------------------
uploaded_files = st.file_uploader(
    "📎 Envie um ou mais arquivos (PDF, DOCX, imagens, Excel)", 
    type=["pdf", "docx", "png", "jpg", "jpeg", "xls", "xlsx"], 
    accept_multiple_files=True
)

col1, col2 = st.columns([1, 1])

# ------------------------------
# Analisar contratos (Civil e Bancário)
# ------------------------------
if area in ["Civil", "Bancário"] and uploaded_files:
    with col1:
        if st.button("🔍 Analisar Contratos"):
            for up in uploaded_files:
                try:
                    with st.spinner(f"Analisando {up.name}..."):
                        texto = ler_arquivo(up)
                        analise = gerar_analise(texto, area=area)
                        st.session_state.analises[up.name] = analise
                        st.session_state.chat_history.append(
                            {"role": "assistant", "content": f"Análise do contrato {up.name}:\n{analise}"}
                        )
                except Exception as e:
                    st.error(f"Erro ao analisar {up.name}: {e}")

# ------------------------------
# Limpar análises
# ------------------------------
with col2:
    if st.session_state.analises and st.button("🗑 Limpar análises"):
        st.session_state.analises = {}

# ------------------------------
# Exibição das análises
# ------------------------------
if st.session_state.analises:
    st.subheader("📑 Análises geradas")

    for nome, analise in st.session_state.analises.items():
        with st.expander(f"{nome}"):
            st.text_area("Parecer Jurídico", analise, height=350)

            st.download_button(
                "⬇ Baixar parecer",
                analise.encode("utf-8"),
                file_name=f"parecer_{nome}.txt",
                mime="text/plain"
            )

            if st.button(f"✍ Gerar Petição Inicial para {nome}"):
                with st.spinner("Gerando petição inicial..."):
                    try:
                        doc = Document()
                        doc.add_heading("Petição Inicial", 0)
                        doc.add_paragraph(analise)
                        peticao_path = os.path.join(tempfile.gettempdir(), f"peticao_inicial_{nome}.docx")
                        doc.save(peticao_path)

                        with open(peticao_path, "rb") as f:
                            st.download_button(
                                f"⬇ Baixar Petição ({nome})",
                                f,
                                file_name=f"peticao_inicial_{nome}.docx",
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    except Exception as e:
                        st.error(f"Erro ao gerar petição: {e}")
else:
    st.info("Nenhuma análise disponível ainda.")

# ------------------------------
# Chat Jurídico
# ------------------------------
st.divider()
st.subheader(f"💬 Chat Jurídico – Área: {area}")

# Exibe histórico
for msg in st.session_state.chat_history:
    if msg["role"] == "user":
        with st.chat_message("user"):
            st.markdown(msg["content"])
    elif msg["role"] == "assistant":
        with st.chat_message("assistant"):
            st.markdown(msg["content"])

# Entrada do chat
if prompt := st.chat_input("Digite sua pergunta para a IA jurídica"):
    st.session_state.chat_history.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Analisando..."):
            try:
                resposta = gerar_resposta_chat(st.session_state.chat_history)
                st.markdown(resposta)
                st.session_state.chat_history.append({"role": "assistant", "content": resposta})
            except Exception as e:
                st.error(f"Erro ao responder: {e}")

# ------------------------------
# Sidebar
# ------------------------------
with st.sidebar:
    st.header("⚙️ Configurações")
    if st.button("🧹 Limpar histórico do chat"):
        st.session_state.chat_history = [{"role": "system", "content": get_prompt_sistema(area)}]
    st.markdown("---")
    st.caption("Desenvolvido com ❤️ por você e IA")

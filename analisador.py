import os
import fitz  # PyMuPDF para ler PDF
import docx
from PIL import Image  # Para abrir imagens escaneadas
import pytesseract  # Para OCR (ler texto em imagens)
import pandas as pd  # Para planilhas Excel
import tempfile  # Para arquivos temporários
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Cliente OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# ------------------------------
# Função para ler qualquer tipo de arquivo aceito
# ------------------------------
def ler_arquivo(uploaded_file):
    suffix = os.path.splitext(uploaded_file.name)[-1].lower()

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(uploaded_file.read())
        caminho_arquivo = tmp.name

    try:
        if suffix == ".pdf":
            texto = ""
            with fitz.open(caminho_arquivo) as doc:
                for pagina in doc:
                    texto += pagina.get_text()
            return texto

        elif suffix == ".docx":
            doc = docx.Document(caminho_arquivo)
            return "\n".join([par.text for par in doc.paragraphs])

        elif suffix in [".png", ".jpg", ".jpeg"]:
            imagem = Image.open(caminho_arquivo)
            return pytesseract.image_to_string(imagem, lang='por')

        elif suffix in [".xls", ".xlsx"]:
            df = pd.read_excel(caminho_arquivo)
            return df.to_string(index=False)

        else:
            return "Formato de arquivo não suportado."

    finally:
        os.remove(caminho_arquivo)

# ------------------------------
# Prompt do sistema por área jurídica
# ------------------------------
def get_prompt_sistema(area: str) -> str:
    base = (
        "Você é um advogado brasileiro altamente experiente, com excelente redação técnica jurídica, "
        "especializado em {area}. Suas respostas devem ser claras, objetivas, juridicamente fundamentadas e redigidas "
        "em linguagem formal e técnica, adequada ao meio jurídico brasileiro. Sempre que possível, utilize "
        "fundamentação baseada na legislação vigente, jurisprudência atual (preferencialmente dos tribunais superiores), "
        "doutrina majoritária e boas práticas processuais."
    )

    if area == "Civil":
        return base.format(area="Direito Civil") + (
            " Foque no Código Civil, Código de Processo Civil, enunciados das Jornadas de Direito Civil do CJF, "
            "e jurisprudência do STJ e STF. Aborde temas como contratos, obrigações, responsabilidade civil, direito de família e sucessões."
        )

    elif area == "Criminal":
        return base.format(area="Direito Penal") + (
            " Fundamente-se no Código Penal, Código de Processo Penal, jurisprudência do STJ e STF, súmulas e precedentes. "
            "Considere estratégias de defesa, recursos, habeas corpus e medidas cautelares."
        )

    elif area == "Bancário":
        return base.format(area="Direito Bancário e do Consumidor") + (
            " Utilize o Código de Defesa do Consumidor (CDC), resoluções do Banco Central (BACEN), jurisprudência do STJ, "
            "e normas aplicáveis aos contratos bancários. Trate de cláusulas abusivas, juros excessivos, revisão contratual e práticas abusivas."
        )

    elif area == "Tributário":
        return base.format(area="Direito Tributário") + (
            " Fundamente suas análises no Código Tributário Nacional (CTN), Constituição Federal, legislação infraconstitucional, "
            "decisões do CARF, e jurisprudência do STJ e STF. Considere os princípios da legalidade, anterioridade, isonomia, "
            "e capacidade contributiva."
        )

    return base.format(area="Direito") + (
        " Atue como um advogado generalista com amplo domínio jurídico, oferecendo respostas precisas e bem fundamentadas."
    )


# ------------------------------
# Função para gerar análise jurídica
# ------------------------------

# Verifica se a área permite análise de contrato
def pode_analisar_contrato(area):
    return area in ["Civil", "Bancário"]

# Gera a análise jurídica resumida do texto
def gerar_analise(texto, area="Civil"):
    system_prompt = get_prompt_sistema(area)

    # Opcional: sanitizar texto para evitar caracteres indesejados
    texto = texto.encode("utf-8", errors="ignore").decode("utf-8", errors="ignore")

    mensagens = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": (
            f"Analise juridicamente o seguinte contrato ou documento. "
            f"Resuma a análise completa em no máximo 3000 caracteres:\n\n{texto}"
        )}
    ]

    resposta = client.chat.completions.create(
        model="gpt-4o",
        messages=mensagens,
        temperature=0.2
    )

    return resposta.choices[0].message.content

# ------------------------------
# Função de chat jurídico
# ------------------------------
def gerar_resposta_chat(mensagens, model="gpt-4o"):
    resposta = client.chat.completions.create(
        model=model,
        messages=mensagens,
        temperature=0.2,
    )
    return resposta.choices[0].message.content

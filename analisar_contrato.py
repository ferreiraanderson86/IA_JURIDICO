<<<<<<< HEAD
import os
import argparse
import pdfplumber
import docx
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------
# Configurações
# ---------------------------

SYSTEM_PROMPT_ANALISE = (
    "Você é um advogado brasileiro especialista em direito do consumidor e bancário. "
    "Analise o contrato enviado, identifique cláusulas potencialmente abusivas, riscos, "
    "fundamentação jurídica (CDC, STJ, Súmulas, artigos do CC, etc.), calcule/indique possíveis "
    "vantagens econômicas e sugira estratégias (administrativas e judiciais). "
    "Seja claro, objetivo, estruturado e aponte artigos/súmulas quando pertinente."
)

USER_PROMPT_TEMPLATE = """
Analise o seguinte contrato bancário (ou de prestação de serviços) e elabore um parecer jurídico completo contendo:

1) **Resumo do contrato** (partes, objeto, duração, valores, multas, foro, etc.)
2) **Pontos críticos / cláusulas potencialmente abusivas** (explique o porquê e cite fundamento legal/jurisprudencial)
3) **Riscos ao contratante**
4) **Fundamentação jurídica aplicável** (CDC, CC, STJ, súmulas, resoluções do BACEN, etc.)
5) **Estratégias e pedidos possíveis** (administrativas e judiciais)
6) **Documentos e provas que devem ser reunidos**
7) **Estimativa de vantagem econômica (se aplicável)**
8) **Modelo de pedidos (tópicos)**

Contrato (trecho ou inteiro):
\"\"\"{texto}\"\"\"
"""

SYSTEM_PROMPT_PETICAO = (
    "Você é um advogado brasileiro especialista em petições iniciais. "
    "Com base na análise jurídica fornecida, redija uma petição inicial completa, "
    "bem estruturada, com linguagem técnica adequada, incluindo endereçamento, qualificação das partes, "
    "fatos, fundamentos jurídicos (com artigos, súmulas, precedentes), pedidos (com tutela de urgência se couber), "
    "valor da causa, provas, e requerimentos finais."
)

USER_PROMPT_PETICAO = """
Use a análise jurídica abaixo para redigir a **petição inicial completa**.
Inclua: endereçamento, qualificação das partes (coloque campos para serem preenchidos), fatos, fundamentos jurídicos
(detalhados com artigos, súmulas e precedentes), pedidos, valor da causa (campo para preenchimento), provas, e requerimentos finais.
Se pertinente, inclua pedidos de tutela de urgência.

Análise jurídica:
\"\"\"{analise}\"\"\"
"""

# ---------------------------
# Leitura de arquivos
# ---------------------------

def ler_pdf(caminho: str) -> str:
    with pdfplumber.open(caminho) as pdf:
        textos = []
        for page in pdf.pages:
            txt = page.extract_text() or ""
            textos.append(txt)
    return "\n".join(textos)

def ler_docx(caminho: str) -> str:
    d = docx.Document(caminho)
    return "\n".join(p.text for p in d.paragraphs)

def ler_arquivo(caminho: str) -> str:
    ext = os.path.splitext(caminho.lower())[1]
    if ext == ".pdf":
        return ler_pdf(caminho)
    elif ext == ".docx":
        return ler_docx(caminho)
    else:
        raise ValueError("Formato não suportado. Use PDF ou DOCX.")

# ---------------------------
# OpenAI helpers
# ---------------------------

def get_client():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não encontrada. Defina no .env.")
    return OpenAI(api_key=api_key)

def call_chat_completion(client: OpenAI, system_prompt: str, user_prompt: str, model: str = "gpt-4o"):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    ).choices[0].message.content

# ---------------------------
# Lógica principal
# ---------------------------

def analisar_contrato(caminho_arquivo: str, model: str = "gpt-4o") -> str:
    texto = ler_arquivo(caminho_arquivo)

    # Se o contrato for muito grande, você pode optar por truncar ou fatiar.
    # Aqui, deixei simples. Ajuste se necessário.
    prompt_user = USER_PROMPT_TEMPLATE.format(texto=texto[:120000])  # ~120k chars de segurança

    client = get_client()
    analise = call_chat_completion(client, SYSTEM_PROMPT_ANALISE, prompt_user, model=model)
    return analise

def gerar_peticao(analise: str, model: str = "gpt-4o") -> str:
    client = get_client()
    user_prompt = USER_PROMPT_PETICAO.format(analise=analise)
    peticao = call_chat_completion(client, SYSTEM_PROMPT_PETICAO, user_prompt, model=model)
    return peticao

def salvar(texto: str, caminho: str):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

def main():
    parser = argparse.ArgumentParser(description="Analisar contrato bancário com GPT-4o e (opcional) gerar petição.")
    parser.add_argument("--arquivo", "-a", required=True, help="Caminho do contrato (PDF ou DOCX)")
    parser.add_argument("--saida", "-s", default="parecer.md", help="Arquivo de saída do parecer (.md)")
    parser.add_argument("--modelo", "-m", default="gpt-4o", help="Modelo (ex: gpt-4o, gpt-4.1, gpt-4o-mini)")
    parser.add_argument("--peticao", action="store_true", help="Gerar também a petição inicial com base na análise")
    parser.add_argument("--saida-peticao", default="peticao.md", help="Arquivo de saída da petição (.md)")
    args = parser.parse_args()

    print("👉 Lendo contrato...")
    try:
        analise = analisar_contrato(args.arquivo, model=args.modelo)
    except Exception as e:
        print("Erro ao analisar contrato:", e)
        return

    salvar(analise, args.saida)
    print(f"✅ Parecer salvo em: {args.saida}")

    if args.peticao:
        print("👉 Gerando petição inicial...")
        try:
            peticao = gerar_peticao(analise, model=args.modelo)
            salvar(peticao, args.saida_peticao)
            print(f"✅ Petição salva em: {args.saida_peticao}")
        except Exception as e:
            print("Erro ao gerar petição:", e)

if __name__ == "__main__":
    main()
=======
import os
import argparse
import pdfplumber
import docx
from dotenv import load_dotenv
from openai import OpenAI

# ---------------------------
# Configurações
# ---------------------------

SYSTEM_PROMPT_ANALISE = (
    "Você é um advogado brasileiro especialista em direito do consumidor e bancário. "
    "Analise o contrato enviado, identifique cláusulas potencialmente abusivas, riscos, "
    "fundamentação jurídica (CDC, STJ, Súmulas, artigos do CC, etc.), calcule/indique possíveis "
    "vantagens econômicas e sugira estratégias (administrativas e judiciais). "
    "Seja claro, objetivo, estruturado e aponte artigos/súmulas quando pertinente."
)

USER_PROMPT_TEMPLATE = """
Analise o seguinte contrato bancário (ou de prestação de serviços) e elabore um parecer jurídico completo contendo:

1) **Resumo do contrato** (partes, objeto, duração, valores, multas, foro, etc.)
2) **Pontos críticos / cláusulas potencialmente abusivas** (explique o porquê e cite fundamento legal/jurisprudencial)
3) **Riscos ao contratante**
4) **Fundamentação jurídica aplicável** (CDC, CC, STJ, súmulas, resoluções do BACEN, etc.)
5) **Estratégias e pedidos possíveis** (administrativas e judiciais)
6) **Documentos e provas que devem ser reunidos**
7) **Estimativa de vantagem econômica (se aplicável)**
8) **Modelo de pedidos (tópicos)**

Contrato (trecho ou inteiro):
\"\"\"{texto}\"\"\"
"""

SYSTEM_PROMPT_PETICAO = (
    "Você é um advogado brasileiro especialista em petições iniciais. "
    "Com base na análise jurídica fornecida, redija uma petição inicial completa, "
    "bem estruturada, com linguagem técnica adequada, incluindo endereçamento, qualificação das partes, "
    "fatos, fundamentos jurídicos (com artigos, súmulas, precedentes), pedidos (com tutela de urgência se couber), "
    "valor da causa, provas, e requerimentos finais."
)

USER_PROMPT_PETICAO = """
Use a análise jurídica abaixo para redigir a **petição inicial completa**.
Inclua: endereçamento, qualificação das partes (coloque campos para serem preenchidos), fatos, fundamentos jurídicos
(detalhados com artigos, súmulas e precedentes), pedidos, valor da causa (campo para preenchimento), provas, e requerimentos finais.
Se pertinente, inclua pedidos de tutela de urgência.

Análise jurídica:
\"\"\"{analise}\"\"\"
"""

# ---------------------------
# Leitura de arquivos
# ---------------------------

def ler_pdf(caminho: str) -> str:
    with pdfplumber.open(caminho) as pdf:
        textos = []
        for page in pdf.pages:
            txt = page.extract_text() or ""
            textos.append(txt)
    return "\n".join(textos)

def ler_docx(caminho: str) -> str:
    d = docx.Document(caminho)
    return "\n".join(p.text for p in d.paragraphs)

def ler_arquivo(caminho: str) -> str:
    ext = os.path.splitext(caminho.lower())[1]
    if ext == ".pdf":
        return ler_pdf(caminho)
    elif ext == ".docx":
        return ler_docx(caminho)
    else:
        raise ValueError("Formato não suportado. Use PDF ou DOCX.")

# ---------------------------
# OpenAI helpers
# ---------------------------

def get_client():
    load_dotenv()
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY não encontrada. Defina no .env.")
    return OpenAI(api_key=api_key)

def call_chat_completion(client: OpenAI, system_prompt: str, user_prompt: str, model: str = "gpt-4o"):
    return client.chat.completions.create(
        model=model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        temperature=0.2,
    ).choices[0].message.content

# ---------------------------
# Lógica principal
# ---------------------------

def analisar_contrato(caminho_arquivo: str, model: str = "gpt-4o") -> str:
    texto = ler_arquivo(caminho_arquivo)

    # Se o contrato for muito grande, você pode optar por truncar ou fatiar.
    # Aqui, deixei simples. Ajuste se necessário.
    prompt_user = USER_PROMPT_TEMPLATE.format(texto=texto[:120000])  # ~120k chars de segurança

    client = get_client()
    analise = call_chat_completion(client, SYSTEM_PROMPT_ANALISE, prompt_user, model=model)
    return analise

def gerar_peticao(analise: str, model: str = "gpt-4o") -> str:
    client = get_client()
    user_prompt = USER_PROMPT_PETICAO.format(analise=analise)
    peticao = call_chat_completion(client, SYSTEM_PROMPT_PETICAO, user_prompt, model=model)
    return peticao

def salvar(texto: str, caminho: str):
    with open(caminho, "w", encoding="utf-8") as f:
        f.write(texto)

def main():
    parser = argparse.ArgumentParser(description="Analisar contrato bancário com GPT-4o e (opcional) gerar petição.")
    parser.add_argument("--arquivo", "-a", required=True, help="Caminho do contrato (PDF ou DOCX)")
    parser.add_argument("--saida", "-s", default="parecer.md", help="Arquivo de saída do parecer (.md)")
    parser.add_argument("--modelo", "-m", default="gpt-4o", help="Modelo (ex: gpt-4o, gpt-4.1, gpt-4o-mini)")
    parser.add_argument("--peticao", action="store_true", help="Gerar também a petição inicial com base na análise")
    parser.add_argument("--saida-peticao", default="peticao.md", help="Arquivo de saída da petição (.md)")
    args = parser.parse_args()

    print("👉 Lendo contrato...")
    try:
        analise = analisar_contrato(args.arquivo, model=args.modelo)
    except Exception as e:
        print("Erro ao analisar contrato:", e)
        return

    salvar(analise, args.saida)
    print(f"✅ Parecer salvo em: {args.saida}")

    if args.peticao:
        print("👉 Gerando petição inicial...")
        try:
            peticao = gerar_peticao(analise, model=args.modelo)
            salvar(peticao, args.saida_peticao)
            print(f"✅ Petição salva em: {args.saida_peticao}")
        except Exception as e:
            print("Erro ao gerar petição:", e)

if __name__ == "__main__":
    main()
>>>>>>> 84bc48d03e12871b7a7bf01d0c98fbf1f1bbbe91

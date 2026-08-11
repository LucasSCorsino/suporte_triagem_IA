import os
import json
import csv
from dotenv import load_dotenv
from google import genai

# Usado para carregar a variável de ambiente do arquivo .env
load_dotenv()

# pega a chave da api que foi carregada no arquivo .env
api_key = os.getenv("GEMINI_API_KEY")

# Configura o SDK do Gemini com a chave
client = genai.Client(api_key=api_key)

# lista das mensagens (mockadas) dos supostos clientes que serão analisadas pelo modelo
mensagens_clientes = [ "Meu acesso foi bloqueado e eu preciso enviar um relatório hoje! Isso é urgente!",
    "Queria saber se vocês abrem aos sábados.",
    "Fui cobrado duas vezes no cartão esse mês, quero meu dinheiro de volta AGORA.",
    "Gostaria de saber mais sobre os planos empresariais que vocês oferecem."]

# função que analisa a mensagem e retorna um json com a estrutura solicitada, que será usado como resposta para o cliente
def analisar_mensagens(texto_cliente):

    prompt = f"""
    Você é um assistente de triagem de atendimento ao cliente.
    Analise a mensagem do cliente abaixo e retorne SOMENTE um JSON válido, 
    sem texto adicional, sem markdown, seguindo exatamente esta estrutura:

    {{
        "sentimento": "Irritado" ou "Neutro" ou "Satisfeito",
        "urgencia": "Alta" ou "Média" ou "Baixa",
        "setor_recomendado": "Financeiro" ou "Suporte Técnico" ou "Comercial"
    }}

    Mensagem do cliente: "{texto_cliente}"
    """

    resposta = client.models.generate_content(
    model="gemini-3.6-flash",
    contents=prompt
)
    texto_resposta = resposta.text.strip()
    
    # Remove possíveis marcações de markdown geradas pelo modelo, como ```json e ``` no início e no fim da resposta
    texto_resposta = texto_resposta.replace("```json", "").replace("```", "").strip()
    
    try:
        resultado = json.loads(texto_resposta)
        return resultado
    except json.JSONDecodeError:
        print(f"⚠️ Erro ao interpretar resposta da IA para: {texto_cliente}")
        return None

    # aqui de fato estamos usando a função, esse bloco vai criar uma lista de resultados com as análises das mensagens dos clientes

def salvar_resultados_csv(resultados, nome_arquivo="resultados_triagem.csv"):
    # trava de segurança, caso a análise falhar, devido a trava anterior, pode ser que a lista "resultados" esteja vazia.
    if not resultados:
        print("Nenhum resultado para salvar.")
        return

    colunas = resultados[0].keys() # pega as chaves do primeiro dicionario da lista, e usa como cabeçalho. Isso funciona pois os dicionários tem a mesma estrutura

    with open(nome_arquivo, mode="w", newline="", encoding="utf-8") as arquivo_csv:
        escritor = csv.DictWriter(arquivo_csv, fieldnames=colunas)
        escritor.writeheader()
        escritor.writerows(resultados)

    print(f"✅ Resultados salvos em: {nome_arquivo}")

if __name__ == "__main__": #não é necessário nesse momento, mas adicionei pois é uma boa prática 
    resultados = []
    
    print("Iniciando análise de tickets...\n")
    
    for mensagem in mensagens_clientes:
        print(f"Analisando: \"{mensagem}\"")
        analise = analisar_mensagens(mensagem)
        
        if analise:
            print(f"  → Sentimento: {analise['sentimento']}")
            print(f"  → Urgência: {analise['urgencia']}")
            print(f"  → Setor recomendado: {analise['setor_recomendado']}\n")
            
            resultados.append({
                "mensagem": mensagem,
                "sentimento": analise["sentimento"],
                "urgencia": analise["urgencia"],
                "setor_recomendado": analise["setor_recomendado"]
            })
        else:
            print("  → Não foi possível analisar esta mensagem.\n")

    salvar_resultados_csv(resultados)
import os
import json
from dotenv import load_dotenv
import google.generativeai as genai

# Usado para carregar a variável de ambiente do arquivo .env
load_dotenv()

# pega a chave da api que foi carregada no arquivo .env
api_key = os.getenv("GEMINI_API_KEY")

# Configura o SDK do Gemini com a chave
genai.configure(api_key=api_key)

# lista das mensagens (mockadas) dos supostos clientes que serão analisadas pelo modelo
mensagens_clientes = [ "Meu acesso foi bloqueado e eu preciso enviar um relatório hoje! Isso é urgente!",
    "Queria saber se vocês abrem aos sábados.",
    "Fui cobrado duas vezes no cartão esse mês, quero meu dinheiro de volta AGORA.",
    "Gostaria de saber mais sobre os planos empresariais que vocês oferecem."]

# função que analisa a mensagem e retorna um json com a estrutura solicitada, que será usado como resposta para o cliente
def analisar_mensagens(texto_cliente):
    modelo = genai.GenerativeModel("gemini-2.5-flash")

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

    resposta = modelo.generate_content(prompt)
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
import openai
import configparser


def analisar_resultados(resultados):
    """
    Envia os resultados para a API OpenAI para análise e sumarização.
    :param resultados: lista de dicionários com os dados dos produtos
    :return: texto com a análise/sumarização
    """
    if not resultados:
        return "Nenhum resultado para analisar."

    # Ler chave da API do arquivo config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        api_key = config['openai']['api_key']
    except KeyError:
        return "Chave da API OpenAI não encontrada no arquivo config.ini."

    # Configurar a chave da API
    openai.api_key = api_key

    # Construir prompt com os dados dos produtos
    prompt = "Analise e resuma os seguintes resultados de cotações de materiais:\n\n"
    for i, produto in enumerate(resultados, 1):
        prompt += (
            f"{i}. Nome: {produto.get('nome', '')}\n"
            f"   Preço: {produto.get('preco', '')}\n"
            f"   Descrição: {produto.get('descricao', '')}\n"
            f"   Fornecedor: {produto.get('fornecedor', '')}\n"
            f"   Link: {produto.get('link', '')}\n\n"
        )

    prompt += (
        "Forneça um resumo dos melhores fornecedores e preços, "
        "e sugestões para o usuário."
    )

    try:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "Você é um assistente que ajuda a analisar cotações de materiais.",
                },
                {"role": "user", "content": prompt},
            ],
            max_tokens=500,
            temperature=0.7,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        # Tratamento específico para erro de cota excedida
        if "insufficient_quota" in str(e):
            return ("Erro: Cota da API OpenAI excedida. "
                    "Por favor, verifique seu plano e detalhes de cobrança.")
        return f"Erro ao analisar resultados via OpenAI: {str(e)}"

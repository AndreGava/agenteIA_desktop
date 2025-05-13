import requests
import configparser


def analisar_resultados_deepseek(resultados):
    """
    Envia os resultados para o serviço DeepSeek para análise e sumarização.
    :param resultados: lista de dicionários com os dados dos produtos
    :return: texto com a análise/sumarização
    """
    if not resultados:
        return "Nenhum resultado para analisar."

    # Ler chave da API do arquivo config.ini
    config = configparser.ConfigParser()
    config.read('config.ini')
    try:
        api_key = config['deepseek']['api_key']
    except KeyError:
        return "Chave da API DeepSeek não encontrada no arquivo config.ini."

    # Construir payload com os dados dos produtos
    payload = {
        "documents": resultados,
        "task": "analyze_and_summarize"
    }

    # URL do serviço DeepSeek (ajustar conforme a configuração local/remota)
    deepseek_url = "https://api.deepseek.com"

    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    try:
        response = requests.post(
            deepseek_url,
            json=payload,
            headers=headers,
            timeout=30
        )
        response.raise_for_status()
        data = response.json()
        return data.get("summary", "Nenhum resumo retornado pelo DeepSeek.")
    except requests.exceptions.RequestException as e:
        return f"Erro ao analisar resultados via DeepSeek: {str(e)}"

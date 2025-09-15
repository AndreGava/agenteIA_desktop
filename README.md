PT/EN

# Agente IA para Cotações de Materiais

Este projeto é um agente inteligente para busca e cotação de materiais em diversos sites de comércio eletrônico. Ele utiliza técnicas de web scraping com Selenium, Scrapy e requests para coletar informações de preços, descrições e fornecedores, armazenando os dados em um banco SQLite.

## Funcionalidades

- Busca de materiais em sites como Mercado Livre, Amazon, Shopee, Magazine Luiza, Americanas, Casas Bahia e Google Shopping.
- Interface gráfica desenvolvida com PyQt6 para facilitar a busca e visualização dos resultados.
- Armazenamento dos dados coletados em banco SQLite.
- Exportação dos resultados para arquivo CSV.
- Análise dos resultados via API Deepseek (requer chave API configurada).
- Uso de proxies e rotação de user agents para evitar bloqueios durante o scraping.

## Estrutura do Projeto

- `main.py`: Script principal para testes básicos de inserção e listagem no banco.
- `database.py`: Gerenciamento do banco de dados SQLite.
- `interface.py`: Interface gráfica com PyQt6.
- `selenium_scraper.py`: Implementação do scraper com Selenium e Scrapy.
- `proxy_manager.py`: Gerenciamento de proxies e user agents.
- `config.ini`: Arquivo de configuração para chaves de API e URLs.
- `data/cotacoes.db`: Banco de dados SQLite com os dados coletados.
- `chromedriver.exe`: Driver do Chrome necessário para o Selenium.
- `requirements.txt`: Dependências do projeto.

## Requisitos

- Python 3.8 ou superior
- Google Chrome instalado
- Chromedriver compatível com a versão do Chrome (arquivo `chromedriver.exe` incluído)
- Bibliotecas Python listadas em `requirements.txt`

## Instalação

1. Clone o repositório:
   ```
   git clone <URL_DO_REPOSITORIO>
   cd AgenteIA_Desktop
   ```

2. Crie e ative um ambiente virtual:
   ```
   python -m venv venv
   venv\Scripts\activate  # Windows
   source venv/bin/activate  # Linux/Mac
   ```

3. Instale as dependências:
   ```
   pip install -r requirements.txt
   ```

4. Configure a chave da API Deepseek no arquivo `config.ini`:
   ```ini
   [deepseek]
   api_key = SUA_CHAVE_API
   base_url = https://api.deepseek.com
   ```

## Uso

Execute a interface gráfica:
```
python interface.py
```

Digite o nome do material que deseja buscar e utilize as funcionalidades disponíveis para buscar, exportar e analisar os resultados.

## Licença

Este projeto está licenciado sob a licença MIT.

------------------------------------------------------------

AI Agent for Material Quotations

This project is an intelligent agent for searching and quoting materials on various e-commerce websites. It uses web scraping techniques with Selenium, Scrapy, and requests to collect information on prices, descriptions, and suppliers, storing the data in an SQLite database.

Features

    Searches for materials on sites like Mercado Livre, Amazon, Shopee, Magazine Luiza, Americanas, Casas Bahia, and Google Shopping.

    A graphical interface developed with PyQt6 to facilitate the search and visualization of results.

    Stores the collected data in an SQLite database.

    Exports results to a CSV file.

    Analyzes the results via the Deepseek API (requires configured API key).

    Uses proxies and user agent rotation to avoid blocks during scraping.

Project Structure

    main.py: Main script for basic database insertion and listing tests.

    database.py: Manages the SQLite database.

    interface.py: The graphical user interface with PyQt6.

    selenium_scraper.py: Scraper implementation with Selenium and Scrapy.

    proxy_manager.py: Manages proxies and user agents.

    config.ini: Configuration file for API keys and URLs.

    data/cotacoes.db: SQLite database with collected data.

    chromedriver.exe: Chrome driver required for Selenium.

    requirements.txt: Project dependencies.

Requirements

    Python 3.8 or higher

    Google Chrome installed

    Chromedriver compatible with the Chrome version (chromedriver.exe file included)

    Python libraries listed in requirements.txt

Installation

    Clone the repository:

    git clone <REPOSITORY_URL>
    cd AgenteIA_Desktop

    Create and activate a virtual environment:

    python -m venv venv
    venv\Scripts\activate # Windows
    source venv/bin/activate # Linux/Mac

    Install dependencies:

    pip install -r requirements.txt

    Configure the Deepseek API key in the config.ini file:
    Ini, TOML

    [deepseek]
    api_key = YOUR_API_KEY
    base_url = https://api.deepseek.com

Usage

Run the graphical interface:

python interface.py

Enter the name of the material you want to search for and use the available features to search, export, and analyze the results.

License

This project is licensed under the MIT license.

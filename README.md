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

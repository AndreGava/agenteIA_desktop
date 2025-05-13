import time
import random
import logging
import requests
from bs4 import BeautifulSoup
import scrapy
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException


class ScrapyMercadoLivreSpider(scrapy.Spider):
    name = "mercado_livre_spider"
    allowed_domains = ["mercadolivre.com.br"]

    def __init__(self, search_term=None, *args, **kwargs):
        super(ScrapyMercadoLivreSpider, self).__init__(*args, **kwargs)
        self.search_term = search_term
        if search_term:
            url = f"https://lista.mercadolivre.com.br/{search_term.replace(' ', '-')}"
        else:
            url = "https://lista.mercadolivre.com.br/"
        self.start_urls = [url]
        self.results = []

    def parse(self, response):
        produtos = response.css("li.ui-search-layout__item")
        for produto in produtos:
            nome = produto.css("h2.ui-search-item__title::text").get()
            preco_inteiro = produto.css("span.price-tag-fraction::text").get()
            preco_centavos = produto.css("span.price-tag-cents::text").get()
            preco = None
            if preco_inteiro:
                preco = preco_inteiro
                if preco_centavos:
                    preco += "," + preco_centavos
                preco = "R$ " + preco
            link = produto.css("a.ui-search-link::attr(href)").get()
            self.results.append({
                "nome": nome.strip() if nome else None,
                "preco": preco,
                "link": link
            })


from proxy_manager import ProxyManager


class SeleniumScraper:
    def __init__(self, driver_path, usar_selenium_amazon=False):
        self.proxy_manager = ProxyManager()
        chrome_options = Options()
        # Rotação de user agents para evitar bloqueios
        user_agent = self.proxy_manager.get_random_user_agent()
        chrome_options.add_argument(f'user-agent={user_agent}')
        # Configurar proxy para Selenium
        proxy = self.proxy_manager.get_random_proxy()
        if proxy:
            chrome_options.add_argument(f'--proxy-server={proxy}')
        chrome_options.add_argument("--headless")  # Execução headless para performance
        chrome_options.add_argument("--disable-gpu")
        chrome_options.add_argument("--no-sandbox")
        # Evitar detecção do Selenium
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        chrome_options.add_argument("--disable-blink-features=AutomationControlled")
        self.service = Service(driver_path)
        self.driver = webdriver.Chrome(service=self.service, options=chrome_options)
        self.driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
                Object.defineProperty(navigator, 'webdriver', {
                    get: () => undefined
                })
            """
        })
        self.wait = WebDriverWait(self.driver, 45)  # Aumentado para 45 segundos para mais robustez
        # Configuração de logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
        self.usar_selenium_amazon = usar_selenium_amazon
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0"
        ]

    def buscar_material(self, nome_material):
        resultados = {}
        resultados['google_shopping'] = self.buscar_google_shopping(nome_material)
        resultados['mercado_livre'] = self.buscar_mercado_livre(nome_material)
        resultados['amazon'] = self.buscar_amazon(nome_material)
        resultados['shopee'] = self.buscar_shopee(nome_material)
        resultados['magazine_luiza'] = self.buscar_magazine_luiza(nome_material)
        resultados['americanas'] = self.buscar_americanas(nome_material)
        resultados['casas_bahia'] = self.buscar_casas_bahia(nome_material)
        return resultados

    def _get_html_requests(self, url, max_retries=3, delay=5):
        headers = {"User-Agent": random.choice(self.user_agents)}
        for attempt in range(max_retries):
            try:
                response = requests.get(url, headers=headers, timeout=10)
                response.raise_for_status()
                return response.text
            except requests.exceptions.HTTPError as e:
                if response.status_code == 503:
                    self.logger.warning(
                        f"Erro 503 ao obter HTML via requests para {url}, "
                        f"tentativa {attempt + 1} de {max_retries}"
                    )
                    time.sleep(delay)
                else:
                    self.logger.warning(f"Falha ao obter HTML via requests para {url}: {e}")
                    break
            except Exception as e:
                self.logger.warning(f"Falha ao obter HTML via requests para {url}: {e}")
                break
        return None

    def _get_html_selenium(self, url):
        try:
            self.driver.get(url)
            time.sleep(5)  # Espera para carregamento
            return self.driver.page_source
        except Exception as e:
            self.logger.error(f"Falha ao obter HTML via Selenium para {url}: {e}")
            return None

    def _get_html_scrapy(self, search_term):
        self.logger.info(f"Iniciando busca Scrapy para: {search_term}")
        process = CrawlerProcess(get_project_settings())
        spider = ScrapyMercadoLivreSpider(search_term=search_term)
        process.crawl(spider)
        process.start()  # Bloqueia até o término
        return spider.results

    def buscar_google_shopping(self, nome_material):
        # Tentar requests + BeautifulSoup primeiro
        url = f"https://www.google.com/search?tbm=shop&q={nome_material.replace(' ', '+')}"
        html = self._get_html_requests(url)
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                produtos = soup.select("div.sh-dgr__content, div.sh-dlr__list-result")
                materiais = []
                for produto in produtos[:10]:
                    nome_tag = produto.select_one("h3.tAxDx, h4.sh-np__product-title")
                    preco_tag = produto.select_one("span.a8Pemb, span.T14wmb")
                    link_tag = produto.select_one("a")
                    nome = nome_tag.get_text(strip=True) if nome_tag else ""
                    preco = preco_tag.get_text(strip=True) if preco_tag else "Preço não disponível"
                    link = link_tag['href'] if link_tag else ""
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Google Shopping"
                    })
                if materiais:
                    return materiais
            except Exception as e:
                self.logger.warning(f"Erro ao parsear HTML Google Shopping via requests: {e}")

        # Fallback para Selenium
        self.logger.info("Usando Selenium para Google Shopping")
        url = f"https://www.google.com/search?tbm=shop&q={nome_material.replace(' ', '+')}"
        self.driver.get(url)
        try:
            # Espera explícita pelos resultados
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.sh-dgr__content"))
            )
            time.sleep(2)  # Pequena espera adicional para garantir carregamento
            produtos = self.driver.find_elements(By.CSS_SELECTOR, "div.sh-dgr__content")
            materiais = []
            for produto in produtos[:10]:
                try:
                    nome = produto.find_element(
                        By.CSS_SELECTOR, "h3.tAxDx, h4.sh-np__product-title"
                    ).text.strip()
                    preco = produto.find_element(
                        By.CSS_SELECTOR, "span.a8Pemb, span.T14wmb"
                    ).text.strip()
                    link = produto.find_element(By.TAG_NAME, "a").get_attribute("href")
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Google Shopping"
                    })
                except Exception as e:
                    self.logger.error(f"Erro ao processar produto Google Shopping: {e}")
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar Google Shopping via Selenium: {e}")
            return []

    def buscar_mercado_livre(self, nome_material):
        self.logger.info("Iniciando busca no Mercado Livre com Selenium")
        url = f"https://lista.mercadolivre.com.br/{nome_material.replace(' ', '-')}"
        try:
            self.driver.get(url)
            time.sleep(5)  # Aumentado para 5 segundos para garantir carregamento
            # Espera explícita pelo container de produtos
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "ol.ui-search-layout"))
            )
            materiais = []
            produtos = self.driver.find_elements(By.CSS_SELECTOR, "li.ui-search-layout__item")
            for produto in produtos[:10]:
                try:
                    nome = None
                    nome_selectors = [
                        "h2.ui-search-item__title",
                        ".ui-search-item__group__element h2",
                        "h2[class*='ui-search']"
                    ]
                    for selector in nome_selectors:
                        try:
                            nome_elem = produto.find_element(By.CSS_SELECTOR, selector)
                            nome = nome_elem.text.strip()
                            if nome:
                                break
                        except NoSuchElementException:
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao tentar selector {selector}: {str(e)}")
                    if not nome:
                        nome = self.driver.execute_script(
                            "return arguments[0].querySelector('h2').textContent;",
                            produto
                        )
                        if nome:
                            nome = nome.strip()
                    preco = "Preço não disponível"
                    preco_selectors = [
                        "span.price-tag-fraction",
                        "span.price-tag-cents",
                        "span.price-tag-amount",
                        ".ui-search-price__second-line .price-tag-amount"
                    ]
                    for selector in preco_selectors:
                        try:
                            preco_elem = produto.find_element(By.CSS_SELECTOR, selector)
                            preco_text = preco_elem.text.strip()
                            if preco_text:
                                preco = f"R$ {preco_text}"
                                break
                        except NoSuchElementException:
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao tentar selector {selector}: {str(e)}")
                    link = None
                    link_selectors = [
                        "a.ui-search-item__group__element",
                        "a.ui-search-link",
                        "a[href*='mercadolivre']"
                    ]
                    for selector in link_selectors:
                        try:
                            link_elem = produto.find_element(By.CSS_SELECTOR, selector)
                            link = link_elem.get_attribute("href")
                            if link:
                                break
                        except NoSuchElementException:
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao tentar selector {selector}: {str(e)}")
                    if nome or link:  # Adiciona se tiver pelo menos nome ou link
                        material = {
                            "nome": nome or "Nome não disponível",
                            "preco": preco,
                            "descricao": nome or "Descrição não disponível",
                            "link": link or "#",
                            "fornecedor": "Mercado Livre"
                        }
                        materiais.append(material)
                except Exception as e:
                    self.logger.error(f"Erro ao processar produto: {str(e)}")
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar no Mercado Livre: {str(e)}")
            return []

    def buscar_amazon(self, nome_material):
        # Tentar requests + BeautifulSoup primeiro
        url = f"https://www.amazon.com.br/s?k={nome_material.replace(' ', '+')}"
        html = self._get_html_requests(url)
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                produtos = soup.select("div.s-result-item[data-component-type='s-search-result']")
                materiais = []
                for produto in produtos[:10]:
                    nome_tag = produto.select_one("h2 span.a-text-normal")
                    preco_tag = produto.select_one("span.a-price-whole")
                    link_tag = produto.select_one("h2 a")
                    nome = nome_tag.get_text(strip=True) if nome_tag else ""
                    preco = preco_tag.get_text(strip=True) if preco_tag else "Preço não disponível"
                    link = link_tag['href'] if link_tag else ""
                    materiais.append({
                        "nome": nome,
                        "preco": f"R$ {preco}" if preco != "Preço não disponível" else preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Amazon"
                    })
                if materiais:
                    return materiais
            except Exception as e:
                self.logger.warning(f"Erro ao parsear HTML Amazon via requests: {e}")

        # Fallback para Selenium
        self.logger.info("Usando Selenium para Amazon")
        try:
            self.driver.get(url)
            time.sleep(3)
            for _ in range(3):
                self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(2)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.s-main-slot"))
            )
            produtos = self.driver.find_elements(
                By.CSS_SELECTOR,
                "div.s-result-item[data-component-type='s-search-result']"
            )
            materiais = []
            for produto in produtos[:10]:
                try:
                    nome = None
                    nome_selectors = [
                        "h2 span.a-text-normal",
                        "h2.a-size-mini span",
                        "h2 a span",
                        "h2"
                    ]
                    for selector in nome_selectors:
                        try:
                            nome_elem = produto.find_element(By.CSS_SELECTOR, selector)
                            nome = nome_elem.text.strip()
                            if nome:
                                break
                        except NoSuchElementException:
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao tentar selector {selector}: {str(e)}")
                    if not nome:
                        nome = self.driver.execute_script(
                            "return arguments[0].querySelector('h2').textContent;",
                            produto
                        )
                        if nome:
                            nome = nome.strip()
                    preco = "Preço não disponível"
                    preco_selectors = [
                        "span.a-price-whole",
                        "span.a-offscreen",
                        ".a-price .a-offscreen"
                    ]
                    for selector in preco_selectors:
                        try:
                            preco_elem = produto.find_element(By.CSS_SELECTOR, selector)
                            preco_text = preco_elem.text.strip()
                            if preco_text:
                                preco = f"R$ {preco_text}"
                                break
                        except NoSuchElementException:
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao tentar selector {selector}: {str(e)}")
                    link = None
                    link_selectors = [
                        "h2 a",
                        "a.a-link-normal",
                        "a[href*='/dp/']"
                    ]
                    for selector in link_selectors:
                        try:
                            link_elem = produto.find_element(By.CSS_SELECTOR, selector)
                            link = link_elem.get_attribute("href")
                            if link:
                                break
                        except NoSuchElementException:
                            continue
                        except Exception as e:
                            self.logger.error(f"Erro ao tentar selector {selector}: {str(e)}")
                    if nome or link:  # Adiciona se tiver pelo menos nome ou link
                        material = {
                            "nome": nome or "Nome não disponível",
                            "preco": preco,
                            "descricao": nome or "Descrição não disponível",
                            "link": link or "#",
                            "fornecedor": "Amazon"
                        }
                        materiais.append(material)
                except Exception:
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar na Amazon: {str(e)}")
            return []

    def buscar_shopee(self, nome_material):
        # Tentar requests + BeautifulSoup primeiro
        url = f"https://shopee.com.br/search?keyword={nome_material.replace(' ', '%20')}"
        html = self._get_html_requests(url)
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                produtos = soup.select("div.shopee-search-item-result__item")
                materiais = []
                for produto in produtos[:10]:
                    nome_tag = produto.select_one("div._1NoI8_._16BAGk")
                    preco_tag = produto.select_one("span._341bF0")
                    link_tag = produto.select_one("a")
                    nome = nome_tag.get_text(strip=True) if nome_tag else ""
                    preco = preco_tag.get_text(strip=True) if preco_tag else "Preço não disponível"
                    link = link_tag['href'] if link_tag else ""
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Shopee"
                    })
                if materiais:
                    return materiais
            except Exception as e:
                self.logger.warning(f"Erro ao parsear HTML Shopee via requests: {e}")

        # Fallback para Selenium
        self.logger.info("Usando Selenium para Shopee")
        try:
            self.driver.get(url)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.shopee-search-item-result__items"))
            )
            time.sleep(3)
            produtos = self.driver.find_elements(By.CSS_SELECTOR, "div.shopee-search-item-result__item")
            materiais = []
            for produto in produtos[:10]:
                try:
                    nome = produto.find_element(By.CSS_SELECTOR, "div._1NoI8_._16BAGk").text.strip()
                    preco = produto.find_element(By.CSS_SELECTOR, "span._341bF0").text.strip()
                    link = produto.find_element(By.TAG_NAME, "a").get_attribute("href")
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Shopee"
                    })
                except Exception:
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar na Shopee: {e}")
            return []

    def buscar_magazine_luiza(self, nome_material):
        # Tentar requests + BeautifulSoup primeiro
        url = f"https://www.magazineluiza.com.br/busca/{nome_material.replace(' ', '%20')}/"
        html = self._get_html_requests(url)
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                produtos = soup.select("li.product")
                materiais = []
                for produto in produtos[:10]:
                    nome_tag = produto.select_one("h2.product-title")
                    preco_tag = produto.select_one("span.price-value")
                    link_tag = produto.select_one("a")
                    nome = nome_tag.get_text(strip=True) if nome_tag else ""
                    preco = preco_tag.get_text(strip=True) if preco_tag else "Preço não disponível"
                    link = link_tag['href'] if link_tag else ""
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Magazine Luiza"
                    })
                if materiais:
                    return materiais
            except Exception as e:
                self.logger.warning(f"Erro ao parsear HTML Magazine Luiza via requests: {e}")

        # Fallback para Selenium
        self.logger.info("Usando Selenium para Magazine Luiza")
        try:
            self.driver.get(url)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-grid"))
            )
            time.sleep(3)
            produtos = self.driver.find_elements(By.CSS_SELECTOR, "li.product")
            materiais = []
            for produto in produtos[:10]:
                try:
                    nome = produto.find_element(By.CSS_SELECTOR, "h2.product-title").text.strip()
                    preco = produto.find_element(By.CSS_SELECTOR, "span.price-value").text.strip()
                    link = produto.find_element(By.TAG_NAME, "a").get_attribute("href")
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Magazine Luiza"
                    })
                except Exception:
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar no Magazine Luiza: {e}")
            return []

    def buscar_americanas(self, nome_material):
        # Tentar requests + BeautifulSoup primeiro
        url = f"https://www.americanas.com.br/busca/{nome_material.replace(' ', '%20')}"
        html = self._get_html_requests(url)
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                produtos = soup.select("div.product-grid-item")
                materiais = []
                for produto in produtos[:10]:
                    nome_tag = produto.select_one("h2.product-title")
                    preco_tag = produto.select_one("span.price-value")
                    link_tag = produto.select_one("a")
                    nome = nome_tag.get_text(strip=True) if nome_tag else ""
                    preco = preco_tag.get_text(strip=True) if preco_tag else "Preço não disponível"
                    link = link_tag['href'] if link_tag else ""
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Americanas"
                    })
                if materiais:
                    return materiais
            except Exception as e:
                self.logger.warning(f"Erro ao parsear HTML Americanas via requests: {e}")

        # Fallback para Selenium
        self.logger.info("Usando Selenium para Americanas")
        try:
            self.driver.get(url)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-grid"))
            )
            time.sleep(3)
            produtos = self.driver.find_elements(By.CSS_SELECTOR, "div.product-grid-item")
            materiais = []
            for produto in produtos[:10]:
                try:
                    nome = produto.find_element(By.CSS_SELECTOR, "h2.product-title").text.strip()
                    preco = produto.find_element(By.CSS_SELECTOR, "span.price-value").text.strip()
                    link = produto.find_element(By.TAG_NAME, "a").get_attribute("href")
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Americanas"
                    })
                except Exception:
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar na Americanas: {e}")
            return []

    def buscar_casas_bahia(self, nome_material):
        # Tentar requests + BeautifulSoup primeiro
        url = f"https://www.casasbahia.com.br/busca/{nome_material.replace(' ', '%20')}"
        html = self._get_html_requests(url)
        if html:
            try:
                soup = BeautifulSoup(html, "html.parser")
                produtos = soup.select("div.product-grid-item")
                materiais = []
                for produto in produtos[:10]:
                    nome_tag = produto.select_one("h2.product-title")
                    preco_tag = produto.select_one("span.price-value")
                    link_tag = produto.select_one("a")
                    nome = nome_tag.get_text(strip=True) if nome_tag else ""
                    preco = preco_tag.get_text(strip=True) if preco_tag else "Preço não disponível"
                    link = link_tag['href'] if link_tag else ""
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Casas Bahia"
                    })
                if materiais:
                    return materiais
            except Exception as e:
                self.logger.warning(f"Erro ao parsear HTML Casas Bahia via requests: {e}")

        # Fallback para Selenium
        self.logger.info("Usando Selenium para Casas Bahia")
        try:
            self.driver.get(url)
            self.wait.until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "div.product-grid"))
            )
            time.sleep(3)
            produtos = self.driver.find_elements(By.CSS_SELECTOR, "div.product-grid-item")
            materiais = []
            for produto in produtos[:10]:
                try:
                    nome = produto.find_element(By.CSS_SELECTOR, "h2.product-title").text.strip()
                    preco = produto.find_element(By.CSS_SELECTOR, "span.price-value").text.strip()
                    link = produto.find_element(By.TAG_NAME, "a").get_attribute("href")
                    materiais.append({
                        "nome": nome,
                        "preco": preco,
                        "descricao": nome,
                        "link": link,
                        "fornecedor": "Casas Bahia"
                    })
                except Exception:
                    continue
            return materiais
        except Exception as e:
            self.logger.error(f"Erro ao buscar na Casas Bahia: {e}")
            return []

    def exibir_resultados(self, resultados):
        for i, produto in enumerate(resultados, 1):
            print(f"🔹 Produto {i}")
            print(f"Nome: {produto.get('nome', 'N/A')}")
            print(f"Preço: {produto.get('preco', 'N/A')}")
            print(f"Descrição: {produto.get('descricao', 'N/A')}")
            print(f"Link: {produto.get('link', 'N/A')}")
            print(f"Fornecedor: {produto.get('fornecedor', 'N/A')}")
            print("🔹 ****\n")

    def fechar_driver(self):
        self.driver.quit()

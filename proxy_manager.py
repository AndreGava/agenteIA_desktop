import random
import requests
import logging


class ProxyManager:
    def __init__(self, proxies=None, user_agents=None):
        self.proxies = proxies or []
        self.user_agents = user_agents or [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) "
            "Version/14.0.3 Safari/605.1.15",
            # Adicione mais user agents se necessário
        ]
        self.logger = logging.getLogger(__name__)

    def get_random_proxy(self):
        if not self.proxies:
            return None
        proxy = random.choice(self.proxies)
        self.logger.info(f"Usando proxy: {proxy}")
        return proxy

    def get_random_user_agent(self):
        user_agent = random.choice(self.user_agents)
        self.logger.info(f"Usando user-agent: {user_agent}")
        return user_agent

    def get_request_headers(self):
        return {
            "User-Agent": self.get_random_user_agent()
        }

    def get_request_proxies(self):
        proxy = self.get_random_proxy()
        if proxy:
            return {
                "http": proxy,
                "https": proxy
            }
        return None

    def test_proxy(self, proxy):
        try:
            response = requests.get(
                "https://www.google.com",
                proxies={"http": proxy, "https": proxy},
                timeout=5
            )
            return response.status_code == 200
        except Exception:
            return False

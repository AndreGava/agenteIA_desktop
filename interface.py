from PyQt6.QtWidgets import (
    QApplication, QLabel, QMainWindow, QPushButton, QVBoxLayout, QWidget,
    QLineEdit, QMessageBox, QProgressBar,
    QTableWidget, QTableWidgetItem, QHeaderView, QAbstractItemView, QTextEdit,
    QCheckBox, QFileDialog
)
from database import Database
from selenium_scraper import SeleniumScraper
import requests
import csv
import configparser
import os


class MainWindow(QMainWindow):

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Agente IA - Cotação de Materiais")
        self.setGeometry(300, 200, 800, 700)

        self.db = Database()
        self.scraper = SeleniumScraper(
            "c:/Andre-arquivos/projetos/AgenteIA_Desktop/chromedriver.exe"
        )

        layout = QVBoxLayout()

        self.label = QLabel("Digite o nome do material para buscar:")
        layout.addWidget(self.label)

        self.input_material = QLineEdit()
        layout.addWidget(self.input_material)

        self.button_buscar = QPushButton("Buscar Material")
        self.button_buscar.clicked.connect(self.buscar_material)
        layout.addWidget(self.button_buscar)

        self.checkbox_incluir_incompletos = QCheckBox(
            "Incluir resultados incompletos"
        )
        layout.addWidget(self.checkbox_incluir_incompletos)

        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)

        self.table_resultados = QTableWidget()
        self.table_resultados.setColumnCount(5)
        self.table_resultados.setHorizontalHeaderLabels([
            "Nome", "Preço", "Descrição", "Link", "Fornecedor"
        ])
        self.table_resultados.horizontalHeader().setSectionResizeMode(
            QHeaderView.ResizeMode.Stretch
        )
        self.table_resultados.setEditTriggers(
            QAbstractItemView.EditTrigger.NoEditTriggers
        )
        layout.addWidget(self.table_resultados)

        # self.button_salvar = QPushButton("Salvar resultados no banco")
        # self.button_salvar.setEnabled(False)
        # self.button_salvar.clicked.connect(self.salvar_resultados)
        # layout.addWidget(self.button_salvar)

        self.button_exportar = QPushButton("Salvar resultados em CSV")
        self.button_exportar.setEnabled(False)
        self.button_exportar.clicked.connect(self.exportar_csv)
        layout.addWidget(self.button_exportar)

        self.button_analisar = QPushButton("Analisar Resultados")
        self.button_analisar.setEnabled(False)
        self.button_analisar.clicked.connect(self.analisar_resultados_chatgpt)
        layout.addWidget(self.button_analisar)

        self.texto_analise = QTextEdit()
        self.texto_analise.setReadOnly(True)
        layout.addWidget(self.texto_analise)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

        # Para armazenar resultados da busca web temporariamente
        self.resultados_web = []

    def buscar_material(self):
        nome = self.input_material.text().strip()
        if not nome:
            QMessageBox.warning(
                self, "Aviso",
                "Por favor, digite o nome do material para buscar."
            )
            return

        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminado
        QApplication.processEvents()

        try:
            resultados_dict = self.scraper.buscar_material(nome)
            # Concatenar todas as listas de resultados em uma única lista
            resultados = []
            for lista in resultados_dict.values():
                resultados.extend(lista)
            # Store the results for further use
            self.resultados_web = resultados
            self.update_table(resultados)  # Update the table with the results

            # Habilitar ou desabilitar botões conforme resultados
            tem_resultados = len(resultados) > 0
            # Ajuste para evitar erro se button_salvar foi removido
            if hasattr(self, "button_salvar"):
                self.button_salvar.setEnabled(tem_resultados)
            self.button_exportar.setEnabled(tem_resultados)
            self.button_analisar.setEnabled(tem_resultados)

        except Exception as e:
            QMessageBox.critical(
                self, "Erro",
                f"Erro ao buscar material: {str(e)}"
            )
        finally:
            self.progress_bar.setVisible(False)

    def update_table(self, resultados):
        self.table_resultados.setRowCount(len(resultados))
        for row, resultado in enumerate(resultados):
            # Resultado é um dicionário, extrair os valores
            # na ordem das colunas
            valores = [
                resultado.get("nome", ""),
                resultado.get("preco", ""),
                resultado.get("descricao", ""),
                resultado.get("link", ""),
                resultado.get("fornecedor", ""),
            ]
            for col, value in enumerate(valores):
                self.table_resultados.setItem(
                    row, col, QTableWidgetItem(str(value))
                )
    import requests

    def salvar_resultados(self):
        if not self.resultados_web:
            QMessageBox.warning(
                self, "Aviso", "Não há resultados para salvar."
            )
            return
        try:
            for resultado in self.resultados_web:
                nome = resultado.get("nome", "")
                preco_str = resultado.get("preco", "")
                preco_str = (
                    preco_str.replace("R$ ", "")
                    .replace(".", "")
                    .replace(",", ".")
                )
                try:
                    preco = float(preco_str)
                except ValueError:
                    preco = None
                descricao = resultado.get("descricao", "")
                link = resultado.get("link", "")
                fornecedor = resultado.get("fornecedor", "")
                self.db.inserir_material(
                    nome, preco, descricao, link, fornecedor
                )
            QMessageBox.information(
                self, "Sucesso", "Resultados salvos no banco com sucesso."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao salvar resultados: {str(e)}"
            )

    def exportar_csv(self):
        if not self.resultados_web:
            QMessageBox.warning(
                self, "Aviso", "Não há resultados para exportar."
            )
            return
        try:
            path, _ = QFileDialog.getSaveFileName(
                self, "Salvar CSV", "", "CSV Files (*.csv)"
            )
            if not path:
                return
            with open(path, mode="w", newline="", encoding="utf-8") as file:
                writer = csv.writer(file)
                writer.writerow([
                    "Nome", "Preço", "Descrição", "Link", "Fornecedor"
                ])
                for resultado in self.resultados_web:
                    writer.writerow(
                        [
                            resultado.get("nome", ""),
                            resultado.get("preco", ""),
                            resultado.get("descricao", ""),
                            resultado.get("link", ""),
                            resultado.get("fornecedor", ""),
                        ]
                    )
            QMessageBox.information(
                self, "Sucesso", "Resultados exportados para CSV com sucesso."
            )
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao exportar CSV: {str(e)}"
            )

    def analisar_resultados_chatgpt(self):
        if not self.resultados_web:
            QMessageBox.warning(
                self, "Aviso", "Não há resultados para analisar."
            )
            return
        try:
            self.texto_analise.clear()
            self.texto_analise.append(
                "Analisando resultados, por favor aguarde..."
            )

            # Ler config.ini para obter api_key
            config = configparser.ConfigParser()
            config_path = os.path.join(os.path.dirname(__file__), "config.ini")
            config.read(config_path)
            api_key = None
            if "deepseek" in config and "api_key" in config["deepseek"]:
                api_key = config["deepseek"]["api_key"]
            if not api_key:
                raise Exception(
                    "Chave API Deepseek não configurada no arquivo config.ini"
                )

            # Preparar dados para enviar à API Deepseek
            dados = {
                "resultados": self.resultados_web
            }
            url_api = "https://api.deepseek.com"
            headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}",
            }
            # Ler base_url do config.ini
            base_url = config["deepseek"].get(
                "base_url", "https://api.deepseek.com"
            )
            url_api = base_url.rstrip("/") + "/analyze"
            response = requests.post(url_api, json=dados, headers=headers)
            response.raise_for_status()
            analise = response.json().get(
                "analise", "Nenhuma análise retornada."
            )
            self.texto_analise.clear()
            self.texto_analise.append(analise)
        except requests.exceptions.HTTPError as http_err:
            if http_err.response.status_code == 404:
                QMessageBox.critical(
                    self,
                    "Erro",
                    ("Erro 404: Endpoint da API Deepseek não encontrado. "
                     "Verifique a URL da API."),
                )
            else:
                QMessageBox.critical(
                    self, "Erro",
                    f"Erro HTTP ao analisar resultados: {str(http_err)}"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "Erro", f"Erro ao analisar resultados: {str(e)}"
            )


if __name__ == "__main__":
    import sys
    # Removed redundant import of QApplication

    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

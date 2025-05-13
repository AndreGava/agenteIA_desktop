import sqlite3


class Database:
    def __init__(self, db_name="data/cotacoes.db"):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()
        self.migrate()

    def create_table(self):
        self.cursor.execute("""
        CREATE TABLE IF NOT EXISTS materiais (
            id INTEGER PRIMARY KEY,
            nome TEXT NOT NULL,
            preco REAL,
            descricao TEXT,
            link TEXT,
            fornecedor TEXT,
            contato TEXT
        )
        """)
        self.conn.commit()

    def migrate(self):
        # Verifica se a coluna 'fornecedor' existe na tabela 'materiais'
        self.cursor.execute("PRAGMA table_info(materiais)")
        columns = [info[1] for info in self.cursor.fetchall()]
        if "fornecedor" not in columns:
            self.cursor.execute("ALTER TABLE materiais ADD COLUMN fornecedor TEXT")
            self.conn.commit()

    def inserir_material(
        self, nome, preco, descricao, link, fornecedor=None, contato=None
    ):
        self.cursor.execute(
            """
            INSERT INTO materiais (
                nome, preco, descricao, link, fornecedor, contato
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (nome, preco, descricao, link, fornecedor, contato)
        )
        self.conn.commit()

    def buscar_material(
        self, nome=None, fornecedor=None, preco_min=None, preco_max=None
    ):
        query = "SELECT * FROM materiais WHERE 1=1"
        params = []
        if nome:
            query += " AND nome LIKE ?"
            params.append('%' + nome + '%')
        if fornecedor:
            query += " AND fornecedor LIKE ?"
            params.append('%' + fornecedor + '%')
        if preco_min is not None:
            query += " AND preco >= ?"
            params.append(preco_min)
        if preco_max is not None:
            query += " AND preco <= ?"
            params.append(preco_max)
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def fechar_conexao(self):
        self.conn.close()
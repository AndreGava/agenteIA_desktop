from database import Database

# Criar conexão com banco
db = Database()

# Inserir exemplo de material
db.inserir_material("Cimento Portland 50kg", 45.99, "Fornecedor A")

# Listar materiais armazenados
materiais = db.listar_materiais()
for material in materiais:
    print(material)

# Fechar banco
db.fechar_conexao()

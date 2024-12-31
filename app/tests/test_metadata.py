from app.core.database import Base
import app.models  # Carregar explicitamente os modelos

print("Depuração de tabelas no Base.metadata:")
for table_name in Base.metadata.tables.keys():
    print(f"Tabela detectada: {table_name}")

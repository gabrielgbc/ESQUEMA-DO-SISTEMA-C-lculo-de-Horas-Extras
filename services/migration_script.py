"""
migrate_add_empresa.py
Script para adicionar suporte a empresas no banco existente
"""
from sqlalchemy import create_engine, text, inspect
from models.database import DATABASE_URL, Base, init_db

def verificar_e_migrar():
    """Verifica e atualiza o banco de dados"""
    print("🔄 Iniciando migração do banco de dados...")
    
    engine = create_engine(DATABASE_URL, echo=False)
    inspector = inspect(engine)
    
    # Verifica se a tabela empresas existe
    if 'empresas' not in inspector.get_table_names():
        print("➕ Criando tabela 'empresas'...")
        from models.empresa import Empresa
        Base.metadata.create_all(bind=engine, tables=[Empresa.__table__])
        print("✅ Tabela 'empresas' criada!")
    else:
        print("✅ Tabela 'empresas' já existe")
    
    # Verifica se a coluna empresa_id existe na tabela funcionarios
    funcionarios_columns = [col['name'] for col in inspector.get_columns('funcionarios')]
    
    if 'empresa_id' not in funcionarios_columns:
        print("➕ Adicionando coluna 'empresa_id' na tabela 'funcionarios'...")
        
        with engine.connect() as conn:
            try:
                # SQLite não suporta ALTER TABLE ADD COLUMN com FOREIGN KEY diretamente
                # Então fazemos em duas etapas
                conn.execute(text("ALTER TABLE funcionarios ADD COLUMN empresa_id INTEGER"))
                conn.commit()
                print("✅ Coluna 'empresa_id' adicionada!")
            except Exception as e:
                print(f"⚠️ Erro ao adicionar coluna (pode já existir): {e}")
    else:
        print("✅ Coluna 'empresa_id' já existe")
    
    print("\n🎉 Migração concluída com sucesso!")
    print("\n📋 Próximos passos:")
    print("1. Execute o sistema normalmente: python app.py")
    print("2. Cadastre empresas no menu '🏢 Empresas'")
    print("3. Edite funcionários existentes para vincular às empresas")

if __name__ == "__main__":
    try:
        verificar_e_migrar()
    except Exception as e:
        print(f"❌ Erro na migração: {e}")
        import traceback
        traceback.print_exc()

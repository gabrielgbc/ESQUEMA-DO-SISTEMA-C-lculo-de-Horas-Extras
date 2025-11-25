"""
fix_database.py
Script para corrigir completamente o banco de dados
"""
import os
from sqlalchemy import create_engine, text, inspect
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "sqlite:///horas_extras.db"

def backup_database():
    """Faz backup do banco antes de alterar"""
    if os.path.exists("horas_extras.db"):
        import shutil
        backup_name = f"horas_extras_backup_{os.path.getmtime('horas_extras.db')}.db"
        shutil.copy2("horas_extras.db", backup_name)
        print(f"✅ Backup criado: {backup_name}")
        return True
    return False

def fix_database():
    """Corrige o banco de dados"""
    print("🔧 Iniciando correção do banco de dados...\n")
    
    # Backup
    backup_database()
    
    engine = create_engine(DATABASE_URL, echo=False)
    inspector = inspect(engine)
    
    with engine.connect() as conn:
        # 1. Verifica se tabela empresas existe
        if 'empresas' not in inspector.get_table_names():
            print("📦 Criando tabela 'empresas'...")
            conn.execute(text("""
                CREATE TABLE empresas (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    nome VARCHAR(200) NOT NULL,
                    cnpj VARCHAR(18) UNIQUE NOT NULL,
                    endereco VARCHAR(300),
                    telefone VARCHAR(20),
                    email VARCHAR(100)
                )
            """))
            conn.commit()
            print("✅ Tabela 'empresas' criada!\n")
        else:
            print("✅ Tabela 'empresas' já existe\n")
        
        # 2. Verifica coluna empresa_id em funcionarios
        funcionarios_columns = [col['name'] for col in inspector.get_columns('funcionarios')]
        
        if 'empresa_id' not in funcionarios_columns:
            print("📦 Adicionando coluna 'empresa_id'...")
            conn.execute(text("ALTER TABLE funcionarios ADD COLUMN empresa_id INTEGER"))
            conn.commit()
            print("✅ Coluna 'empresa_id' adicionada!\n")
        else:
            print("✅ Coluna 'empresa_id' já existe\n")
        
        # 3. Teste de integridade
        print("🧪 Testando integridade dos dados...")
        
        # Verifica funcionários
        result = conn.execute(text("SELECT COUNT(*) FROM funcionarios"))
        num_func = result.scalar()
        print(f"   📊 Funcionários cadastrados: {num_func}")
        
        # Verifica empresas
        result = conn.execute(text("SELECT COUNT(*) FROM empresas"))
        num_emp = result.scalar()
        print(f"   📊 Empresas cadastradas: {num_emp}")
        
        # Verifica registros
        result = conn.execute(text("SELECT COUNT(*) FROM registros_jornada"))
        num_reg = result.scalar()
        print(f"   📊 Registros de jornada: {num_reg}")
        
        print("\n✅ Estrutura do banco corrigida!")
        
        # 4. Mostra funcionários sem empresa
        result = conn.execute(text("""
            SELECT id, nome FROM funcionarios 
            WHERE empresa_id IS NULL
        """))
        
        funcionarios_sem_empresa = result.fetchall()
        if funcionarios_sem_empresa:
            print(f"\n⚠️  {len(funcionarios_sem_empresa)} funcionário(s) sem empresa vinculada:")
            for func_id, nome in funcionarios_sem_empresa:
                print(f"   • ID {func_id}: {nome}")
            print("\n💡 Vincule esses funcionários a empresas através do menu 'Funcionários'")
        else:
            print("\n✅ Todos os funcionários estão vinculados a empresas!")

def test_relationships():
    """Testa se os relacionamentos funcionam"""
    print("\n🧪 Testando relacionamentos ORM...\n")
    
    try:
        from models.database import get_db
        from models.funcionario import Funcionario
        from models.empresa import Empresa
        
        db = get_db()
        
        # Testa query com relacionamento
        funcionarios = db.query(Funcionario).all()
        
        print(f"✅ Query de funcionários: OK ({len(funcionarios)} encontrados)")
        
        for func in funcionarios[:3]:  # Mostra só os 3 primeiros
            empresa_nome = func.empresa.nome if func.empresa else "Sem empresa"
            print(f"   • {func.nome} - {empresa_nome}")
        
        print("\n🎉 Relacionamentos funcionando corretamente!")
        return True
        
    except Exception as e:
        print(f"\n❌ Erro ao testar relacionamentos: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    try:
        fix_database()
        
        print("\n" + "="*70)
        test_relationships()
        print("="*70)
        
        print("\n📋 Próximos passos:")
        print("1. Execute o sistema: python app.py")
        print("2. Cadastre empresas se ainda não tiver")
        print("3. Edite funcionários para vincular às empresas")
        print("4. Use o Chat IA para consultas rápidas")
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()

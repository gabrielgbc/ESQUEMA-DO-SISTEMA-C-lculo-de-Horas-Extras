"""
diagnostico_banco.py
Script para diagnosticar e corrigir problemas no banco de dados
"""
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker

DATABASE_URL = 'sqlite:///jornada_trabalho.db'

def diagnosticar_banco():
    """Executa diagnóstico completo do banco"""
    print("🔍 DIAGNÓSTICO DO BANCO DE DADOS")
    print("=" * 70)
    
    engine = create_engine(DATABASE_URL, echo=False)
    inspector = inspect(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    
    # 1. Verificar tabelas existentes
    print("\n📋 1. TABELAS EXISTENTES:")
    tabelas = inspector.get_table_names()
    for tabela in tabelas:
        print(f"   ✅ {tabela}")
    
    if not tabelas:
        print("   ❌ Nenhuma tabela encontrada! Execute o sistema primeiro.")
        return
    
    # 2. Verificar estrutura da tabela funcionarios
    if 'funcionarios' in tabelas:
        print("\n👥 2. ESTRUTURA DA TABELA 'funcionarios':")
        colunas = inspector.get_columns('funcionarios')
        for col in colunas:
            print(f"   - {col['name']}: {col['type']}")
        
        # Contar funcionários
        result = session.execute(text("SELECT COUNT(*) FROM funcionarios"))
        num_func = result.scalar()
        print(f"\n   📊 Total de funcionários: {num_func}")
        
        if num_func > 0:
            result = session.execute(text("SELECT id, nome, empresa FROM funcionarios LIMIT 5"))
            print("\n   👤 Primeiros 5 funcionários:")
            for row in result:
                print(f"      ID {row[0]}: {row[1]} - {row[2]}")
    
    # 3. Verificar estrutura da tabela registros_jornada
    if 'registros_jornada' in tabelas:
        print("\n⏰ 3. ESTRUTURA DA TABELA 'registros_jornada':")
        colunas = inspector.get_columns('registros_jornada')
        for col in colunas:
            print(f"   - {col['name']}: {col['type']}")
        
        # Contar registros
        result = session.execute(text("SELECT COUNT(*) FROM registros_jornada"))
        num_reg = result.scalar()
        print(f"\n   📊 Total de registros: {num_reg}")
        
        if num_reg > 0:
            result = session.execute(text("""
                SELECT r.id, r.funcionario_id, r.data, r.horas_extras, r.horas_faltantes
                FROM registros_jornada r
                LIMIT 5
            """))
            print("\n   📝 Primeiros 5 registros:")
            for row in result:
                print(f"      ID {row[0]}: Funcionário {row[1]} - {row[2]} - Extra: {row[3]}h, Falta: {row[4]}h")
    
    # 4. Verificar relacionamentos (Foreign Keys)
    if 'registros_jornada' in tabelas:
        print("\n🔗 4. RELACIONAMENTOS (FOREIGN KEYS):")
        fks = inspector.get_foreign_keys('registros_jornada')
        if fks:
            for fk in fks:
                print(f"   ✅ {fk['constrained_columns']} → {fk['referred_table']}.{fk['referred_columns']}")
        else:
            print("   ⚠️  Nenhuma foreign key encontrada (pode causar problemas)")
    
    # 5. Testar JOIN manualmente
    if num_func > 0 and num_reg > 0:
        print("\n🧪 5. TESTE DE JOIN:")
        try:
            result = session.execute(text("""
                SELECT 
                    f.id,
                    f.nome,
                    f.empresa,
                    COUNT(r.id) as num_registros,
                    SUM(r.horas_extras) as total_extras,
                    SUM(r.horas_faltantes) as total_faltas
                FROM funcionarios f
                LEFT JOIN registros_jornada r ON f.id = r.funcionario_id
                GROUP BY f.id, f.nome, f.empresa
            """))
            
            print("   ✅ JOIN funcionando! Resultados:")
            for row in result:
                print(f"      ID {row[0]}: {row[1]} ({row[2]}) - {row[3]} registros - "
                      f"Extras: {row[4] or 0}h, Faltas: {row[5] or 0}h")
        
        except Exception as e:
            print(f"   ❌ Erro no JOIN: {e}")
    
    # 6. Verificar integridade referencial
    print("\n🔍 6. INTEGRIDADE REFERENCIAL:")
    try:
        result = session.execute(text("""
            SELECT r.id, r.funcionario_id
            FROM registros_jornada r
            LEFT JOIN funcionarios f ON r.funcionario_id = f.id
            WHERE f.id IS NULL
        """))
        
        registros_orfaos = result.fetchall()
        if registros_orfaos:
            print(f"   ⚠️  {len(registros_orfaos)} registro(s) órfão(s) (sem funcionário):")
            for reg in registros_orfaos:
                print(f"      Registro ID {reg[0]} referencia funcionário {reg[1]} (inexistente)")
        else:
            print("   ✅ Todos os registros têm funcionários válidos")
    
    except Exception as e:
        print(f"   ❌ Erro ao verificar integridade: {e}")
    
    # 7. Resumo final
    print("\n" + "=" * 70)
    print("📊 RESUMO:")
    print(f"   Funcionários: {num_func}")
    print(f"   Registros: {num_reg}")
    
    if num_func > 0 and num_reg > 0:
        print("   ✅ Banco parece estar OK para gerar relatórios")
    elif num_func > 0 and num_reg == 0:
        print("   ⚠️  Há funcionários mas nenhum registro de jornada")
        print("   💡 Cadastre jornadas na tela principal primeiro")
    elif num_func == 0:
        print("   ⚠️  Nenhum funcionário cadastrado")
        print("   💡 O sistema criará funcionários exemplo na primeira execução")
    
    print("=" * 70)
    
    session.close()

if __name__ == "__main__":
    try:
        diagnosticar_banco()
    except Exception as e:
        print(f"\n❌ ERRO CRÍTICO: {e}")
        import traceback
        traceback.print_exc()

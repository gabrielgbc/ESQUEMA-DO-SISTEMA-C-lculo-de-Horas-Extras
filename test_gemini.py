from services.ia_service import IAService

# Testa conexão
ia = IAService()

if ia.habilitado:
    print("✅ Gemini conectado com sucesso!")
    
    # Teste simples
    resposta = ia.responder_consulta("O que são horas extras?")
    print(f"\nResposta: {resposta}")
else:
    print("❌ Gemini não configurado")

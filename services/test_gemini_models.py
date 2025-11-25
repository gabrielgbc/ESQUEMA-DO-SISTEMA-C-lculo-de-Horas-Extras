"""
test_gemini_models.py
Verifica quais modelos Gemini estão disponíveis na sua API Key
"""
import os
from dotenv import load_dotenv
import google.generativeai as genai

# Carrega variáveis de ambiente
load_dotenv()

api_key = os.getenv('GEMINI_API_KEY')

if not api_key:
    print("❌ GEMINI_API_KEY não encontrada no arquivo .env")
    exit(1)

print("🔑 API Key encontrada!")
print(f"🔑 Primeiros caracteres: {api_key[:10]}...")

# Configura API
genai.configure(api_key=api_key)

print("\n📋 Listando modelos disponíveis:\n")
print("-" * 70)

try:
    modelos = genai.list_models()
    
    modelos_generativos = []
    
    for modelo in modelos:
        # Verifica se suporta generateContent
        if 'generateContent' in modelo.supported_generation_methods:
            modelos_generativos.append(modelo.name)
            print(f"✅ {modelo.name}")
            print(f"   Descrição: {modelo.display_name}")
            print(f"   Métodos: {', '.join(modelo.supported_generation_methods)}")
            print("-" * 70)
    
    if modelos_generativos:
        print(f"\n🎯 Total de modelos disponíveis para generateContent: {len(modelos_generativos)}")
        print(f"\n💡 Modelos recomendados para usar no código:")
        for modelo in modelos_generativos[:3]:  # Mostra os 3 primeiros
            # Remove o prefixo 'models/' se existir
            nome_limpo = modelo.replace('models/', '')
            print(f"   - '{nome_limpo}'")
        
        print("\n🧪 Testando geração de conteúdo com o primeiro modelo...")
        try:
            # Pega só o nome do modelo sem 'models/'
            nome_teste = modelos_generativos[0].replace('models/', '')
            model = genai.GenerativeModel(nome_teste)
            response = model.generate_content("Diga 'Olá' em uma palavra")
            print(f"✅ Teste bem-sucedido!")
            print(f"📝 Resposta: {response.text}")
            print(f"\n🎉 Use este modelo no seu código: '{nome_teste}'")
        except Exception as e:
            print(f"❌ Erro no teste: {e}")
    else:
        print("\n⚠️ Nenhum modelo disponível para generateContent")
        print("Isso pode indicar um problema com a API Key ou região")

except Exception as e:
    print(f"\n❌ Erro ao listar modelos: {e}")
    print("\nPossíveis causas:")
    print("1. API Key inválida ou expirada")
    print("2. Problemas de conexão com a internet")
    print("3. Serviço Google AI indisponível")
    print("4. Biblioteca google-generativeai desatualizada")
    print("\n💡 Tente:")
    print("   pip install --upgrade google-generativeai")
"""
services/ia_service.py
Serviço simples para integração com Gemini (Google Generative AI) e heurísticas de análise.

O arquivo tenta configurar a biblioteca `genai` quando disponível e usa uma
lista de modelos para tentar conectar. Caso a biblioteca ou a chave de API
não estejam disponíveis, o serviço permanece em modo degradado (não habilitado)
e oferece respostas fallback baseadas em regras locais.
"""

import os
from typing import List, Dict, Any

# dotenv é opcional; se existir, carrega variáveis de ambiente do .env
try:
    from dotenv import load_dotenv
    load_dotenv()
except Exception:
    pass

# Tentativa de importar a biblioteca genai (opcional)
try:
    import google.generativeai as genai   
except Exception:
    genai = None


class IAService:
    """Serviço responsável por conectar ao Gemini e prover utilitários de IA.

    A classe é tolerante à ausência da biblioteca `genai` ou da variável
    de ambiente `GEMINI_API_KEY`. Nestes casos, `habilitado` fica `False`
    e os métodos retornam respostas fallback.
    """

    def __init__(self):
        """Inicializa o serviço de IA e tenta conectar ao Gemini."""
        self.api_key = os.getenv('GEMINI_API_KEY')
        self.model = None
        self.habilitado = False

        if not self.api_key:
            print("⚠️ API Key do Gemini não encontrada. Funcionalidades de IA desabilitadas.")
            return

        if genai is None:
            print("⚠️ Biblioteca 'genai' não instalada. Instale via 'pip install google-generativeai'.")
            return

        try:
            genai.configure(api_key=self.api_key)

            modelos_para_tentar = [
                'gemini-2.0-flash'
            ]

            for nome_modelo in modelos_para_tentar:
                try:
                    print(f"🔄 Tentando modelo: {nome_modelo}")
                    self.model = genai.GenerativeModel(nome_modelo)
                    # Teste simples: apenas tente instanciar/usar o modelo.
                    # APIs podem variar; encapsulamos em try/except para ser tolerante.
                    try:
                        test_resp = None
                        # Tenta chamada mais comum (pode variar conforme versão)
                        if hasattr(self.model, 'generate_content'):
                            test_resp = self.model.generate_content("teste")
                        elif hasattr(self.model, 'generate'):
                            test_resp = self.model.generate({"input": "teste"})

                        print(f"✅ Modelo '{nome_modelo}' inicializado com sucesso.")
                        self.habilitado = True
                        break
                    except Exception:
                        # Se a chamada de teste falhar, tenta próximo modelo
                        self.model = None
                        continue
                except Exception as e:
                    print(f"⚠️ Modelo '{nome_modelo}' não disponível: {str(e)[:120]}")
                    continue

            if not self.habilitado:
                print("❌ Nenhum modelo Gemini disponível. Execute os testes para diagnóstico.")

        except Exception as e:
            print(f"❌ Erro ao configurar Gemini: {e}")
            self.model = None
            self.habilitado = False

    def responder_consulta(self, prompt: str) -> str:
        """Retorna uma resposta para a consulta `prompt`.

        Quando a IA não está habilitada, retorna uma mensagem fallback.
        """
        if not self.habilitado or self.model is None:
            return "[IA indisponível] Resposta automática: verifique configuração do GEMINI_API_KEY ou instale 'google-generativeai'."

        try:
            # Tenta usar APIs comuns de forma tolerante
            if hasattr(self.model, 'generate_content'):
                resp = self.model.generate_content(prompt)
                # Pode ser string ou objeto; normalize para string
                if isinstance(resp, str):
                    return resp
                # tenta extrair texto de campos comuns
                for attr in ('text', 'output', 'content'):
                    val = getattr(resp, attr, None)
                    if val:
                        return str(val)
                return str(resp)

            if hasattr(self.model, 'generate'):
                resp = self.model.generate({"input": prompt})
                if isinstance(resp, dict):
                    # tenta alguns caminhos comuns
                    return resp.get('output', resp.get('content', str(resp)))
                return str(resp)

            return "[IA] Não foi possível obter resposta do modelo configurado."

        except Exception as e:
            return f"[IA Erro] {str(e)}"

    def analisar_inconsistencias(self, registros: List[Any]) -> List[Dict[str, Any]]:
        """Analisa registros e retorna lista de inconsistências encontradas.

        Implementação leve baseada em regras (heurísticas). Se o serviço de IA
        estiver habilitado, essa função poderia ser estendida para enriquecer
        a análise via modelo generativo; por ora, usamos regras determinísticas.
        """
        problemas: List[Dict[str, Any]] = []

        for r in registros:
            try:
                h_extra = float(getattr(r, 'horas_extras', 0) or 0)
                h_falta = float(getattr(r, 'horas_faltantes', 0) or 0)
                rid = getattr(r, 'id', '')
                data = getattr(r, 'data', '')

                if h_extra >= 8:
                    problemas.append({
                        'mensagem': f"Registro {rid} ({data}): horas extras muito altas ({h_extra:.2f}h).",
                        'gravidade': 'alta'
                    })
                elif h_extra >= 2:
                    problemas.append({
                        'mensagem': f"Registro {rid} ({data}): horas extras elevadas ({h_extra:.2f}h).",
                        'gravidade': 'média'
                    })

                if h_falta > 0:
                    grav = 'média' if h_falta < 2 else 'alta'
                    problemas.append({
                        'mensagem': f"Registro {rid} ({data}): horas faltantes ({h_falta:.2f}h).",
                        'gravidade': grav
                    })

            except Exception:
                continue

        return problemas
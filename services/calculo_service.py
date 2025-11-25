"""
services/calculo_service.py
Serviço para cálculo de horas trabalhadas, extras e faltantes
"""
from datetime import datetime, time, timedelta

class CalculoService:
    
    @staticmethod
    def calcular_horas_trabalhadas(hora_entrada, hora_saida, intervalo=0.0):
        """
        Calcula as horas trabalhadas
        
        Args:
            hora_entrada: objeto time
            hora_saida: objeto time
            intervalo: horas de intervalo (float)
        
        Returns:
            float: horas trabalhadas
        """
        # Converte time para datetime para fazer cálculos
        dt_entrada = datetime.combine(datetime.today(), hora_entrada)
        dt_saida = datetime.combine(datetime.today(), hora_saida)
        
        # Se saída for menor que entrada, passou da meia-noite
        if dt_saida < dt_entrada:
            dt_saida += timedelta(days=1)
        
        # Calcula diferença
        diferenca = dt_saida - dt_entrada
        horas_totais = diferenca.total_seconds() / 3600
        
        # Subtrai intervalo
        horas_trabalhadas = horas_totais - intervalo
        
        return round(horas_trabalhadas, 2)
    
    @staticmethod
    def calcular_horas_extras_e_faltantes(horas_trabalhadas, carga_horaria_diaria):
        """
        Calcula horas extras e horas faltantes
        
        Args:
            horas_trabalhadas: float
            carga_horaria_diaria: float
        
        Returns:
            tuple: (horas_extras, horas_faltantes)
        """
        diferenca = horas_trabalhadas - carga_horaria_diaria
        
        if diferenca > 0:
            horas_extras = round(diferenca, 2)
            horas_faltantes = 0.0
        else:
            horas_extras = 0.0
            horas_faltantes = round(abs(diferenca), 2)
        
        return horas_extras, horas_faltantes
    
    @staticmethod
    def calcular_jornada_completa(hora_entrada, hora_saida, intervalo, carga_horaria_diaria):
        """
        Calcula todas as informações da jornada
        
        Returns:
            dict: {horas_trabalhadas, horas_extras, horas_faltantes}
        """
        horas_trabalhadas = CalculoService.calcular_horas_trabalhadas(
            hora_entrada, hora_saida, intervalo
        )
        
        horas_extras, horas_faltantes = CalculoService.calcular_horas_extras_e_faltantes(
            horas_trabalhadas, carga_horaria_diaria
        )
        
        return {
            'horas_trabalhadas': horas_trabalhadas,
            'horas_extras': horas_extras,
            'horas_faltantes': horas_faltantes
        }
    
    @staticmethod
    def calcular_valor_horas_extras(horas_extras, valor_hora, percentual=1.5):
        """
        Calcula o valor monetário das horas extras
        
        Args:
            horas_extras: float
            valor_hora: float
            percentual: float (padrão 1.5 = 50% adicional)
        
        Returns:
            float: valor em reais
        """
        return round(horas_extras * valor_hora * percentual, 2)
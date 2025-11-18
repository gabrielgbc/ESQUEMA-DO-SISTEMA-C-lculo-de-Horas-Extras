# **ESQUEMA DO SISTEMA – Cálculo de Horas Extras**

## **🎯 Objetivo**

Criar um sistema simples e intuitivo para registrar jornadas de trabalho e calcular automaticamente horas extras dos funcionários, considerando regras de jornada, carga horária e bancos de horas.  
O sistema deve ser construído em **Python**, com:

-   **Tkinter** para interface gráfica
    
-   **SQLAlchemy** para modelagem de dados
    
-   Estrutura preparada para **integração futura com uma API de IA**
    

----------

## **👥 Público-Alvo**

-   Pequenas empresas
    
-   Lojas e comércios que controlam ponto manualmente
    
-   RH e gestores que desejam um cálculo rápido e automático
    
-   Estudantes/profissionais aprendendo Python, Tkinter e SQLAlchemy
    

----------

## **🧩 Funcionalidades do Sistema**

### **1. Cadastro de Funcionários**

-   Nome
    
-   Cargo
    
-   Carga horária diária (ex.: 8h)
    
-   Valor por hora
    

### **2. Registro de Jornada**

-   Data
    
-   Horário de entrada
    
-   Horário de saída
    
-   Intervalo
    
-   Cálculo automático de:
    
    -   Horas trabalhadas
        
    -   Horas extras
        
    -   Horas faltantes
        

### **3. Relatórios**

-   Total de horas extras por período
    
-   Total de horas trabalhadas
    
-   Visualização individual por funcionário
    

### **4. Banco de Dados (SQLAlchemy)**

Tabelas:

-   `Funcionario`
    
-   `RegistroJornada`
    
-   `ConfiguracoesEmpresa` (opcional)
    

Relacionamentos:

-   Um funcionário → vários registros de jornada
    

----------

## **🧠 Uso Futuro de Agentes Inteligentes**

O sistema será preparado para aceitar uma **API de IA** em etapas posteriores, com aplicações como:

### **1. Agente para Sugestão Automática**

-   IA analisa padrões de ponto
    
-   Sugere correções (ex.: esquecimentos de intervalo)
    

### **2. Agente para Auditoria**

-   Detecção de inconsistências
    
-   Alertas sobre horas extras excessivas
    

### **3. Assistente Conversacional**

-   Usuário fala: _"Calcule as horas extras do João esta semana"_
    
-   IA responde com base no banco de dados
    

### **4. Geração de relatórios inteligentes**

-   IA gera PDFs, insights e análises automáticas

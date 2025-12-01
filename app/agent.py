# === Importações ===
import os
from app.tools import calculate_math_expression, calculate_compound_interest, get_ticker_price
from strands import Agent
from strands.models.ollama import OllamaModel
from dotenv import load_dotenv
from datetime import datetime

# === Variáveis de ambiente ===
load_dotenv()

class NexusAgent:
    """
    O agente inteligente financeiro NEXUS é capaz de responder consultas sobre valores de ações e realizar cálculos matemático-financeiros.
    """
    def __init__(self):
        # Define o modelo llama3.1 pelo Ollama
        self.ollama_model = OllamaModel(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            model_id="llama3.1"
        )

        # Define as tools criadas em tools.py
        self.tools = [
            get_ticker_price,
            calculate_compound_interest,
            calculate_math_expression
        ]

        # Define o system prompt em formato TOON
        self.system_prompt = f"""
        You are NEXUS, an advanced financial AI assistant.
        Rules:
        1. Use 'calculate_math_expression' for ANY math calculation.
        2. Use 'get_ticker_price' for stock info.
        3. Use 'calculate_compound_interest' for compound interest calculations.
        4. Be concise.
        
        AGENT_PROFILE:
          name: Nexus
          role: Executive Assistant & Orchestrator
          boss: "André Codea (CEO of WedgeDynamics)"
          channel: Streamlit Chat via FastAPI connection.
          tone:
            style: "Natural, humano, breve, eficiente."
            forbidden: "Linguagem robótica, excessivamente formal ou pedidos de desculpas desnecessários."
        
        CONTEXT_VARIABLES:
          current_date_and_time: {datetime.now()}
        
        GLOBAL_DIRECTIVES:
          - "Você é um AGENTE FINANCEIRO, quaisquer consultas que não envolvam matemática ou finanças não são sua responsabilidade"
          - "O raciocínio (think/CoT) é interno. O usuário vê apenas a resposta final."
          - "Nunca invente dados (taxa, tempo, valor). Se faltar dado, PERGUNTE."
          - "Priorize respostas curtas e diretas"
          - "CRÍTICO: Para respostas financeiras, o uso das tools é OBRIGATÓRIO."

        CHAIN_OF_THOUGHT:
          step_1_analyze: "Identificar a intenção (Calcular, Buscar ação (Ticker), jogar conversa fora)"
          
          step_2_validate:
            Cálculo genérico: requer a tool de cálculo (calculate_math_expression).
            Buscar ação: requer o nome da ação.
            Cálculo de juros: requer a tool de cálculo de juros (calculate_compound_interest)
        
          step_3_decision:
            - "IF info_missing OR context_vague THEN ask_user(missing_info)"
            - "IF data_complete THEN call_tool(tool)"
    
        TOOLS_SPEC:
            get_ticker_price:
                description: "Busca o valor de uma ação no mercado via yfinance."
                trigger: "Consulta de preço de alguma ação do mercado, ou consulta para cálculo envolvendo alguma ação."
    
            calculate_math_expression:
                description: "Realiza cálculos de expressões matemáticas comuns"
                trigger: "Consulta para cálculo de expressões matemáticas."

            calculate_compound_interest:
                description: "Calcula os juros compostos sobre o tempo."
                trigger: "Solicitação para calcular os rendimentos de alguma ação."

        FEW_SHOT_EXAMPLES:
            - input: "Quanto é 1234 vezes 5678?"
              reasoning: "Solicitação de cálculo matemático simples."
              tool_call: "calculate_math_expression(expression='1234 * 5678')"
              output: "O resultado é 7.006.652. 🧮"
        
            - input: "Qual o valor da ação da Petrobras hoje?"
              reasoning: "Solicitação de cotação de mercado. Identificado ticker PETR4.SA."
              tool_call: "get_ticker_price(ticker='PETR4.SA')"
              output: "O preço atual de PETR4.SA é R$ 36,50. 📉"
        
            - input: "Quanto rende 1000 reais investidos a 10% ao ano por 5 anos?"
              reasoning: "Cálculo de investimento/juros compostos. Principal=1000, Taxa=10, Tempo=5."
              tool_call: "calculate_compound_interest(amount=1000, rate=10, time=5)"
              output: "Ao final de 5 anos, você terá acumulado R$ 1.610,51. 💰"
        
            - input: "Qual a raiz quadrada de 144?"
              reasoning: "Cálculo matemático avançado. Requer sintaxe python (math)."
              tool_call: "calculate_math_expression(expression='math.sqrt(144)')"
              output: "A raiz quadrada de 144 é 12.0."
        
            - input: "O que é um fundo imobiliário?"
              reasoning: "Pergunta conceitual. Nenhuma ferramenta necessária."
              tool_call: null
              output: "Um Fundo Imobiliário (FII) é um fundo de investimento destinado à aplicação em empreendimentos imobiliários..."
        """

        # Cria o agente com o modelo, tools e o system prompt
        self.agent = Agent(
            model=self.ollama_model,
            tools=self.tools,
            system_prompt=self.system_prompt
        )

    # Cria o chat com o loop de execução
    def chat(self, user_message: str):
        """
        Gets user prompt and generates response.
        """
        try:
            # Exibe a consulta do usuário
            print(f"User: {user_message}")

            # Reitera o system prompt e concatena à consulta do usuário
            full_prompt = f"{self.system_prompt}\n\nUser Question: {user_message}"

            # Gera a resposta
            response = self.agent(full_prompt)

            # Formata a resposta para texto
            if isinstance(response, dict) and "parameters" in response:
                final_answer = response["parameters"].get("message", str(response))
            elif isinstance(response, list):
                final_answer = str(response[-1])
            else:
                final_answer = str(response)

            # Exibe a resposta de debug e a resposta final
            print(f"Nexus (Raw): {response}")
            print(f"Nexus (Raw): {final_answer}")

            return final_answer
        except Exception as e:
            print(f"Error: {e}")
            return f"Error processing your request: {str(e)}"
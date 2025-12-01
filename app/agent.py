# === Importações Necessárias ===
import os
from datetime import datetime
from dotenv import load_dotenv

# Importa o SDK do Strands e o conector do Ollama
from strands import Agent
from strands.models.ollama import OllamaModel

# Importa as ferramentas que criamos no tools.py
from app.tools import (
    calculate_math_expression,
    calculate_compound_interest,
    get_ticker_price,
    get_company_info,
    get_ticker_news
)

# Carrega variáveis de ambiente (.env)
load_dotenv()


class NexusAgent:
    """
    Classe principal do Agente NEXUS.
    Responsável por configurar o modelo (Cérebro), as ferramentas (Mãos)
    e as regras de comportamento (System Prompt).
    """

    def __init__(self):
        # 1. Configuração do llm
        self.ollama_model = OllamaModel(
            host=os.getenv("OLLAMA_HOST", "http://localhost:11434"),
            model_id="llama3.1"
        )

        # 2. Configuração das tools
        self.tools = [
            get_ticker_price,
            calculate_compound_interest,
            calculate_math_expression,
            get_ticker_news,
            get_company_info
        ]

        # 3. Configuração da Personalidade (System Prompt)
        # ADICIONEI O EXEMPLO DE "OLÁ" NOS FEW-SHOTS ABAIXO PARA ELE NÃO TRAVAR
        self.system_prompt = f"""
        You are NEXUS, an advanced financial AI assistant.

        AGENT_PROFILE:
          name: Nexus
          role: Financial Assistant
          tone: Natural, concise, and efficient.
          language: Portuguese (BR).

        CONTEXT_VARIABLES:
          current_date_and_time: {datetime.now()}

        RULES:
          1. Use 'calculate_math_expression' for math.
          2. Use 'get_ticker_price' for price history/trends.
          3. Use 'get_company_info' for fundamentals (Sector, P/E, Business).
          4. Use 'get_ticker_news' for latest news/events.
          5. STRATEGY: If the user asks for a "Summary" or "Analysis" of a stock, USE MULTIPLE TOOLS (Price + News + Info) before answering.
          6. If the user greets, answer directly without tools.
          7. FORMATTING: Use Markdown (bold, lists). NEVER use LaTeX math formatting (like \frac, ^, \c).
          8. Speak naturally. Use spaces between numbers and words.
          9. Round numbers to 2 decimal places (e.g., R$ 35.50, not 35.502391).
          10. ALWAYS answer in normal, brazilian portuguese text.

        FEW_SHOT_EXAMPLES (How to behave):
            - User: "Quanto é 50 * 50?"
              Reasoning: Math detected.
              Tool: calculate_math_expression("50 * 50")
              Output: "A resposta é 2500."
              
            - User: "Resumo da Apple"
              Reasoning: Analysis requested. Need price, info and news.
              Tool 1: get_ticker_price("AAPL")
              Tool 2: get_company_info("AAPL")
              Tool 3: get_ticker_news("AAPL")
              Tool 4: calculate_math_expression
            
            - User: "Por que a Vale caiu?"
              Reasoning: Explanation needed. Need news and recent price trend.
              Tool 1: get_ticker_price("VALE3.SA")
              Tool 2: get_ticker_news("VALE3.SA")
              

            - User: "Preço da Petrobras"
              Reasoning: Market data detected.
              Tool: get_ticker_price("PETR4.SA")

            - User: "Olá, tudo bem?"
              Reasoning: Greeting detected. No tool needed.
              Output: "Olá! Sou o NEXUS, seu assistente financeiro. Como posso ajudar você hoje?"

            - User: "O que é um ETF?"
              Reasoning: General question. No tool needed.
              Output: "Um ETF (Exchange Traded Fund) é um fundo de investimento negociado em bolsa como se fosse uma ação..."
        """

        # 4. Inicialização do agente
        self.agent = Agent(
            model=self.ollama_model,
            tools=self.tools,
            system_prompt=self.system_prompt
        )

    def chat(self, user_message: str):
        """
        Chamada da API para processar a mensagem do usuário.
        """
        try:
            print(f"User: {user_message}")

            response = self.agent(user_message)
            final_answer = ""

            # === TRATAMENTO DE RESPOSTA ===

            # Caso 1: O Agente devolveu um Dicionário (JSON)
            if isinstance(response, dict):

                tool_name = response.get("name")

                # Se o nome da tool for "None" (string) ou None (nulo), é apenas conversa.
                if tool_name is None or str(tool_name) == "None":
                    final_answer = "Olá! Sou o NEXUS. Como posso ajudar com seus cálculos ou investimentos?"

                # Caso Tool de Mensagem (Padrão Strands)
                elif "parameters" in response and "message" in response["parameters"]:
                    final_answer = response["parameters"]["message"]

                # Caso Tool Call Real (Fallback Manual)
                elif tool_name is not None:
                    print(f"⚠️ Tentativa de tool manual: {tool_name}")
                    # Busca a ferramenta na lista
                    target_tool = next((t for t in self.tools if t.__name__ == tool_name), None)

                    if target_tool:
                        try:
                            params = response.get("parameters", {})
                            print(f"🛠️ Executando {tool_name} manualmente...")
                            result = target_tool(**params)
                            final_answer = str(result)
                        except Exception as tool_err:
                            final_answer = f"Erro ao executar ferramenta: {tool_err}"
                    else:
                        final_answer = f"Tentei usar a ação '{tool_name}', mas não consegui."

            # Caso 2: Lista (Histórico)
            elif isinstance(response, list):
                final_answer = str(response[-1])

            # Caso 3: String direta
            else:
                final_answer = str(response)

            # Limpeza final de segurança
            if "name': 'None" in str(final_answer) or "name': None" in str(final_answer):
                final_answer = "Olá! Como posso ajudar você hoje?"

            print(f"Nexus Output: {final_answer}")
            return final_answer

        except Exception as e:
            print(f"Critical Error: {e}")
            return f"Ocorreu um erro no processamento: {str(e)}"
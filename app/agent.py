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

        # 3. Configuração da Personalidade
        self.system_prompt = f"""
                You are NEXUS, an expert Financial AI Assistant.

                CURRENT CONTEXT:
                  Date: {datetime.now()}
                  Language: Portuguese (BR)

                ### YOUR TOOLKIT (ONLY use these):
                1. `calculate_math_expression`: For ANY math (e.g., "10 * 5", "sqrt(144)").
                2. `get_ticker_price`: For stock prices/history (e.g., "PETR4.SA").
                3. `get_company_info`: For company fundamentals (Sector, P/E).
                4. `get_ticker_news`: For market news.
                5. `calculate_compound_interest`: For investment projection.

                ### CRITICAL PROTOCOL - READ CAREFULLY:

                [WHEN TO USE A TOOL]
                - Only use a tool if the user asks for DATA or CALCULATION.
                - Example: "Calculate...", "Price of...", "News about...".

                [WHEN *NOT* TO USE A TOOL]
                - If the user greets you ("Olá", "Oi").
                - If the user asks for an explanation/concept ("O que é ETF?", "Quem é você?").
                - If you are just answering a question.

                [PROHIBITED ACTIONS]
                - NEVER invent tools like "answer", "get_response", "reply", "no_tool". 
                - If no tool is needed, WRITE TEXT DIRECTLY. Do not wrap it in JSON.
                - NEVER use LaTeX formatting (like \frac, ^, $). Use plain text.

                ### EXAMPLES OF CORRECT BEHAVIOR:

                User: "Olá, tudo bem?"
                (Analysis: Greeting. No tool needed.)
                Nexus: "Olá! Tudo ótimo. Sou o NEXUS, seu assistente financeiro. Como posso ajudar?"

                User: "O que é uma ação?"
                (Analysis: Conceptual question. No tool needed.)
                Nexus: "Uma ação é a menor parcela do capital social de uma empresa..."

                User: "Quanto é 50 vezes 12?"
                (Analysis: Math needed.)
                Tool Call: calculate_math_expression(expression="50 * 12")

                User: "Preço da Vale"
                (Analysis: Market data needed.)
                Tool Call: get_ticker_price(ticker="VALE3.SA")
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

            # Envia mensagem
            response = self.agent(user_message)
            final_answer = ""

            # === TRATAMENTO DE RESPOSTA ===

            # Caso 1: O Agente devolveu um JSON (Tentativa de usar ferramenta)
            if isinstance(response, dict):

                tool_name = response.get("name")
                params = response.get("parameters", {})

                # Lista de nomes reais das suas ferramentas
                valid_tool_names = [t.__name__ for t in self.tools]

                # CENÁRIO A: É uma ferramenta
                if tool_name in valid_tool_names:
                    print(f"🛠️ Tool Call Válido: {tool_name}")
                    target_tool = next((t for t in self.tools if t.__name__ == tool_name), None)

                    try:
                        result = target_tool(**params)
                        final_answer = str(result)
                    except Exception as tool_err:
                        final_answer = f"Erro técnico ao executar {tool_name}: {tool_err}"

                # CENÁRIO B: É uma alucinação ("answer", "get_response", etc)
                else:
                    print(f"⚠️ Alucinação de Tool ignorada: {tool_name}")

                    # 1. Tenta chaves conhecidas primeiro
                    candidates = [
                        params.get("text"),
                        params.get("message"),
                        params.get("input_text"),
                        params.get("response"),
                        params.get("output")
                    ]
                    # Pega o primeiro que não for None
                    extracted_text = next((item for item in candidates if item is not None), None)

                    # 2. Se não achou, pega o primeiro string que encontrar no dicionário
                    if not extracted_text and params:
                        for value in params.values():
                            if isinstance(value, str):
                                extracted_text = value
                                break

                    # Define a resposta final
                    if extracted_text:
                        final_answer = str(extracted_text)
                    else:
                        # Se o JSON veio vazio ou sem texto útil
                        final_answer = "Olá! Sou o NEXUS. Como posso ajudar com seus investimentos hoje?"

            # Caso 2: Lista
            elif isinstance(response, list):
                final_answer = str(response[-1])

            # Caso 3: String direta
            else:
                final_answer = str(response)

            # Limpeza final de segurança
            if "name':" in str(final_answer) or "parameters':" in str(final_answer):
                final_answer = "Olá! Como posso ajudar você?"

            print(f"Nexus Output (Clean): {final_answer}")
            return final_answer

        except Exception as e:
            print(f"Critical Error: {e}")
            return f"Ocorreu um erro no processamento: {str(e)}"
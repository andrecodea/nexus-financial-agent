# === Importações Necessárias ===
import os
import re
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
            model_id="qwen3:8b"
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
                - NEVER use LaTeX formatting (like \frac, ^, $). Use PLAIN TEXT.
                - NEVER use Markdown formatting (like **, *, $). Use PLAIN TEXT.

                ### EXAMPLES OF CORRECT BEHAVIOR:

                User: "Olá, tudo bem?"
                (Analysis: Greeting. No tool needed.)
                Nexus: "Olá! Sou o NEXUS, seu assistente financeiro. Como posso ajudar?"

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

    # === Função de limpeza da resposta ===
    def clean_response(self, text: str) -> str:
        """
        Cleans response from LaTeX formatting.
        """
        # 1. Remove delimitadores de LaTeX comuns: \(, \), \[, \]
        text = re.sub(r'\\\(|\\\)|\\\[|\\\]', '', text)
        # 2. Remove o símbolo de dólar solto usado para abrir fórmulas
        text = text.replace("$", "")
        text = text.replace("R ", "R$ ")
        # 3. Remove caracteres de escape
        text = text.replace("\\c", "").replace("^", "")

        return text

    # === Função de chat ===
    def chat(self, user_message: str):
        """
        Chamada de API
        """
        try:
            print(f"User: {user_message}")
            response = self.agent(user_message)
            final_answer = ""

            # === TRATAMENTO DE RESPOSTA ===

            if isinstance(response, dict):
                tool_name = response.get("name")
                params = response.get("parameters", {})

                # Lista de ferramentas reais
                valid_tools = [t.__name__ for t in self.tools]

                # 1. Verifica se a tool é real.
                if tool_name in valid_tools:
                    target_tool = next((t for t in self.tools if t.__name__ == tool_name), None)
                    try:
                        print(f"🛠️ Executing: {tool_name}")
                        final_answer = str(target_tool(**params))
                    except Exception as e:
                        final_answer = f"Erro na ferramenta: {e}"

                # 2. Se for falsa, extrai texto.
                else:
                    print(f"⚠️ JSON não executável detectado: {response}")

                    # Tenta varrer chaves comuns de texto
                    candidates = [
                        params.get("input_text"), params.get("message"),
                        params.get("text"), params.get("response"), params.get("output"),
                        response.get("response")  # Às vezes vem na raiz
                    ]

                    # Pega o primeiro valor de texto válido
                    text_found = next((item for item in candidates if item), None)

                    if text_found:
                        final_answer = str(text_found)

                    # Se não achou texto mas tem valores soltos no params
                    elif params:
                        # Tenta pegar o primeiro valor string que achar
                        for v in params.values():
                            if isinstance(v, str):
                                final_answer = v
                                break

            elif isinstance(response, list):
                if response:
                    final_answer = str(response[-1])
            else:
                final_answer = str(response)

            # Remove espaços em branco
            clean_check = str(final_answer).strip()

            # Lista de respostas "lixo" que queremos substituir por saudação
            garbage_responses = ["{}", "[]", "None", "{'name': None}", "{'parameters': {}}"]

            # Se a resposta estiver vazia ou for lixo técnico
            if not clean_check or clean_check in garbage_responses:
                final_answer = "Olá! Sou o NEXUS, seu assistente financeiro. Como posso ajudar com seus investimentos hoje?"

            print(f"Nexus Output: {final_answer}")
            return final_answer

        except Exception as e:
            print(f"Error: {e}")
            return f"Erro interno: {str(e)}"
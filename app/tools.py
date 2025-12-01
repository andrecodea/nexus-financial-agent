import yfinance as yf
import math
from strands import tool


# === 1. TOOL de cotação com histórico ===
@tool
def get_ticker_price(ticker: str) -> str:
    """
    Retrieves the stock price history for the last 5 days.
    Useful to analyze trends (rising/falling).
    Input: Ticker symbol (e.g., 'PETR4.SA', 'AAPL').
    """
    try:
        stock = yf.Ticker(ticker)
        # Pega 5 dias para análise de tendência
        hist = stock.history(period="5d")

        if hist.empty:
            return f"Não encontrei dados para o ticker '{ticker}'."

        # Formata uma "tabela" em texto para o LLM ler
        # Ex: "Data: 2023-10-01 | Fechamento: R$ 35.00"
        report = f"=== Histórico Recente de {ticker} ===\n"
        for date, row in hist.iterrows():
            date_str = date.strftime('%d/%m/%Y')
            price = row['Close']
            report += f"- Data: {date_str} | Preço: R$ {price:.2f}\n"

        # Adiciona o preço atual (último)
        last_price = hist['Close'].iloc[-1]
        report += f"\nPreço Atual Referência: R$ {last_price:.2f}"

        return report

    except Exception as e:
        return f"Erro ao buscar cotação: {str(e)}"


# === 2. TOOL de informações sobre a empresa ===
@tool
def get_company_info(ticker: str) -> str:
    """
    Retrieves fundamental data about a company: Sector, PE Ratio, Dividend Yield, and Business Summary.
    Use this when the user asks for a 'summary', 'analysis', or 'what is this company'.
    """
    try:
        stock = yf.Ticker(ticker)
        info = stock.info

        # Extração segura de dados (pode vir nulo)
        name = info.get('longName', ticker)
        sector = info.get('sector', 'N/A')
        pe = info.get('trailingPE', 'N/A')
        div_yield = info.get('dividendYield', 0)
        if div_yield:
            div_yield = f"{div_yield * 100:.2f}%"

        summary = info.get('longBusinessSummary', 'Descrição indisponível.')[:400] + "..."  # Limita tamanho

        return f"""
        === Fundamentos de {name} ===
        Setor: {sector}
        P/L (Preço/Lucro): {pe}
        Dividend Yield: {div_yield}
        Resumo: {summary}
        """
    except Exception as e:
        return f"Erro ao buscar fundamentos: {str(e)}"


# === 3. TOOL de noticías recentes ===
@tool
def get_ticker_news(ticker: str) -> str:
    """
    Retrieves the top 3 latest news headlines for a specific stock ticker.
    Use this to explain why a stock is moving or for general updates.
    """
    try:
        stock = yf.Ticker(ticker)
        news_list = stock.news

        if not news_list:
            return f"Sem notícias recentes para {ticker}."

        report = f"=== Últimas Notícias de {ticker} ===\n"
        # Pega as 3 primeiras
        for item in news_list[:3]:
            title = item.get('title', 'Sem título')
            publisher = item.get('publisher', 'Fonte desc.')
            link = item.get('link', '')
            report += f"- [{publisher}] {title} (Link: {link})\n"

        return report
    except Exception as e:
        return f"Erro ao buscar notícias: {str(e)}"


# === 4. Ferramentas Matemáticas ===
# Calculadora de juros
@tool
def calculate_compound_interest(amount: float, rate: float, time: int) -> str:
    """
    Calculates compound interest. Input: amount, rate (%), time (years).
    """
    try:
        total = amount * (1 + rate / 100) ** time
        return f"Investing ${amount} at {rate}% for {time} years results in ${total:.2f}"
    except Exception as e:
        return f"Error: {str(e)}"

# Calculadora
@tool
def calculate_math_expression(expression: str) -> str:
    """
    Evaluates python math expressions (e.g., '1234 * 5678', 'math.sqrt(144)').
    """
    try:
        result = eval(expression)
        return f"Result: {str(result)}"
    except Exception as e:
        return "Invalid expression."

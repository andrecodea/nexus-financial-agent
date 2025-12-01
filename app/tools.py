# === FERRAMENTAS DO AGENTE ===
import yfinance as yf
import math
from strands import tool

# === Tool de cotação da bolsa ===
@tool
def get_ticker_price(ticker:str):
    """
    Retrieves the current stock price for a given ticker symbol (e.g., 'AAPL', 'PETR4.SA').
    Returns the price as a string.
    :param ticker:
    :return ticker price:
    """
    try:
        stock = yf.Ticker(ticker)
        history = stock.history(period='1d')
        if history.empty:
            return f"Symbol '{ticker}' not found."

        preco = history['Close'].iloc[0]
        return f"The price of {ticker} is R$ {stock:.2f}"
    except Exception as e:
        return f"Error fetching price for {ticker}: {str(e)}"

# === Tool para cálculo de juros compostos ===
@tool
def calculate_compound_interest(amount:float, rate:float, time:int):
    """
    Calculates the future value of an investment using compound interest logic.
    Input: principal amount, annual rate (in %), and time in years.
    :param amount:
    :param rate:
    :param time:
    :return compound interest:
    """
    try:
        total = amount * (1 + rate/100) ** time
        return f"Investing ${amount} at {rate}% for {time} years will result in ${total:.2f}"
    except Exception as e:
        return f"Error calculating interest: {str(e)}"

# === Tool de calculadora genérica ===
@tool
def calculate_math_expression(expression:str):
    """
    Evaluates a mathematical expression provided as a string.
    Input should be a valid Python mathematical string (e.g., '1234 * 5678' or 'math.sqrt(144)').
    :param expression:
    :return calculation result:
    """
    try:
        result = eval(expression)
        return f"The result of the expression {expression} is: {str(result)}"
    except Exception as e:
        return "Invalid expression. Please provide a valid mathematical formula."


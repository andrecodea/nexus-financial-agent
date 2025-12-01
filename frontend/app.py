import requests.exceptions
import streamlit as st
import yfinance as yf
import pandas as pd

# === Configuração da Página ===
st.set_page_config(
    page_title="NEXUS Financial",
    page_icon="📈",
    layout="wide"
)

# === Título e Header
st.title("NEXUS: Agente Inteligente Financeiro")
st.markdown('---')

# === Sidebar (Dash de ações)===
with st.sidebar:
    st.header("Market Monitor")
    st.write("Visualize ações em tempo real enquanto conversa")
    ticker = st.text_input("Digite o nome do Ticker (ex: AAPL, PETR4.SA:):", value="PETR4.SA")

    if st.button("Carregar Gráfico"):
        try:
            with st.spinner(f"Buscado dados de {ticker}..."):
                stock=yf.Ticker(ticker)
                hist = stock.history(period="1mo")

                if not hist.empty:
                    st.line_chart(hist['Close'])
                    current_price = hist['Close'].iloc[-1]
                    st.metric(
                        label=f"Preço Atual ({ticker})",
                        value=f"R$ {current_price:.2f}"
                    )
                else:
                    st.error("Ticker não encontrado ou sem dados.")
        except Exception as e:
            st.error(f"Erro ao carregar gráfico: {e}")

        st.markdown('---')
        st.info("O Agente NEXUS pode calcular juros, buscar ações de mercado e realizar cálculos matemáticos.")

# === Memória do Chat com Session State ===
if "messages" not in st.session_state:
    st.session_state.messages = []

# === Histórico de Mensagens ===
for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])

# === User Input ===
if prompt := st.chat_input("Pergunte algo sobre finanças ou matemática..."):
    st.chat_message("user").markdown(prompt) # mostra a mensagem do usuário
    st.session_state.messages.append({"role":"user", "content":prompt}) # adiciona à mensagem ao histórico

    # === Chamada de API ===
    try:
        with st.spinner("NEXUS está pensando..."):
            response = requests.post(
                "http://127.0.0.1:8000/chat",
                json={"message":prompt}
            )

            if response.status_code == 200:
                data = response.json()
                bot_response = data["response"]
                st.chat_message("assistant").markdown(bot_response)
                st.session_state.messages.append({"role":"assistant", "content":bot_response})
            else:
                st.error("Erro na API: {response.status_code} - {response.text}")
    except requests.exceptions.ConnectionError:
        st.error("Não foi possível conectar ao servidor. 'uvicorn' deve estar rodando!")
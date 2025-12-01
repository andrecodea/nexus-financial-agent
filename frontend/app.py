import requests.exceptions
import streamlit as st
import yfinance as yf
import pandas as pd

def main():
    # === Configuração da Página ===
    st.set_page_config(
        page_title="NEXUS Financial",
        page_icon="📈",
        layout="wide"
    )

    # === Título e Header ===
    st.title("NEXUS: Agente Inteligente Financeiro")
    st.markdown('---')

    # === Estado do Gráfico ===
    if "chart_ticker" not in st.session_state:
        st.session_state.chart_ticker = None

    # === Sidebar (Dash de ações)===
    with st.sidebar:
        st.header("Arquitetura do Sistema")
        st.info(
            """
            **Como funciona:**
            1. **Frontend:** Streamlit
            2. **Backend:** FastAPI (Porta 8000)
            3. **Agente:** Strands SDK + Ollama
            """
        )

        st.markdown("---")

        st.header("Monitor de Mercado")
        st.write("Visualize ações em tempo real enquanto conversa")
        ticker_input = st.text_input("Ticker da Ação:", value="PETR4.SA", key="input_ticker")

        # Atualização de estado
        if st.button("Carregar Gráfico"):
            st.session_state.chart_ticker = ticker_input

        # Renderização do gráfico
        if st.session_state.chart_ticker:
            ticker = st.session_state.chart_ticker
            try:
                with st.spinner(f"Atualizando {ticker}..."):
                    stock = yf.Ticker(ticker)
                    hist = stock.history(period="5d")

                    if not hist.empty:
                        current_price = hist['Close'].iloc[-1]
                        previous_price = hist['Close'].iloc[-2] if len(hist) > 1 else current_price
                        delta = current_price - previous_price

                        # Pega a data exata do último dado disponível
                        last_date = hist.index[-1].strftime('%d/%m/%Y')

                        st.metric(
                            label=f"Preço Atual ({ticker})",
                            value=f"R$ {current_price:.2f}",
                            delta=f"{delta:.2f} (Desde o último fechamento)"
                        )

                        st.line_chart(hist['Close'])
                        st.caption(f"**Atualizado em:** {last_date}")
                        st.caption("Nota: Cotações podem ter delay de 15min ou referir-se ao último pregão fechado.")

                    else:
                        st.warning(f"Sem dados para '{ticker}'.")
            except Exception as e:
                st.error(f"Erro: {e}")

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
            # Tenta realizar um POST à API
            with st.spinner("NEXUS está pensando..."):
                response = requests.post(
                    "http://127.0.0.1:8000/chat",
                    json={"message":prompt}
                )

                # Se a resposta for positiva, a resposta do agente é exibida
                if response.status_code == 200:
                    data = response.json()
                    bot_response = data["response"]
                    st.chat_message("assistant").markdown(bot_response)
                    st.session_state.messages.append({"role":"assistant", "content":bot_response})
                else:
                    st.error("Erro na API: {response.status_code} - {response.text}")
        except requests.exceptions.ConnectionError:
            st.error("Não foi possível conectar ao servidor. 'uvicorn' deve estar rodando!")

if __name__ == "__main__":
    main()
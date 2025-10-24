import streamlit as st
import pandas as pd
import plotly.graph_objs as go
from trading_strategy import main, analyze_results

# Run backend to get data
data = None
positions = None
try:
    positions = main()
    data = None  # Not returned by main, so reload for chart
except Exception as e:
    st.error(f"Error running backend: {e}")

# If needed, reload price data for chart
def get_price_data():
    import yfinance as yf
    stock = yf.Ticker("MSFT")
    return stock.history(period="5y")

if data is None:
    data = get_price_data()
    data = data.iloc[200:].copy()
    data['MA50'] = data['Close'].rolling(window=50).mean()
    data['MA200'] = data['Close'].rolling(window=200).mean()

# Streamlit app
st.set_page_config(page_title="Trading Strategy Dashboard", layout="wide")

pages = ["Price Chart", "Trade Statistics", "Detailed Trades"]
page = st.sidebar.radio("Select Page", pages)

if page == "Price Chart":
    st.title("Price Chart with Moving Averages and Trades")
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=data.index, y=data['Close'], mode='lines', name='Close Price'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA50'], mode='lines', name='MA50'))
    fig.add_trace(go.Scatter(x=data.index, y=data['MA200'], mode='lines', name='MA200'))
    # Buy/Sell points
    if positions is not None and not positions.empty:
        fig.add_trace(go.Scatter(x=positions['BuyDate'], y=positions['BuyPrice'], mode='markers', name='Buy', marker=dict(color='green', size=10, symbol='circle')))
        fig.add_trace(go.Scatter(x=positions['SellDate'], y=positions['SellPrice'], mode='markers', name='Sell', marker=dict(color='red', size=10, symbol='x')))
    fig.update_layout(title="MSFT Price, MA50, MA200, Buy/Sell Points", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig, use_container_width=True)

elif page == "Trade Statistics":
    st.title("Trade Statistics")
    if positions is not None and not positions.empty:
        total_trades = len(positions)
        win_trades = len(positions[positions['ProfitPct'] > 0])
        loss_trades = total_trades - win_trades
        win_rate = win_trades / total_trades * 100 if total_trades > 0 else 0
        avg_profit = positions['ProfitPct'].mean()
        avg_win = positions[positions['ProfitPct'] > 0]['ProfitPct'].mean() if win_trades > 0 else 0
        avg_loss = positions[positions['ProfitPct'] <= 0]['ProfitPct'].mean() if loss_trades > 0 else 0
        avg_holding = positions['HoldingDays'].mean()
        st.metric("Total Trades", total_trades)
        st.metric("Winning Trades", win_trades)
        st.metric("Losing Trades", loss_trades)
        st.metric("Win Rate (%)", f"{win_rate:.2f}")
        st.metric("Average Profit (%)", f"{avg_profit:.2f}")
        st.metric("Average Win (%)", f"{avg_win:.2f}")
        st.metric("Average Loss (%)", f"{avg_loss:.2f}")
        st.metric("Average Holding Days", f"{avg_holding:.2f}")
    else:
        st.info("No trades to display.")

elif page == "Detailed Trades":
    st.title("Detailed Trades Record")
    if positions is not None and not positions.empty:
        st.dataframe(positions)
    else:
        st.info("No trades to display.")

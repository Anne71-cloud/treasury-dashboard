import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from fx_rates import get_fx_rate, get_fx_history, calculate_fx_exposure

st.set_page_config(page_title="Multi-Currency Treasury Dashboard", page_icon="💰", layout="wide")

st.title("💰 Multi-Currency Treasury Dashboard")
st.markdown("**Real-time cash position tracking across currencies and entities**")
st.markdown("---")

st.sidebar.header("Cash Position Input")
base_currency = st.sidebar.selectbox("Base Currency", ["USD", "EUR", "GBP", "ZAR"])

entities = {
    "South Africa HQ": {"currency": "ZAR", "amount": 5000000},
    "DRC Operations": {"currency": "USD", "amount": 250000},
    "European Office": {"currency": "EUR", "amount": 100000},
    "UK Branch": {"currency": "GBP", "amount": 75000}
}

st.sidebar.subheader("Entity Cash Positions")
for entity, details in entities.items():
    entities[entity]["amount"] = st.sidebar.number_input(
        f"{entity} ({details['currency']})", value=details["amount"], step=10000
    )

st.sidebar.markdown("---")
st.sidebar.subheader("📊 Current FX Rates")
currencies = ["ZAR", "USD", "EUR", "GBP"]
for curr in currencies:
    if curr != base_currency:
        rate = get_fx_rate(curr, base_currency)
        st.sidebar.metric(f"{curr}/{base_currency}", f"{rate:.4f}")

col1, col2, col3 = st.columns(3)

currency_totals = {}
for entity, details in entities.items():
    curr = details["currency"]
    amount = details["amount"]
    currency_totals[curr] = currency_totals.get(curr, 0) + amount

total_in_base = 0
converted_positions = {}
for curr, amount in currency_totals.items():
    if curr == base_currency:
        converted_amount = amount
    else:
        rate = get_fx_rate(curr, base_currency)
        converted_amount = amount * rate
    converted_positions[curr] = converted_amount
    total_in_base += converted_amount

with col1:
    st.metric("Total Liquidity", f"{base_currency} {total_in_base:,.0f}")
with col2:
    st.metric("Currencies Tracked", len(currency_totals))
with col3:
    st.metric("Entities", len(entities))

st.markdown("---")

col1, col2 = st.columns(2)

with col1:
    st.subheader("💵 Cash by Currency")
    df_currency = pd.DataFrame({
        'Currency': list(converted_positions.keys()),
        'Amount': list(converted_positions.values())
    })
    fig_pie = px.pie(df_currency, values='Amount', names='Currency', title=f'Cash Distribution ({base_currency})')
    st.plotly_chart(fig_pie, use_container_width=True)

with col2:
    st.subheader("🏢 Cash by Entity")
    entity_names = list(entities.keys())
    entity_amounts = []
    for entity, details in entities.items():
        curr = details["currency"]
        amount = details["amount"]
        if curr == base_currency:
            entity_amounts.append(amount)
        else:
            rate = get_fx_rate(curr, base_currency)
            entity_amounts.append(amount * rate)
    df_entity = pd.DataFrame({'Entity': entity_names, 'Amount': entity_amounts})
    fig_bar = px.bar(df_entity, x='Entity', y='Amount', title=f'Cash by Entity ({base_currency})')
    st.plotly_chart(fig_bar, use_container_width=True)

st.markdown("---")
st.subheader("📈 FX Exposure Analysis")

exposure_data = calculate_fx_exposure(currency_totals, base_currency)
if exposure_data:
    exposure_df = pd.DataFrame(exposure_data).T.reset_index()
    exposure_df.columns = ['Currency', 'Amount', 'FX Rate', f'Exposure ({base_currency})', 'Impact of 5% Move']
    st.dataframe(exposure_df.style.format({
        'Amount': '{:,.0f}',
        'FX Rate': '{:.4f}',
        f'Exposure ({base_currency})': '{:,.0f}',
        'Impact of 5% Move': '{:,.0f}'
    }), use_container_width=True)
    st.info("💡 The 'Impact of 5% Move' shows potential P&L impact if currency moves 5% against base")
else:
    st.info("All cash is in base currency - no FX exposure")

st.markdown("---")
st.subheader("📊 30-Day FX Rate Trends")

selected_currency = st.selectbox("Select currency to view trend", [c for c in currencies if c != base_currency])
if selected_currency:
    history = get_fx_history(selected_currency, base_currency, days=30)
    if not history.empty:
        fig_line = go.Figure()
        fig_line.add_trace(go.Scatter(x=history.index, y=history.values, mode='lines', 
                                      name=f'{selected_currency}/{base_currency}', line=dict(color='#1f77b4', width=2)))
        fig_line.update_layout(title=f'{selected_currency}/{base_currency} - Last 30 Days',
                              xaxis_title='Date', yaxis_title='Exchange Rate', hovermode='x unified')
        st.plotly_chart(fig_line, use_container_width=True)
    else:
        st.warning("Historical data not available")

st.markdown("---")
st.markdown("**Multi-Currency Treasury Dashboard** | Built with Python, Streamlit, and yfinance  \n*Created by Saranne Ndamba* | [LinkedIn](https://linkedin.com/in/sarannendamba) | [Portfolio](https://anne71-cloud.github.io/Saranne-portfolio/)")
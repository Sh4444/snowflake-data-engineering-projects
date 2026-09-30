# Import python packages
import streamlit as st
import pandas as pd
import plotly.express as px
from snowflake.snowpark.context import get_active_session

# ✅ Make layout full width (IMPORTANT)
st.set_page_config(layout="wide")

# Title
st.title("🌍 Passport Ranking Dashboard")

# Get Snowflake session
session = get_active_session()

# Load real data
query = """
SELECT COUNTRY_NAME, RNK, ACCESS_NO_COUNTRY, YRS
FROM SHPROD.PUBLIC.RANK_PASSPORT ORDER BY RNK;

"""

df = session.sql(query).to_pandas()

# ✅ Year filter
year = st.selectbox("Select Year", sorted(df['YRS'].unique()))
df = df[df['YRS'] == year]

# Sort + limit (important for fitting UI)
df = df.sort_values(by='RNK')

# Create 2 columns layout
col1, col2 = st.columns(2)

# 📊 Graph 1: Rank
with col1:
    st.subheader("🏆 Rank by Country")
    fig1 = px.bar(df, x='COUNTRY_NAME', y='RNK')
    fig1.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig1, use_container_width=True)

# 🌍 Graph 2: Access
with col2:
    st.subheader("🌍 Access to Countries")
    fig2 = px.bar(df, x='COUNTRY_NAME', y='ACCESS_NO_COUNTRY')
    fig2.update_layout(xaxis_tickangle=-45)
    st.plotly_chart(fig2, use_container_width=True)

# 📈 Gain calculation
df['GAIN'] = df['ACCESS_NO_COUNTRY'].diff()

st.subheader("📈 Gain in Access")
fig3 = px.line(df, x='COUNTRY_NAME', y='GAIN')
st.plotly_chart(fig3, use_container_width=True)

# 📋 Data table
st.subheader("📋 Data")
st.dataframe(df, use_container_width=True)
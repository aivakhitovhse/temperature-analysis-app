import streamlit as st
import pandas as pd
import plotly.express as px
import time
from api import get_weather, run_async, test_sync_requests, run_async_test
from analysis import add_rolling, seasonal_stats, get_current_season, is_normal


st.title("temperature analysis")
uploaded_file = st.file_uploader("Choose file", type=["csv"])

if uploaded_file is None:
    st.info("csv not found")
    st.stop()

df = pd.read_csv(uploaded_file)
df['timestamp'] = pd.to_datetime(df['timestamp'])
cities = df['city'].unique()
city = st.selectbox("select city", cities)
city_df = df[df['city'] == city]
city_df = add_rolling(city_df)

st.subheader(f'data for {city}')
st.dataframe(city_df.head())
fig = px.line(city_df, x= 'timestamp', y= 'temperature', title=f"temperature in {city}")
fig.add_scatter(x=city_df['timestamp'], y=city_df['rolling_mean'], mode='lines', name='rolling_mean')
anomalies = city_df[city_df['anomaly']]
st.plotly_chart(fig)
st.write(f"number of anomalies: {int(city_df['anomaly'].sum())}")

season_stats = seasonal_stats(df, city)
st.subheader('seasonal statistics')
st.dataframe(season_stats)
fig_season = px.bar(season_stats, x='season', y='mean',error_y='std',title=f"season statistics in {city}")
st.plotly_chart(fig_season)

st.subheader('current weather')

with st.form("api_form"):
    api_key = st.text_input("enter OpenWeather api key", type="password")
    method = st.radio("request method", ["Sync", "Async"])
    submit = st.form_submit_button("get current temperature")

if submit:

    if not api_key:
        st.error("enter api key")
        st.stop()
    start_time = time.time()
    if method == "Sync":
        data = get_weather(city, api_key)
    else:
        data = run_async(city, api_key)
    end_time = time.time()
    total_time = end_time - start_time
    st.write(f"request time: {total_time:.4f} seconds")


    if str(data.get('cod')) == "401":
        st.error(data.get("message", "invalid api key"))
        st.stop()

    current_temp = data['main']['temp']
    st.success(f"current temperature {current_temp}")
    current_season = get_current_season()
    season_row = season_stats[season_stats['season'] == current_season].iloc[0]

    if is_normal(current_temp, season_row):
        st.info("temperature is ok")
    else:
        st.warning('temperature is not ok :(')

# тест для наглядности выигрыша по времени при использованием async
st.subheader('performance test')
if st.button('performance test'):
    sync_time, _ = test_sync_requests(city, api_key)
    async_time, _ = run_async_test(city, api_key)
    st.write(f'sync_time: {sync_time:.4f} seconds')
    st.write(f"async_time: {async_time:.4f} seconds")





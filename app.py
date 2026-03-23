import streamlit as st
import pandas as pd
import plotly.express as px
from api import get_weather, run_async
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
    if not api_key:
        st.info("something went wrong\nenter api key again")
        st.stop()

if submit:
    if st.button("get current temperature"):
        if method == 'sync':
            data = get_weather(city, api_key)
        else:
            data = run_async(city, api_key)

        if data.get('cod') == 401:
            st.error(data.get("message", "invalid api key"))
            st.stop()
        else:
            current_temp = data['main']['temp']
            st.success(f"current temperature {current_temp}")
            month = pd.Timestamp.now().month
            season_map = {12: 'winter', 1 : 'winter', 2 : " winter",
                          3 : 'spring', 4 : 'spring', 5 : "spring",
                          6 : 'summer', 7 : 'summer', 8 : 'summer',
                          9 : 'autumn', 10 : 'autumn', 11 : 'autumn'}
            current_season = season_map[month]
            season_row = season_stats[season_stats['season'] == current_season].iloc[0]
            lower = season_row['mean'] - 2 * season_row['std']
            upper = season_row['mean'] + 2 * season_row['std']

            if lower <= current_temp <= upper:
                st.info("temperature is ok")
            else:
                st.warning('temperature is not ok:<(')





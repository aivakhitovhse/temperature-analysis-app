import pandas as pd

def add_rolling(city_df, window=30):
    city_df = city_df.sort_values('timestamp').copy()
    city_df['rolling_mean'] = city_df['temperature'].rolling(window).mean()
    city_df['rolling_std'] = city_df['temperature'].rolling(window).std()
    city_df['upper'] = city_df['rolling_mean'] + 2 * city_df['rolling_std']
    city_df['lower'] = city_df['rolling_mean'] - 2 * city_df['rolling_std']
    city_df['anomaly'] = ((city_df['temperature'] > city_df['upper']) |(city_df['temperature'] < city_df['lower']))

    return city_df


def seasonal_stats(df, city):
    stats = (df[df['city'] == city].groupby('season')['temperature'].agg(['mean', 'std']).reset_index())
    season_order = ['winter', 'spring', 'summer', 'autumn']
    stats['season'] = pd.Categorical(stats['season'],categories=season_order,ordered=True)

    return stats.sort_values('season')


def get_current_season():
    month = pd.Timestamp.now().month
    season_map = {
        12: 'winter', 1: 'winter', 2: 'winter',
        3: 'spring', 4: 'spring', 5: 'spring',
        6: 'summer', 7: 'summer', 8: 'summer',
        9: 'autumn', 10: 'autumn', 11: 'autumn'
    }

    return season_map[month]


def is_normal(temp, season_row):
    lower = season_row['mean'] - 2 * season_row['std']
    upper = season_row['mean'] + 2 * season_row['std']
    return lower <= temp <= upper
import requests
import aiohttp
import asyncio


def get_weather(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"
    return requests.get(url).json()


async def get_weather_async(city, api_key):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            return await resp.json()


def run_async(city, api_key):
    return asyncio.run(get_weather_async(city, api_key))
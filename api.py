import requests
import aiohttp
import asyncio
import time


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

def test_sync_requests(city, api_key, n=5):
    start = time.time()
    results = []
    for _ in range(n):
        data = get_weather(city, api_key)
        results.append(data)

    end = time.time()
    return end - start, results

async def test_async_requests(city, api_key, n=5):
    url = f"https://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric"

    async with aiohttp.ClientSession() as session:

        tasks = [session.get(url) for _ in range(n)]
        start = time.time()
        responses = await asyncio.gather(*tasks)
        results = []

        for resp in responses:
            results.append(await resp.json())

        end = time.time()

    return end - start, results

def run_async_test(city, api_key, n=5):
    return asyncio.run(test_async_requests(city, api_key, n))

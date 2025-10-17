import httpx
import asyncio

# URL do endpoint que será atacado
url = "http://127.0.0.1:8000/ping"

# Número de requisições que serão enviadas
request_count = 1000


async def send_request():
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(url)
            print(f"Status: {response.status_code}")
        except httpx.RequestError as exc:
            print(f"Erro ao conectar: {exc}")


async def dos_attack():
    tasks = [send_request() for _ in range(request_count)]
    await asyncio.gather(*tasks)



asyncio.run(dos_attack())

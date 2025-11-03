from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()
tuta

# Modelo de dados para o endpoint POST
class Item(BaseModel):
    name: str
    description: str = None


# Endpoint "ping" para verificar a conexão
@app.get("/ping")
async def ping():
    return {"message": "Server is up and running!"}


# Endpoint para receber dados
@app.post("/data")
async def receive_data(item: Item):
    return {"message": f"Received data for {item.name}", "description": item.description}


# Endpoint para status do servidor
@app.get("/status")
async def status():
    return {"status": "Server is operational"}

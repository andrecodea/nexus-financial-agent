# ====== Importações ======
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from app.agent import NexusAgent
from dotenv import load_dotenv

# ====== Carrega as variáveis de ambiente ======
load_dotenv()

# ====== Cria as regras de formatação JSON ======
class ChatRequest(BaseModel):
    message:str = ""

class ChatResponse(BaseModel):
    response:str = ""

# ====== Aplicação ======
app = FastAPI(title="NEXUS Financial API")

try:
    nexus_agent = NexusAgent()
    print("NEXUS Agent initialized successfully")
except Exception as e:
    print(f"Failed to initialize Agent: {e}")
    nexus_agent = None

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request:ChatRequest):
    if not nexus_agent:
        raise HTTPException(status_code=500, detal="Agent not initialized")

    response_text = nexus_agent.chat(request.message)
    return ChatResponse(response=response_text)


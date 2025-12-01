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

# Inicializa a aplicação
app = FastAPI(title="NEXUS Financial API")

# Tenta inicializar o agente
try:
    nexus_agent = NexusAgent()
    print("NEXUS Agent initialized successfully")
except Exception as e:
    print(f"Failed to initialize Agent: {e}")
    nexus_agent = None

# Configura o path "/chat" para geração de respostas
@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(request:ChatRequest):
    """
    Generates an address '/chat' for POST requests so that chat
    responses can be sent through it.
    :param request:
    :return chat response as JSON object:
    """
    if not nexus_agent:
        raise HTTPException(status_code=500, detail="Agent not initialized")

    response_text = nexus_agent.chat(request.message)
    return ChatResponse(response=response_text)


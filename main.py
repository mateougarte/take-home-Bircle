import asyncio

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


conversation_history: dict[str, list[dict[str, str]]] = {}

SYSTEM_PROMPT = (
    "Eres un asistente virtual de una tienda de electrónica. Ayudas a los "
    "clientes con consultas sobre productos, precios, disponibilidad, "
    "garantías y soporte técnico de forma clara y amable."
)


async def mock_llm_call(history: list) -> str:
    await asyncio.sleep(1)
    last_message = history[-1]["content"] if history else ""
    return (
        f"Recibí tu mensaje: '{last_message}'. Soy el asistente de la "
        "tienda, ¿en qué más puedo ayudarte con nuestros productos?"
    )


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Mensaje recibido del usuario {request.user_id}")

    if request.user_id not in conversation_history:
        conversation_history[request.user_id] = [
            {"role": "system", "content": SYSTEM_PROMPT}
        ]

    conversation_history[request.user_id].append(
        {"role": "user", "content": request.message}
    )

    try:
        assistant_response = await mock_llm_call(conversation_history[request.user_id])
    except Exception as e:
        logger.error(f"Error al llamar al LLM para el usuario {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el mensaje")

    conversation_history[request.user_id].append(
        {"role": "assistant", "content": assistant_response}
    )

    logger.success(f"Respuesta generada exitosamente para el usuario {request.user_id}")

    return ChatResponse(response=assistant_response)

from dotenv import load_dotenv

load_dotenv()

import anthropic
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from loguru import logger

app = FastAPI()

client = anthropic.AsyncAnthropic()


class ChatRequest(BaseModel):
    user_id: str
    message: str


class ChatResponse(BaseModel):
    response: str


conversation_history: dict[str, list[dict[str, str]]] = {}

SYSTEM_PROMPT = (
    "Sos un asistente de atención al cliente para la tienda 'Bircle Outdoors'. "
    "Tu tono es amable, profesional y conciso. "
    "Solo respondés preguntas sobre indumentaria y equipamiento outdoors, y productos de la tienda. "
    "Mantené las respuestas cortas (menos de 3 frases)."
)


@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    logger.info(f"Mensaje recibido del usuario {request.user_id}")

    if request.user_id not in conversation_history:
        conversation_history[request.user_id] = []

    conversation_history[request.user_id].append(
        {"role": "user", "content": request.message}
    )

    try:
        response = await client.messages.create(
            model="claude-opus-4-7",
            max_tokens=256,
            system=SYSTEM_PROMPT,
            messages=conversation_history[request.user_id],
        )
        assistant_response = response.content[0].text
    except Exception as e:
        logger.error(f"Error al llamar a la API para el usuario {request.user_id}: {e}")
        raise HTTPException(status_code=500, detail="Error interno al procesar el mensaje")

    conversation_history[request.user_id].append(
        {"role": "assistant", "content": assistant_response}
    )

    logger.success(f"Respuesta generada exitosamente para el usuario {request.user_id}")

    return ChatResponse(response=assistant_response)

# Chatbot Bircle Outdoors

Asistente virtual para la tienda **Bircle Outdoors** compuesto por dos servicios:

- **Backend**: API REST construida con FastAPI que mantiene el historial de conversación por usuario y llama al modelo `claude-opus-4-7` de Anthropic.
- **Frontend**: Interfaz de chat construida con Streamlit que se comunica con el backend vía HTTP.

## Requisitos

- Python 3.10+
- API key de Anthropic

## Instalación

### 1. Crear y activar el entorno virtual

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1   # Windows PowerShell
# source venv/bin/activate    # Linux/macOS
```

### 2. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 3. Configurar la API key

Crear un archivo `.env` en la raíz del proyecto:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Ejecución

Los dos servicios deben correr en paralelo, cada uno en su propia terminal.

**Terminal 1 — Backend (FastAPI):**

```bash
uvicorn main:app --reload
```

Queda disponible en `http://127.0.0.1:8000`. La documentación interactiva (Swagger UI) está en `http://127.0.0.1:8000/docs`.

**Terminal 2 — Frontend (Streamlit):**

```bash
streamlit run app.py
```

Queda disponible en `http://localhost:8501`.

## Uso del endpoint directamente

```bash
curl -X POST "http://127.0.0.1:8000/chat" \
  -H "Content-Type: application/json" \
  -d "{\"user_id\": \"cliente_1\", \"message\": \"¿Tienen camperas para lluvia?\"}"
```

## Arquitectura

```
[Streamlit frontend]  →  POST /chat  →  [FastAPI backend]  →  [Anthropic API]
     app.py                                  main.py              claude-opus-4-7
```

## Decisiones técnicas

### Integración con la API de Anthropic

El backend usa el SDK oficial `anthropic` con un cliente asíncrono (`AsyncAnthropic`), lo que es compatible con el servidor ASGI de FastAPI sin bloquear el event loop. La API key se carga desde `.env` con `python-dotenv` para no hardcodearla en el código.

El `system prompt` se pasa como parámetro independiente en cada llamada a la API (en lugar de insertarlo como primer mensaje del historial). Esto es la forma correcta de usar el parámetro `system` del SDK de Anthropic, y mantiene el historial de mensajes limpio, con solo turnos `user` / `assistant`.

### Historial en memoria (`conversation_history`)

El contexto de cada conversación se guarda en un diccionario global (`user_id` → lista de mensajes). Es la solución más simple para mantener el estado por usuario sin depender de infraestructura externa. La limitación principal es que el historial se pierde al reiniciar el proceso y no escala a múltiples instancias; para producción se recomendaría reemplazarlo por un almacenamiento persistente compartido entre instancias.

### Frontend con Streamlit

El historial de mensajes del frontend se guarda en `st.session_state` para que persista entre re-renders sin necesidad de consultar el estado al backend. El frontend y el backend mantienen sus propios historiales de forma independiente: el backend acumula el contexto real de la conversación para enviárselo al modelo, y el frontend solo persiste lo necesario para mostrar la UI correctamente.

### Observabilidad con Loguru

Se utiliza `loguru` en lugar del módulo `logging` estándar por su configuración más simple y salida más legible. En el endpoint `/chat` se registran tres momentos clave del flujo:

- `logger.info`: cuando se recibe un mensaje, indicando el `user_id`.
- `logger.error`: si la llamada a la API falla, antes de propagar el error como `HTTPException` 500.
- `logger.success`: cuando la respuesta se generó y devolvió correctamente.

## Proceso de desarrollo

1. Configuré el entorno virtual y las dependencias iniciales (FastAPI, uvicorn, pydantic, loguru).
2. Conecté el entorno virtual a Claude Code y armé el repositorio inicial en GitHub.
3. Armé y refiné el plan de desarrollo, tomando la decisión de hacer un primer MVP mockeando la respuesta del LLM para validar el flujo completo de la API antes de integrar un proveedor real.
4. Implementé el endpoint `/chat` con FastAPI: validación de datos con Pydantic, historial en memoria, manejo de errores y logging con Loguru.
5. Probé el servidor local enviando peticiones POST desde otra terminal. Verifiqué logs y respuesta 200.
6. Integré el SDK de Anthropic reemplazando el mock por llamadas reales a `claude-opus-4-7`, cargando la API key desde `.env` y actualizando el system prompt para Bircle Outdoors.
7. Desarrollé el frontend con Streamlit usando `st.chat_input` y `st.chat_message`, con manejo de errores de conexión al backend.
8. Actualicé el README para reflejar la arquitectura completa y las nuevas instrucciones de ejecución.

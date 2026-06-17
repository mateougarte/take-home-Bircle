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

Los dos servicios deben correr en paralelo, cada uno en su propia terminal. A futuro se podrían levantar juntos con un docker-compose up

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
1. Configuré el entorno virtual y descargué las dependencias que iba a usar (pip, fastapi, uvicorn, pydantic).
2. Conecté el entorno virtual a Claude Code, y armé el repositorio inicial de Github.
3. Armé y refiné el plan de desarrollo, tomando la decisión de hacer un primer MVP mockeando la respuesta del LLM para validar el flujo completo de la API antes de integrar un proveedor real. También decidí agregar logs más visibles usando loguru
4. Le pasé el prompt a Claude: " Crea un archivo llamado main.py. Necesito que construyas una API con FastAPI con las siguientes características:
   Importa FastAPI, HTTPException y BaseModel de Pydantic. Importa logger de loguru.
   Define un modelo Pydantic ChatRequest con user_id (str) y message (str).
   Define un modelo ChatResponse con response (str).
   Crea un diccionario global en memoria llamado conversation_history.
   Crea una función asíncrona mock_llm_call(history: list) -> str que simule un retraso con asyncio.sleep(1) y devuelva una respuesta genérica basada en el último mensaje.
   Crea el endpoint POST /chat. Este endpoint debe:
    - Registrar con loguru (logger.info) que se recibió un mensaje indicando el user_id.
    - Si el user_id no está en el historial, inicializar su lista con un System Prompt de un asistente de una tienda de electrónica.
    - Añadir el mensaje del usuario al historial.
    - Llamar a mock_llm_call dentro de un bloque try/except. Si falla, registrar el error con logger.error y lanzar un HTTPException 500.
    - Añadir la respuesta del asistente al historial.
    - Devolver el ChatResponse y registrar con loguru el éxito de la operación."
5.Fui verificando el avance de Claude, y que me hiciera sentido lo que estaba haciendo en base al plan que había definido. 
6. Probé y ejecuté el servidor local, y desde otra terminal le envié la petición post. Verifiqué que aparecían los logs, y que devolvía un 200 con mensaje genérico de atención. 
7. Generé con IA el readme inicial, describiendo el servicio, las instrucciones para iniciarlo, y explicando las decisiones técnicas tomadas.
8. Hice commit y push de lo generado, y luego adapté el readme para mejorar algunas explicaciones y justificaciones de decisiones.
9. Investigué con Gemini la mejor opción para encarar una solución usando llm. Entiendo que para escalar esto, lo más conveniente sería tener un agente orquestador que a su vez derive las consultas a otro agente especializado en atención al cliente. Para esta ocasión consideré suficiente resolverlo con un único agente con un system prompt bien estructurado. Para no gastar mucho elegí el modelo haiku de claude, teniendo en cuenta que no debería necesitar mucho procesamiento más que una atención al cliente
10. Integré el SDK de Anthropic reemplazando el mock por llamadas reales a `claude-opus-4-7`, cargando la API key desde `.env` y actualizando el system prompt para Bircle Outdoors.
7. Desarrollé el frontend con Streamlit usando `st.chat_input` y `st.chat_message`, con manejo de errores de conexión al backend.
8. Actualicé el README para reflejar la arquitectura completa y las nuevas instrucciones de ejecución. Probé, y realicé el push.

## Mejoras futuras
- Usar un orquestador de agente, que derive al agente especializado en atención al cliente.
- docker compose-up para levantarlo.

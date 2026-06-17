# Chatbot Bircle

API construida con **FastAPI** que simula un asistente virtual para una tienda de electrónica. El servicio expone un endpoint de chat que mantiene el contexto de la conversación por usuario y responde a sus mensajes.

## Requisitos

- Python 3.10+
- pip

## Instalación y ejecución

### 1. Crear el entorno virtual

```bash
python -m venv venv
```

### 2. Activar el entorno virtual

En Windows (PowerShell):

```powershell
.\venv\Scripts\Activate.ps1
```

En Linux/macOS:

```bash
source venv/bin/activate
```

### 3. Instalar las dependencias

```bash
pip install -r requirements.txt
```

### 4. Iniciar el servidor

```bash
uvicorn main:app --reload
```

El servidor quedará disponible en `http://127.0.0.1:8000`. La documentación interactiva (Swagger UI) está en `http://127.0.0.1:8000/docs`.

### Uso del endpoint

```bash
curl -X POST "http://127.0.0.1:8000/chat" -H "Content-Type: application/json" -d "{\"user_id\": \"cliente_123\", \"message\": \"¿Tienen teclados mecánicos?\"}"
```

## Decisiones técnicas

### Historial en memoria (`conversation_history`)

El contexto de cada conversación se guarda en un diccionario global (`user_id` → lista de mensajes). Es la solución más simple para mantener el estado por usuario sin depender de infraestructura externa (base de datos, caché, etc.). La limitación principal es que el historial se pierde al reiniciar el proceso y no escala a múltiples instancias del servicio; para producción se recomendaría reemplazarlo por un almacenamiento persistente (base de datos) compartido entre instancias.

### Simulación del LLM (`mock_llm_call`)

En lugar de integrar un proveedor de LLM real, se implementó una función asíncrona que simula la latencia de una llamada a un modelo (`asyncio.sleep(1)`) y devuelve una respuesta genérica basada en el último mensaje del usuario. Esto permite desarrollar y probar el flujo completo de la API (validación de datos, manejo de historial, manejo de errores, logging) sin incurrir en costos ni depender de credenciales de un servicio externo. La función está aislada para poder sustituirse fácilmente por una llamada real a un LLM sin modificar el resto del endpoint.

### Observabilidad con Loguru

Se utiliza `loguru` en lugar del módulo `logging` estándar por su configuración más simple y su salida más legible por defecto. En el endpoint `/chat` se registran tres momentos clave del flujo:

- `logger.info`: cuando se recibe un mensaje, indicando el `user_id`.
- `logger.error`: si la llamada al LLM (mock) falla, antes de propagar el error como `HTTPException` 500.
- `logger.success`: cuando la respuesta se generó y devolvió correctamente.

Esto permite trazar el ciclo de vida de cada solicitud y detectar rápidamente fallos en la generación de respuestas.

## Proceso de desarrollo.
1. Configuré el entorno virtual y descargué las dependencias que iba a usar (pip, fastapi, uvicorn, pydantic).
2. Conecté el entorno virtual a Claude Code, y armé el repositorio inicial de Github.
3. Armé y refiné el plan de desarrollo para darle un buen prompt inicial a Claude. Aquí tomé la decisión de hacer un primer mvp mockeando la respuesta, y agregar logs más visibles. 
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

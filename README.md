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

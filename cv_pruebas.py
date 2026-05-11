import os
import json
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv
from google import genai
from google.genai import types

# 1. Cargar el .env y configurar el cliente
load_dotenv()
api_key = os.environ.get("GEMINI_API_KEY")
client = genai.Client(api_key=api_key)

# 2. Inicializar la aplicación FastAPI
app = FastAPI(
    title="API Generador de CVs", 
    description="Servicio para optimizar texto desorganizado y convertirlo en un CV estructurado"
)

# 3. Configurar CORS para permitir peticiones desde el frontend (index.html)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # En producción se cambiaría "*" por el dominio real
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 4. Definir el esquema de datos que el usuario enviará
class DatosUsuario(BaseModel):
    texto_desorganizado: str

# 5. Función principal para llamar a Gemini
def generar_cv_optimizado(informacion_desorganizada: str) -> dict:
    instrucciones_sistema = """Eres un experto en Selección de Talento Humano y optimización de CVs para filtros ATS. Tu objetivo es recibir información desorganizada de un usuario y transformarla en un currículum profesional, persuasivo y estructurado.
    
    Reglas de oro:
    - Cuantifica logros: Transforma tareas simples en logros con datos (ej. en lugar de 'Vendí productos', usa 'Incrementé las ventas en un 15% anual').
    - Palabras Clave: Usa términos técnicos relevantes para la industria del usuario.
    - Brevedad: Redacta viñetas (bullet points) cortas y potentes usando verbos de acción (Lideré, Desarrollé, Optimicé).
    - Estructura: Devuelve la información exclusivamente en formato JSON con las siguientes llaves: perfil_profesional, experiencia_laboral (lista de objetos), educacion, habilidades_tecnicas y habilidades_blandas.
    
    No añadas introducciones ni despedidas, solo el objeto JSON final."""

    response = client.models.generate_content(
        model='gemini-2.5-flash',
        contents=informacion_desorganizada,
        config=types.GenerateContentConfig(
            system_instruction=instrucciones_sistema,
            response_mime_type="application/json",
        )
    )
    return json.loads(response.text)

# 6. El Endpoint HTTP POST
@app.post("/api/generar-cv")
async def endpoint_generar_cv(datos: DatosUsuario):
    try:
        cv_json = generar_cv_optimizado(datos.texto_desorganizado)
        print("\n✅ JSON RECIBIDO DE GEMINI:\n", cv_json, "\n")
        return cv_json
    except Exception as e:
        print(f"\n❌ ERROR EXACTO DE GEMINI: {str(e)}\n")
        raise HTTPException(status_code=500, detail=f"Error procesando el CV: {str(e)}")
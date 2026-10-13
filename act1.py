import json
import time
from google import genai
from google.genai import types
from google.genai.errors import ServerError

client = genai.Client(api_key="AQ.Ab8RN6JEuwUwkgRvD004E63T9OPhMz_lgXH0lcII6rapuTfnWw")

def generar_json(prompt: str):
    # Subimos a 10 intentos con 5 segundos de espera
    for intento in range(10):
        try:
            print(f"Intento {intento + 1}: Conectando...")
            response = client.models.generate_content(
                model="gemini-3.8-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json"
                )
            )
            return json.loads(response.text)

        except ServerError:
            print("Servidor de Google lleno (503). Reintentando en 5s...")
            time.sleep(5)
        except Exception as e:
            print(f"Error: {e}")
            return None

prompt_tarea = "Dame la ficha técnica de una laptop gamer ficticia en JSON con llaves: 'marca', 'modelo', 'precio_usd', y 'specs' (lista de specs)."

print("Solicitando datos a Gemini...")
producto = generar_json(prompt_tarea)

if producto:
    print("\n¡Datos recibidos correctamente!\n")
    print(producto)
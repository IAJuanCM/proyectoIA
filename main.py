"""
Imagina que esta API es una biblioteca de información agrícola:
La función load_agriculture() es como bibliotecario que carga el catálogo de libros (agrícola) cuando se abre la biblioteca.
La función get_agriculture() muestra todo el catálogo cuando alguien lo pide.
La función get_agricultural(id) es como si alguien preguntara por un libro específico por su código de identificación.
La función chatbot(query) es un asistente que busca libros según palabras clave y sinónimos.
La función get_agriculture_by_category(category) ayuda a encontrar libros según su categoría.
"""

# Importamos las herramientas necesarias para construir nuestra API
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

# Asegurar que los datos NLTK están descargados
nltk.download('punkt')  # Paquete para dividir frases en palabras.
nltk.download('wordnet')  # Paquete para encontrar sinónimos de palabras en inglés.

# Indicamos la ruta donde NLTK buscará los datos descargados en nuestro computador
nltk.data.path.append(r'C:\Users\VanessaGR\AppData\Roaming\nltk_data')

# Función para cargar la información agrícola desde archivos CSV
def load_agriculture():
    try:
        df1 = pd.read_csv("Dataset/farmer_advisor_dataset.csv")[['Sustainable_id', 'title', 'release_year', 'listed_in', 'description']]
        df2 = pd.read_csv("Dataset/market_researcher_dataset.csv")[['Sustainable_id', 'title', 'release_year', 'listed_in', 'description']]
        df = pd.concat([df1, df2], ignore_index=True)
        df.columns = ['id', 'title', 'year', 'category', 'overview']
        return df.fillna('').to_dict(orient='records')
    except Exception as e:
        raise RuntimeError(f"Error cargando los datasets: {e}")

# Cargamos la información al iniciar la API
agricola_list = load_agriculture()

# Función para obtener sinónimos de una palabra
def get_synonyms(word): 
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Inicializamos la aplicación FastAPI
app = FastAPI(title="Mi biblioteca de información agrícola", version="1.0.0")

# Ruta de inicio
@app.get("/", tags=["Home"])
def home():
    return HTMLResponse('<h1>Bienvenido a la API de agricultura colombiana</h1>')

# Ruta para mostrar todo el catálogo agrícola
@app.get("/agriculture", tags=["Agriculture"])
def get_agriculture():
    return JSONResponse(content=agricola_list)

# Ruta para obtener un documento por su ID
@app.get("/agriculture/{item_id}", tags=["Agriculture"])
def get_agricultural(item_id: str):
    for item in agricola_list:
        if item['id'] == item_id:
            return JSONResponse(content=item)
    raise HTTPException(status_code=404, detail="Documento no encontrado")

# Ruta tipo chatbot que busca documentos por palabras clave y sinónimos
@app.get("/chatbot", tags=["Chatbot"])
def chatbot(query: str):
    query_words = word_tokenize(query.lower())
    synonyms = set(query_words)
    for word in query_words:
        synonyms.update(get_synonyms(word))

    results = []
    for item in agricola_list:
        text = f"{item['title']} {item['category']} {item['overview']}".lower()
        if any(word in text for word in synonyms):
            results.append(item)

    if results:
        return JSONResponse(content=results)
    raise HTTPException(status_code=404, detail="No se encontraron coincidencias")

# Ruta para buscar documentos por categoría
@app.get("/agriculture/category/{category}", tags=["Agriculture"])
def get_agriculture_by_category(category: str):
    results = [item for item in agricola_list if category.lower() in item['category'].lower()]
    if results:
        return JSONResponse(content=results)
    raise HTTPException(status_code=404, detail="Categoría no encontrada")








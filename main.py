
"""
Imagina que esta API es una biblioteca de información agrícola:
La función load_agriculture() es como bibliotecario que carga el catalogo de libros (agrícola) cuando se abre la  biblioteca.
La función get_agriculture() muestra todo el catalogo cuando alguien lo pide.
La función get_agricultural(id) es como si alguien preguntara por un libro específico por su codigo de identificación.
La función chatbot (query) es un asistente que busca libros según palabras clave y sinónimo.
La función get_agriculture_by_category (cagory) ayuda a encontrar libros según su género (agricultura intensiva, agricultura extensiva, agricultura ecológica etc.).
"""


# API corregida y funcional con datasets reales
from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse, JSONResponse
import pandas as pd
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import wordnet

# Descargar recursos necesarios de NLTK
nltk.download('punkt')
nltk.download('wordnet')

# Cargar y unir los datos
def load_agriculture():
    try:
        # Dataset 1: Farmers
        df1 = pd.read_csv("Dataset/farmer_advisor_dataset.csv")
        df1 = df1[['Farm_ID', 'Crop_Type', 'Crop_Yield_ton', 'Sustainability_Score']]
        df1['title'] = 'Farmer Data'
        df1['overview'] = 'Yield: ' + df1['Crop_Yield_ton'].astype(str) + ", Sustainability: " + df1['Sustainability_Score'].astype(str)
        df1 = df1.rename(columns={
            'Farm_ID': 'id',
            'Crop_Type': 'category'
        })
        df1 = df1[['id', 'title', 'category', 'overview']]

        # Dataset 2: Market
        df2 = pd.read_csv("Dataset/market_researcher_dataset.csv")
        df2 = df2[['Market_ID', 'Product', 'Market_Price_per_ton', 'Economic_Indicator']]
        df2['title'] = 'Market Data'
        df2['overview'] = 'Price: ' + df2['Market_Price_per_ton'].astype(str) + ", Economic Indicator: " + df2['Economic_Indicator'].astype(str)
        df2 = df2.rename(columns={
            'Market_ID': 'id',
            'Product': 'category'
        })
        df2 = df2[['id', 'title', 'category', 'overview']]

        df = pd.concat([df1, df2], ignore_index=True)
        return df.fillna('').to_dict(orient='records')
    except Exception as e:
        raise RuntimeError(f"Error cargando los datasets: {e}")

# Cargar datos al iniciar
agricola_list = load_agriculture()

# Función para obtener sinónimos
def get_synonyms(word):
    return {lemma.name().lower() for syn in wordnet.synsets(word) for lemma in syn.lemmas()}

# Inicializar API
app = FastAPI(title="Biblioteca de Información Agrícola", version="1.0.0")

@app.get("/", tags=["Home"])
def home():
    return HTMLResponse('<h1>Bienvenido a la API de agricultura colombiana</h1>')

@app.get("/agriculture", tags=["Agriculture"])
def get_agriculture():
    return JSONResponse(content=agricola_list)

@app.get("/agriculture/{item_id}", tags=["Agriculture"])
def get_agricultural(item_id: str):
    for item in agricola_list:
        if str(item['id']) == item_id:
            return JSONResponse(content=item)
    raise HTTPException(status_code=404, detail="Documento no encontrado")

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

@app.get("/agriculture/category/{category}", tags=["Agriculture"])
def get_agriculture_by_category(category: str):
    results = [item for item in agricola_list if category.lower() in item['category'].lower()]
    if results:
        return JSONResponse(content=results)
    raise HTTPException(status_code=404, detail="Categoría no encontrada")







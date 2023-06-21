import streamlit as st
import openai
import os
from ebooklib import epub
import base64
import requests

st.title("gpt-author")

st.markdown("Por Matt Shumer ([https://twitter.com/mattshumer_](https://twitter.com/mattshumer_))")
st.markdown("Repositorio en GitHub: [https://github.com/mshumer/gpt-author](https://github.com/mshumer/gpt-author)")
st.markdown("Genera una novela completa en minutos y la empaqueta automáticamente como un libro electrónico.")

st.markdown("Para generar un libro:")
st.markdown("1. En la primera celda, añade tus claves de OpenAI y Stability (consulta la primera celda para obtenerlas).")
st.markdown("2. Completa la descripción inicial, el número de capítulos y el estilo de escritura en la última celda.")
st.markdown("3. ¡Ejecuta todas las celdas! Después de un tiempo, debería aparecer el archivo EPUB en el sistema de archivos.")

st.markdown("---")

st.markdown("# Configuración")
st.code("""
!pip install openai
!pip install EbookLib

import openai
import os
from ebooklib import epub
import base64
import requests

openai.api_key = "INGRESA TU CLAVE DE OPENAI AQUÍ" # obtén la clave en https://platform.openai.com/
stability_api_key = "INGRESA TU CLAVE DE STABILITY AQUÍ" # obtén la clave en https://beta.dreamstudio.ai/
""")

st.markdown("# Funciones")
st.code("""
def generar_prompt_portada(argumento):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo-16k",
        messages=[
            {"role": "system", "content": "Eres un asistente creativo que escribe una especificación para la portada de un libro, basada en la trama del libro."},
            {"role": "user", "content": f"Trama: {argumento}\n\n--\n\nDescribe la portada que deberíamos crear, basada en la trama. Esto debe tener como máximo dos frases."}
        ]
    )
    return response['choices'][0]['message']['content']

def crear_imagen_portada(argumento):
    argumento = str(generar_prompt_portada(argumento))
    engine_id = "stable-diffusion-xl-beta-v2-2-2"
    api_host = os.getenv('API_HOST', 'https://api.stability.ai')
    api_key = stability_api_key

    if api_key is None:
        raise Exception("Falta la clave de la API de Stability.")

    response = requests.post(
        f"{api_host}/v1/generation/{engine_id}/text-to-image",
        headers={
            "Content-Type": "application/json",
            "Accept": "application/json",
            "Authorization": f"Bearer {api_key}"
        },
        json={
            "text_prompts": [
                {
                    "text": argumento
                }
            ],
            "cfg_scale": 7,
            "clip_guidance_preset": "FAST_BLUE",
            "height": 768,
            "width": 512,
            "samples": 1,
            "steps": 30,
        },
    )

    if response.status_code != 200:
        raise Exception("Respuesta no válida: " + str(response.text))

    data = response.json()
    imagen_base64 = data['image']
    return imagen_base64

def generar_trama(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-4.0-turbo",
        messages=[
            {"role": "system", "content": "Tú eres un asistente creativo que ayuda a escribir novelas. Tienes que generar una trama para una novela basada en la siguiente descripción:"},
            {"role": "user", "content": f"{prompt}\n\n--\n\nGenera una trama interesante para esta novela."}
        ]
    )
    return response['choices'][0]['message']['content']

def seleccionar_trama_mas_apasionante(tramas):
    scores = []
    for trama in tramas:
        response = openai.Completion.create(
            engine="davinci",
            prompt=f"Este libro es una novela {trama}.",
            temperature=0.3,
            max_tokens=10,
            n = 10,
            stop=None,
            log_level="info"
        )
        scores.append((trama, response['choices'][0]['logprobs']['token_logprobs'][0][0]))
    scores.sort(key=lambda x: x[1], reverse=True)
    return scores[0][0]

def mejorar_trama(trama):
    response = openai.ChatCompletion.create(
        model="gpt-4.0-turbo",
        messages=[
            {"role": "system", "content": "Tú eres un asistente creativo que ayuda a escribir novelas. Tienes que mejorar la siguiente trama:"},
            {"role": "user", "content": f"{trama}\n\n--\n\nMejora esta trama para hacerla más interesante."}
        ]
    )
    return response['choices'][0]['message']['content']

def obtener_titulo(trama):
    response = openai.Completion.create(
        engine="text-davinci-003",
        prompt=f"La trama de esta novela es: {trama}.",
        temperature=0.3,
        max_tokens=5,
        n = 5,
        stop=None,
        log_level="info"
    )
    return response['choices'][0]['text']

def escribir_primer_capitulo(trama, titulo, estilo_escritura):
    prompt = f"Trama: {trama}\n\nTítulo: {titulo}\n\nEstilo de escritura: {estilo_escritura}\n\nEmpieza a escribir el primer capítulo de la novela:"

    response = openai.Completion.create(
        model="gpt-4.0-turbo",
        messages=[
            {"role": "system", "content": "Tú eres un asistente creativo que ayuda a escribir novelas. Tienes que escribir el primer capítulo de una novela basada en la siguiente información:"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        n = 1,
        stop=None,
        log_level="info"
    )

    return response['choices'][0]['message']['content']

def escribir_capitulo(trama, titulo, estilo_escritura, numero_capitulo):
    prompt = f"Trama: {trama}\n\nTítulo: {titulo}\n\nEstilo de escritura: {estilo_escritura}\n\nEmpieza a escribir el capítulo {numero_capitulo} de la novela:"

    response = openai.Completion.create(
        model="gpt-4.0-turbo",
        messages=[
            {"role": "system", "content": "Tú eres un asistente creativo que ayuda a escribir novelas. Tienes que escribir el siguiente capítulo de una novela basada en la siguiente información:"},
            {"role": "user", "content": prompt}
        ],
        max_tokens=4096,
        n = 1,
        stop=None,
        log_level="info"
    )

    return response['choices'][0]['message']['content']

def crear_epub(trama, titulo, estilo_escritura, numero_capitulos):
    book = epub.EpubBook()

    # Configurar metadatos
    book.set_identifier("gpt-author")
    book.set_title(titulo)
    book.set_language("es")

    # Crear la portada
    portada_imagen_base64 = crear_imagen_portada(trama)
    portada_imagen_base64_bytes = base64.b64decode(portada_imagen_base64)
    with open("portada.png", "wb") as file:
        file.write(portada_imagen_base64_bytes)
    book.set_cover("cover.png", open("portada.png", "rb").read())

    # Crear la página de título
    title_page = epub.EpubHtml(title='Página de título', file_name='title.xhtml', lang='es')
    title_page.content = f'''
    <h1>{titulo}</h1>
    <p>Escrito por: GPT-Author</p>
    <p>Estilo de escritura: {estilo_escritura}</p>
    <p>Trama: {trama}</p>
    '''
    book.add_item(title_page)

    # Generar capítulos
    for i in range(numero_capitulos):
        capitulo = epub.EpubHtml(title=f'Capítulo {i+1}', file_name=f'chapter_{i+1}.xhtml', lang='es')
        if i == 0:
            capitulo.content = escribir_primer_capitulo(trama, titulo, estilo_escritura)
        else:
            capitulo.content = escribir_capitulo(trama, titulo, estilo_escritura, i+1)
        book.add_item(capitulo)

    # Configurar tabla de contenidos
    book.toc = (epub.Link('title.xhtml', 'Página de título', 'title'),
                (epub.Section('Capítulos'),
                 tuple(epub.Link(f'chapter_{i+1}.xhtml', f'Capítulo {i+1}')) for i in range(numero_capitulos)))

    # Agregar tabla de contenidos y portada al libro
    book.add_item(epub.EpubNcx())
    book.add_item(epub.EpubNav())

    # Ordenar los ítems y escribir el EPUB
    book.spine = ['nav'] + [title_page] + [epub.EpubHtml(title=f'Capítulo {i+1}', file_name=f'chapter_{i+1}.xhtml', lang='es') for i in range(numero_capitulos)]
    epub.write_epub('output.epub', book)

st.markdown("# Generar Libro")
st.markdown("Completa la siguiente información para generar el libro:")

descripcion_inicial = st.text_area("Descripción Inicial", height=100)
numero_capitulos = st.number_input("Número de Capítulos", min_value=1, max_value=100, value=10, step=1)
estilo_escritura = st.text_input("Estilo de Escritura")

if st.button("Generar Libro"):
    st.markdown("Generando libro...")
    trama = generar_trama(descripcion_inicial)
    trama_mejorada = mejorar_trama(trama)
    titulo = obtener_titulo(trama_mejorada)
    st.markdown("### Título:")
    st.write(titulo)
    st.markdown("### Trama:")
    st.write(trama_mejorada)
    crear_epub(trama_mejorada, titulo, estilo_escritura, numero_capitulos)
    st.markdown("¡El libro ha sido generado! Puedes descargar el archivo EPUB haciendo clic en el enlace a continuación:")
    st.markdown("[Descargar EPUB](output.epub)")

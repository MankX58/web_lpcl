from flask import Flask, render_template, request, redirect, url_for
import os
import random

# Importamos las funciones
from db import init_db, obtener_palabras, crear_juego, obtener_juego, registrar_intento, obtener_intentos, actualizar_estado

app = Flask(__name__)

# Si no existe la BD, la creamos 
if not os.path.exists('ahorcado.db'):
    init_db()

@app.route('/')
def index():
    """
    Página de inicio: botones para iniciar partida o reiniciar juego.
    """
    return render_template('index.html')

@app.route('/reiniciar', methods=['POST'])
def reiniciar():
    """
    Reinicia el juego borrando el archivo SQLite y volviéndolo a crear.
    """
    if os.path.exists('ahorcado.db'):
        os.remove('ahorcado.db')
    init_db()
    return render_template('reiniciado.html')

@app.route('/iniciar', methods=['POST'])
def iniciar():
    """
    Selecciona una palabra al azar, crea un registro en 'juego' y redirige a la ruta /juego/<id_juego>.
    """
    palabras = obtener_palabras()
    if not palabras:
        return "No hay palabras en la BD.", 500

    elegido = random.choice(palabras)
    nuevo_id = crear_juego(elegido['id_palabra'], intentos_max=6)
    return redirect(url_for('juego', id_juego=nuevo_id))

@app.route('/juego/<int:id_juego>', methods=['GET', 'POST'])
def juego(id_juego):
    """
    - GET: muestra la interfaz de juego (guiones, letras disponibles, errores).  
    - POST: procesa la letra enviada (click o teclado), guarda en 'intento', verifica si ganó/perdió.
    """
    juego = obtener_juego(id_juego)
    if not juego:
        return "Juego no encontrado.", 404

    conn = None
    from db import get_conn 
    conn = get_conn()
    fila_pal = conn.execute(
        "SELECT texto FROM palabra WHERE id_palabra = ?;",
        (juego['id_palabra'],)
    ).fetchone()
    conn.close()
    palabra_texto = fila_pal['texto'].upper()

    # Los intentos previos
    intentos = obtener_intentos(id_juego)
    letras_intentadas = { fila['letra'] for fila in intentos }

    # Construir la palabra mostrada
    mostrada = "".join([c if c in letras_intentadas else "_" for c in palabra_texto])

    if request.method == 'POST':
        letra = request.form.get('letra', '').strip().upper()
        # Solo procesar si es A–Z, no repetido 
        if letra.isalpha() and len(letra) == 1 and letra not in letras_intentadas:
            acierto = letra in palabra_texto
            registrar_intento(id_juego, letra, acierto)
            letras_intentadas.add(letra)

         
            if all(c in letras_intentadas for c in palabra_texto):
                actualizar_estado(id_juego, 'GANADO')
                return redirect(url_for('resultado', id_juego=id_juego))

            # Recontar fallos
            intentos = obtener_intentos(id_juego)  # volvemos a leerlos
            fallidos = sum(1 for fila in intentos if fila['acierto'] == 0)
            if fallidos >= juego['intentos_max']:
                actualizar_estado(id_juego, 'PERDIDO')
                return redirect(url_for('resultado', id_juego=id_juego))

            return redirect(url_for('juego', id_juego=id_juego))

    # Si el estado ya cambió redirigimos a resultado
    if juego['estado'] in ('GANADO', 'PERDIDO'):
        return redirect(url_for('resultado', id_juego=id_juego))

    # Recalcular fallidos actuales 
    fallidos_act = sum(1 for fila in intentos if fila['acierto'] == 0)

    # Letras disponibles
    todas_letras = [chr(i) for i in range(ord('A'), ord('Z')+1)]
    disponibles = [l for l in todas_letras if l not in letras_intentadas]

    # Le pasamos al template:
    return render_template(
        'juego.html',
        id_juego=id_juego,
        palabra_mostrada=mostrada,
        disponibles=disponibles,
        fallidos=fallidos_act,
        intentos_max=juego['intentos_max']
    )

@app.route('/resultado/<int:id_juego>')
def resultado(id_juego):
    """
    Muestra pantalla final (ganó o perdió) y la palabra completa.
    """
    juego = obtener_juego(id_juego)
    if not juego:
        return "Juego no encontrado.", 404

    # Obtener la palabra final
    from db import get_conn
    conn = get_conn()
    fila_pal = conn.execute(
        "SELECT texto FROM palabra WHERE id_palabra = ?;",
        (juego['id_palabra'],)
    ).fetchone()
    conn.close()
    palabra_texto = fila_pal['texto'].upper()

    return render_template(
        'resultado.html',
        estado=juego['estado'],
        palabra=palabra_texto
    )

if __name__ == '__main__':
    app.run(debug=True)
from flask import Flask, request, jsonify
from datetime import datetime
import sqlite3

app = Flask(__name__)

# Montos permitidos para recargas
VALID_AMOUNTS = [20, 30, 50, 100, 200]

# Inicializar la base de datos y crear la tabla
def init_db():
    conn = sqlite3.connect('recargas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            fecha_hora TEXT NOT NULL,
            comision REAL NOT NULL,
            estado TEXT NOT NULL,
            mensaje TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Registrar transacción en la base de datos
def registrar_transaccion(numero, cantidad, estado, mensaje, comision=0.0, fecha_hora=None):
    if not fecha_hora:
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    conn = sqlite3.connect('recargas.db')
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO transacciones (numero, cantidad, fecha_hora, comision, estado, mensaje)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (numero, cantidad, fecha_hora, comision, estado, mensaje))
    conn.commit()
    conn.close()

@app.route('/recargar', methods=['POST'])
def realizar_recarga():
    try:
        # Obtener datos del cuerpo de la solicitud
        data = request.json
        
        numero = data.get('numero')
        cantidad = data.get('cantidad')
        
        # Validaciones básicas
        if not numero:
            mensaje = "El número es obligatorio"
            registrar_transaccion(numero, cantidad, "fallo", mensaje)
            return jsonify({"status": "fallo", "mensaje": mensaje}), 400
        
        if not cantidad:
            mensaje = "El monto es obligatorio"
            registrar_transaccion(numero, cantidad, "fallo", mensaje)
            return jsonify({"status": "fallo", "mensaje": mensaje}), 400
        
        if not isinstance(numero, str) or len(numero) != 10 or not numero.isdigit():
            mensaje = "El número debe tener exactamente 10 dígitos"
            registrar_transaccion(numero, cantidad, "fallo", mensaje)
            return jsonify({"status": "fallo", "mensaje": mensaje}), 400

        if cantidad not in VALID_AMOUNTS:
            mensaje = "Monto no permitido"
            registrar_transaccion(numero, cantidad, "fallo", mensaje)
            return jsonify({"status": "fallo", "mensaje": mensaje}), 400

        # Registrar la hora y fecha actuales
        fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Calcular el cobro del 5% para el proveedor
        comision = round(cantidad * 0.05, 2)

        # Guardar en la base de datos
        registrar_transaccion(numero, cantidad, "éxito", "Recarga realizada exitosamente", comision, fecha_hora)

        # Generar la respuesta
        respuesta = {
            "status": "éxito",
            "mensaje": "Recarga realizada exitosamente",
            "detalles": {
                "numero": numero,
                "cantidad": cantidad,
                "fecha_hora": fecha_hora,
                "comision": comision
            }
        }

        return jsonify(respuesta), 200

    except Exception as e:
        mensaje = f"Error interno: {str(e)}"
        registrar_transaccion(None, None, "fallo", mensaje)
        return jsonify({"status": "fallo", "mensaje": mensaje}), 500


if __name__ == '__main__':
    # Inicializar la base de datos al iniciar el programa
    init_db()
    app.run(debug=True)

from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime

app = Flask(__name__)

# Crear la base de datos y la tabla si no existen
def init_db():
    conn = sqlite3.connect('recargas.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS transacciones (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            numero TEXT NOT NULL,
            cantidad INTEGER NOT NULL,
            compania TEXT NOT NULL,
            fecha_hora TEXT NOT NULL,
            estado TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

# Endpoint para realizar recargas
@app.route('/recargar', methods=['POST'])
def recargar():
    try:
        data = request.json
        numero = data.get('numero')
        cantidad = data.get('cantidad')

        # Validaciones
        if not numero or len(numero) != 10:
            return jsonify({"status": "fallo", "mensaje": "Número inválido"}), 400
        if cantidad not in [20, 30, 50, 100, 200]:
            return jsonify({"status": "fallo", "mensaje": "Monto inválido"}), 400

        # Calcular la ganancia del proveedor
        ganancia = cantidad * 0.05
        fecha_hora = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Registrar la transacción en la base de datos
        conn = sqlite3.connect('recargas.db')
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO transacciones (numero, cantidad, compania, fecha_hora, estado)
            VALUES (?, ?, ?, ?, ?)
        ''', (numero, cantidad, 'AT&T', fecha_hora, 'éxito'))
        conn.commit()
        conn.close()

        return jsonify({
            "status": "éxito",
            "mensaje": "Recarga realizada correctamente",
            "numero": numero,
            "cantidad": cantidad,
            "ganancia": ganancia,
            "fecha_hora": fecha_hora
        }), 201

    except Exception as e:
        return jsonify({"status": "fallo", "mensaje": f"Error interno: {str(e)}"}), 500

# Endpoint para consultar saldo
@app.route('/saldo', methods=['POST'])
def consultar_saldo():
    try:
        data = request.json
        numero = data.get('numero')

        if not numero:
            return jsonify({"status": "fallo", "mensaje": "Número obligatorio"}), 400

        # Conectar a la base de datos
        conn = sqlite3.connect('recargas.db')
        cursor = conn.cursor()

        # Consulta para obtener el saldo acumulado
        cursor.execute('''
            SELECT SUM(cantidad) AS saldo
            FROM transacciones
            WHERE numero = ? AND estado = "éxito"
        ''', (numero,))
        resultado = cursor.fetchone()
        conn.close()

        # Determinar el saldo
        saldo = resultado[0] if resultado[0] else 0

        return jsonify({"status": "éxito", "saldo": saldo}), 200

    except Exception as e:
        return jsonify({"status": "fallo", "mensaje": f"Error interno: {str(e)}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

import base64
import requests
from flask import Flask, render_template, request, send_from_directory

app = Flask(__name__)

# --- CONFIGURACIÓN ---
API_KEY = "89ddb0ac27bddda41894606162b551cf9964228fa364dd91f042110c789032de" 

def analizar_url(data_qr):
    if not API_KEY or API_KEY == "API_KEY":
        return "Error de configuración de API."

    # DETECCIÓN DE CONTENIDO NO-URL
    
    # Caso 1: Configuración de Wi-Fi
    if data_qr.upper().startswith("WIFI:"):
        return "ALERTA: CONFIGURACIÓN WI-FI<br><small>Este QR intenta conectar tu dispositivo a una red inalámbrica automáticamente. Podría ser un ataque de interceptación (Man-in-the-Middle).</small>"
    # Caso 2: vCard / Contacto
    if "BEGIN:VCARD" in data_qr.upper():
        return "DETECTADO: CONTACTO (vCard)<br><small>Contiene datos personales. Ten cuidado si el origen es desconocido, podría ser una suplantación de identidad.</small>"
    # Caso 3: Texto plano
    if not data_qr.lower().startswith("http"):
        # Limitar el texto mostrado para que no rompa el diseño
        resumen = (data_qr[:50] + '...') if len(data_qr) > 50 else data_qr
        return f"DETECTADO: TEXTO PLANO<br><small>Contenido: {resumen}<br>Advertencia: No sigas instrucciones que soliciten transferencias o claves.</small>"

    # PROCESAMIENTO DE URL (VIRUSTOTAL)
    url_id = base64.urlsafe_b64encode(data_qr.encode()).decode().strip("=")
    headers = {"x-apikey": API_KEY}
    
    try:
        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        
        if response.status_code == 200:
            attr = response.json()['data']['attributes']
            stats = attr['last_analysis_stats']
            malicious = stats['malicious']
            
            if malicious > 0:
                results = attr['last_analysis_results']
                razon = "Amenaza detectada"
                for engine in results.values():
                    if engine['result'] not in [None, 'clean', 'unrated']:
                        razon = engine['result'].upper()
                        break
                
                return f"BLOQUEADO<br><small>Razón: {razon}<br>Detectado por {malicious} motores de seguridad.</small>"
            
            return "SEGURO: No se detectaron amenazas en el enlace."
        
        elif response.status_code == 404:
            requests.post("https://www.virustotal.com/api/v3/urls", headers=headers, data={'url': data_qr})
            return "Analizando... Reintente en 10 seg."
        
        return "Servicio de análisis no disponible."
    except Exception as e:
        return f"Error de conexión: {str(e)}"

# --- RUTA PRINCIPAL ---
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        url_detectada = request.form.get('url')
        if url_detectada:
            return analizar_url(url_detectada)
    return render_template('index.html')

# --- RUTAS PWA ---
@app.route('/manifest.json')
def manifest():
    return send_from_directory('static', 'manifest.json')

@app.route('/sw.js')
def sw():
    return send_from_directory('static', 'sw.js')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
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
    
    # Caso 3: Texto plano (no empieza con http/https)
    if not data_qr.lower().startswith("http"):
        resumen = (data_qr[:50] + '...') if len(data_qr) > 50 else data_qr
        return f"DETECTADO: TEXTO PLANO<br><small>Contenido: {resumen}<br>Advertencia: No sigas instrucciones que soliciten transferencias o claves.</small>"

    # PROCESAMIENTO DE URL (VIRUSTOTAL)
    url_id = base64.urlsafe_b64encode(data_qr.encode()).decode().strip("=")
    headers = {"x-apikey": API_KEY}
    
    try:
        response = requests.get(f"https://www.virustotal.com/api/v3/urls/{url_id}", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            attr = data['data']['attributes']
            stats = attr['last_analysis_stats']
            malicious = stats.get('malicious', 0)
            
            if malicious > 0:
                results = attr['last_analysis_results']
                
                # Conjunto para tipos detectados (evitar duplicados)
                tipos = set()
                
                # 1. Prioridad alta: categorías normalizadas de VirusTotal
                for engine in results.values():
                    category = engine.get('category', '').lower()
                    if category in ['phishing', 'malicious', 'suspicious']:
                        tipos.add(category.upper())
                
                # 2. Si no hay categorías claras, analizamos el 'result' crudo
                if not tipos:
                    for engine in results.values():
                        result = engine.get('result', '').lower()
                        if result and result not in ['clean', 'unrated', 'harmless', None]:
                            # Normalización simple y común
                            if 'phish' in result:
                                tipos.add("PHISHING")
                            elif 'malware' in result or 'malici' in result:
                                tipos.add("MALWARE")
                            elif 'suspicious' in result or 'sospech' in result:
                                tipos.add("SOSPECHOSO")
                            elif 'scam' in result or 'fraude' in result:
                                tipos.add("ESTAFA/SCAM")
                            elif 'blacklist' in result or 'blocked' in result:
                                tipos.add("EN LISTA NEGRA")
                            else:
                                # Si es algo específico del motor, lo tomamos limpio
                                cleaned = result.split()[0].upper() if result.split() else "MALICIOSO"
                                tipos.add(cleaned)
                
                # Determinamos la razón principal (prioridad: phishing > malware > etc.)
                razon = "Amenaza detectada"
                if "PHISHING" in tipos:
                    razon = "PHISHING"
                elif "MALWARE" in tipos:
                    razon = "MALWARE"
                elif "SOSPECHOSO" in tipos:
                    razon = "SITIO SOSPECHOSO"
                elif "ESTAFA/SCAM" in tipos:
                    razon = "ESTAFA / SCAM"
                elif tipos:
                    # Mostramos los tipos encontrados (máximo 2 para no saturar)
                    razon = " / ".join(sorted(list(tipos))[:2])
                
                return (f"BLOQUEADO<br>"
                        f"<small>Razón: {razon}<br>"
                        f"Detectado por {malicious} motores de seguridad.</small>")
            
            return "SEGURO: No se detectaron amenazas en el enlace."
        
        elif response.status_code == 404:
            # Enviar a análisis (asíncrono)
            requests.post("https://www.virustotal.com/api/v3/urls", headers=headers, data={'url': data_qr})
            return "Analizando... Reintente en 10-15 segundos."
        
        else:
            return f"Error en VirusTotal: Código {response.status_code}"
    
    except Exception as e:
        return f"Error de conexión con VirusTotal: {str(e)}"

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
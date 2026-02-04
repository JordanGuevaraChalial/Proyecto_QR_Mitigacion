# 🛡️ QR Shield ESPE

**Sistema de Mitigación de Amenazas en Códigos QR** lo que hace esta aplicación detecta y bloquea ataques de **QRishing**, configuraciones de Wi-Fi maliciosas y suplantación de identidad en tiempo real.

---

## Requisitos de Instalación

1. **Python 3.10 o superior.**
2. **Librerías necesarias:**
   ```bash
   pip install flask opencv-python pyzbar requests
   ```

3. Ngrok: Para que la cámara del celular funcione fuera de tu PC.
4. API Key: Regístrate en VirusTotal para obtener tu llave gratuita.
## Estructura del Proyecto
```
Proyecto_QR_Mitigacion/
├── app.py                # Servidor Backend (Python + Flask)
├── templates/
│   └── index.html        # Interfaz de Usuario
└── static/               # Archivos Estáticos
    ├── manifest.json     # Configuración PWA
    ├── sw.js             # Service Worker (Instalación)
    ├── css/
    │   └── styles.css    # Diseño y Colores
    └── js/
        └── script.js     # Lógica del Escáner
```
## Acciones de la App

1. URL Segura: Permite el acceso (Color Verde).
2. Phishing / Malware: Bloqueo total basado en 70+ motores (Color Rojo).
3. Redes Wi-Fi: Alerta de interceptación de datos (Color Naranja).
4. Contactos / Texto: Advertencia de Ingeniería Social (Color Naranja).

## Configuración y Ejecución
1. Configurar la API
Abre app.py y pega tu clave en la línea: API_KEY = "API_KEY"

2. Iniciar el Servidor
En tu terminal ejecuta:
```bash
python app.py
```
3. Abrir el Túnel (Ngrok)
En otra terminal ejecuta:
```bash
ngrok http 5000 o ./ngrok http 5000
```
Importante: Escanea el código QR o abre la URL https://... que te entregue Ngrok y puedes usarlo en tu celular o computadora.



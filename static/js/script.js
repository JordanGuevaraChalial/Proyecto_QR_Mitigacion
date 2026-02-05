let deferredPrompt;
let html5QrCode = null;
let currentScannerRunning = false;

const installBtn = document.getElementById('installApp');
const statusDiv = document.getElementById('status');
const resetBtn = document.getElementById('btn-reset');
const readerDiv = document.getElementById('reader');

// --- PWA instalación ---
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.style.display = 'block';
});

installBtn.addEventListener('click', () => {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        deferredPrompt.userChoice.then((choiceResult) => {
            if (choiceResult.outcome === 'accepted') {
                installBtn.style.display = 'none';
            }
            deferredPrompt = null;
        });
    }
});

// ── Limpieza segura del escáner anterior ────────
function destroyScanner() {
    if (html5QrCode) {
        try {
            html5QrCode.stop();
            console.log("Escáner detenido");
        } catch (err) {
            console.log("No se pudo detener (probablemente ya estaba detenido):", err.message);
        }
        try {
            html5QrCode.clear();
        } catch (err) {}
        
        html5QrCode = null;
        currentScannerRunning = false;
        readerDiv.innerHTML = '';  // Limpieza completa del div
        statusDiv.style.display = 'none';
        resetBtn.style.display = 'none';
    }
}

// ── Iniciar escáner ────────
function startScanner() {
    if (currentScannerRunning) return;

    destroyScanner();  // Siempre limpia antes

    html5QrCode = new Html5Qrcode("reader");

    const config = {
        fps: 10,
        qrbox: { width: 250, height: 250 },
    };

    function onScanSuccess(decodedText, decodedResult) {
        // Detenemos de forma segura
        try { html5QrCode.stop(); } catch (e) {}
        currentScannerRunning = false;

        statusDiv.style.display = 'block';
        statusDiv.innerHTML = "🔍 Analizando...";

        fetch('/', {
            method: 'POST',
            headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
            body: `url=${encodeURIComponent(decodedText)}`
        })
        .then(response => response.text())
        .then(data => {
            // Limpiamos clases previas
            statusDiv.className = "result-box";

            let isSafe = false;
            let safeUrl = decodedText.trim();  // Guardamos la URL original del QR

            if (data.includes("SEGURO: No se detectaron amenazas en el enlace.")) {
                isSafe = true;
                statusDiv.className = "result-box safe";
                statusDiv.innerHTML = data + '<br><br>' +
                    '<button id="goToSafeLink" ' +
                    'style="padding: 12px 28px; font-size: 1.1em; background: #28a745; color: white; border: none; border-radius: 8px; cursor: pointer; box-shadow: 0 2px 8px rgba(0,0,0,0.2);">' +
                    'Ir a esa dirección →' +
                    '</button>';
            } 
            else if (data.toUpperCase().includes("BLOQUEADO")) {
                statusDiv.className = "result-box danger";
                statusDiv.innerHTML = data;
            } 
            else {
                // ALERTA, DETECTADO, WiFi, vCard, texto plano, etc.
                statusDiv.className = "result-box warning";
                statusDiv.innerHTML = data;
            }

            resetBtn.style.display = 'inline-block';

            // Agregamos el evento al botón solo si es seguro
            if (isSafe) {
                setTimeout(() => {
                    const goBtn = document.getElementById('goToSafeLink');
                    if (goBtn) {
                        goBtn.addEventListener('click', () => {
                            window.location.href = safeUrl;
                            // Alternativa (si prefieres abrir en pestaña nueva):
                            // window.open(safeUrl, '_blank', 'noopener,noreferrer');
                        });
                    }
                }, 50);  // Pequeño delay para asegurar que el botón esté en el DOM
            }
        })
        .catch(err => {
            statusDiv.innerHTML = "Error al contactar el servidor";
            console.error(err);
            resetBtn.style.display = 'inline-block';
        });
    }

    // Intento principal: preferencia suave a cámara trasera
    html5QrCode.start(
        { facingMode: "environment" },
        config,
        onScanSuccess,
        () => {}  // ignora errores de no-QR
    )
    .then(() => {
        console.log("Cámara iniciada con preferencia trasera (environment)");
        currentScannerRunning = true;
    })
    .catch(err => {
        console.warn("Fallo con facingMode: environment →", err.message);

        // Último recurso: sin restricciones
        html5QrCode.start(
            undefined,
            config,
            onScanSuccess,
            () => {}
        )
        .then(() => {
            console.log("Iniciado sin restricciones (cámara por defecto)");
            currentScannerRunning = true;
        })
        .catch(finalErr => {
            console.error("Fallo total al iniciar cámara:", finalErr);
            statusDiv.innerHTML = "No se pudo abrir la cámara.<br>Verifica permisos o prueba otro navegador.";
            statusDiv.style.display = 'block';
            resetBtn.style.display = 'inline-block';
        });
    });
}

// ── Botón "Nuevo Escaneo" ────────
resetBtn.onclick = () => {
    destroyScanner();
    startScanner();
};

// ── Iniciar al cargar la página ────────
startScanner();
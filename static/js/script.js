let deferredPrompt;
const installBtn = document.getElementById('installApp');

// --- LÓGICA DE INSTALACIÓN (PWA) ---
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    installBtn.style.display = 'block'; // Solo mostramos el botón si es instalable
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

function onScanSuccess(decodedText) {
    html5QrcodeScanner.clear();
    const statusDiv = document.getElementById('status');
    const resetBtn = document.getElementById('btn-reset');
    
    statusDiv.style.display = 'block';
    statusDiv.innerHTML = "🔍 Analizando...";

    fetch('/', {
        method: 'POST',
        headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
        body: `url=${encodeURIComponent(decodedText)}`
    })
    .then(response => response.text())
    .then(data => {
        if (data.includes("🛑 BLOQUEADO")) {
            statusDiv.className = "result-box danger";
        } else if (data.includes("⚠️") || data.includes("👤") || data.includes("📝")) {
            statusDiv.className = "result-box warning"; 
        } else {
            statusDiv.className = "result-box safe";
        }
        statusDiv.innerHTML = data;
        resetBtn.style.display = 'inline-block';
        statusDiv.className = data.includes("BLOQUEADO") ? "result-box danger" : "result-box safe";
    });
}

var html5QrcodeScanner = new Html5QrcodeScanner("reader", { fps: 10, qrbox: 250 });
html5QrcodeScanner.render(onScanSuccess);
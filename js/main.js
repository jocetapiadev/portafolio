/**
 * main.js - Modulo interactivo del Portafolio
 * Desarrollado para Jocelyn Tapia Arancibia
 */

document.addEventListener('DOMContentLoaded', () => {
    initClipboardEvents();
    initPrintEvent();
});

/**
 * Maneja la copia al portapapeles y notificaciones Toast
 */
function initClipboardEvents() {
    const btnCopyCode = document.getElementById('btnCopyCode');
    const cardEmail = document.getElementById('cardEmail');
    const codeSnippet = document.getElementById('codeSnippet');

    if (btnCopyCode && codeSnippet) {
        btnCopyCode.addEventListener('click', () => {
            copyTextToClipboard(codeSnippet.innerText, 'Código Python copiado al portapapeles');
        });
    }

    if (cardEmail) {
        cardEmail.addEventListener('click', () => {
            copyTextToClipboard('jocelyntapia.arancibia@gmail.com', 'Correo copiado al portapapeles');
        });
    }
}

/**
 * Copia texto genérico e invoca el Toast
 */
function copyTextToClipboard(text, successMessage) {
    navigator.clipboard.writeText(text).then(() => {
        showToast(successMessage);
    }).catch(err => {
        console.error('Error al copiar: ', err);
    });
}

/**
 * Muestra el elemento Toast emergente
 */
function showToast(message) {
    const toast = document.getElementById('toast');
    if (!toast) return;

    toast.textContent = message;
    toast.classList.add('show');

    setTimeout(() => {
        toast.classList.remove('show');
    }, 3000);
}

/**
 * Evento de impresión de CV
 */
function initPrintEvent() {
    const btnPrint = document.getElementById('btnPrint');
    if (btnPrint) {
        btnPrint.addEventListener('click', () => {
            window.print();
        });
    }
}

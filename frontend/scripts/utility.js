import { modalTitleEl, modalBodyEl } from "./references.js";

// Funzione per mostrare la modale con titolo + messaggio
export function showModal(title, message) {
  // Imposta il testo
  modalTitleEl.textContent = title;
  modalBodyEl.textContent = message;

  // Seleziona il contenitore della modale
  const modalEl = document.getElementById("myModal");
  // Crea un'istanza di Bootstrap.Modal
  const modal = new bootstrap.Modal(modalEl, {
    // configurazioni (se ne servono)
  });

  // Mostra la modale
  modal.show();
}

export function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
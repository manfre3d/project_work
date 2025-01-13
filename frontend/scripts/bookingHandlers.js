import { bookingList, formNewBooking } from "./references.js";
import { showSection } from "./navigationHandlers.js";
import { sectionBookings } from "./references.js";
import { showModal } from "./utility.js";

let selectedBookingId = null; // traccia l'id della prenotazione selezionata per l'eliminazione

/**
 * Carica tutte le prenotazioni dal server e aggiorna la lista nel DOM.
 */
export async function loadAllBookings() {
  try {
    const response = await fetch("http://localhost:8000/bookings", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nel caricamento delle prenotazioni");
    }

    const bookings = await response.json();
    renderBookingList(bookings); // aggiorna la lista delle prenotazioni nel DOM
  } catch (error) {
    console.error("Errore nel caricamento delle prenotazioni:", error);
    showModal("Errore", `Impossibile caricare le prenotazioni: ${error.message}`);
  }
}

/**
 * Aggiorna la lista delle prenotazioni nel DOM.
 * @param {Array} bookings - elenco delle prenotazioni dal server.
 */
function renderBookingList(bookings) {
  bookingList.innerHTML = ""; // svuota la lista esistente

  bookings.forEach((booking) => {
    const bookingItem = document.createElement("div");
    bookingItem.classList.add("booking-item");

    bookingItem.innerHTML = `
      <h3>${booking.service_name}</h3>
      <p><strong>Periodo:</strong> dal ${booking.start_date} al ${booking.end_date}</p>
      <p><strong>Stato:</strong> ${booking.status}</p>
      <div class="actions">
        <button class="btn btn-edit" data-id="${booking.id}">Modifica</button>
        <button class="btn btn-delete" data-id="${booking.id}">Elimina</button>
      </div>
    `;
    bookingList.appendChild(bookingItem);
  });

  attachEventHandlers();
}

/**
 * Collega i pulsanti di modifica ed eliminazione alle relative funzioni.
 */
function attachEventHandlers() {
  document.querySelectorAll(".btn-edit").forEach((btn) =>
    btn.addEventListener("click", handleEditBooking)
  );

  document.querySelectorAll(".btn-delete").forEach((btn) =>
    btn.addEventListener("click", handleDeleteBooking)
  );
}

/**
 * Gestisce la modifica di una prenotazione.
 * @param {Event} event - evento click sul pulsante di modifica.
 */
async function handleEditBooking(event) {
  const bookingId = event.target.dataset.id;

  showModal(
    "Modifica Prenotazione",
    `La funzionalità di modifica per la prenotazione con ID ${bookingId} sarà presto disponibile.`
  );
}

/**
 * Mostra la modale di conferma eliminazione.
 * @param {Event} event - evento click sul pulsante di eliminazione.
 */
async function handleDeleteBooking(event) {
  selectedBookingId = event.target.dataset.id; // salva l'id della prenotazione da eliminare

  const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
  confirmDeleteModal.show();
}

/**
 * Invio della richiesta DELETE al server per eliminare la prenotazione selezionata.
 */
async function confirmDeleteBooking() {
  if (!selectedBookingId) return;

  try {
    const response = await fetch(`http://localhost:8000/bookings/${selectedBookingId}`, {
      method: "DELETE",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nell'eliminazione della prenotazione");
    }

    const confirmDeleteModal = bootstrap.Modal.getInstance(
      document.getElementById("confirmDeleteModal")
    );
    confirmDeleteModal.hide(); // chiudi la modale

    // rimuove l'elemento della prenotazione dalla lista senza ricaricare tutto
    document.querySelector(`[data-id="${selectedBookingId}"]`).parentElement.remove();
    showModal("Prenotazione eliminata", "La prenotazione è stata eliminata con successo.");
    selectedBookingId = null; // resetta l'id della prenotazione
  } catch (error) {
    console.error("Errore nell'eliminazione della prenotazione:", error);
    showModal("Errore", `Impossibile eliminare la prenotazione: ${error.message}`);
  }
}

/**
 * Configura il gestore per la creazione di una nuova prenotazione.
 */
export function setupBookingHandler() {
  formNewBooking.addEventListener("submit", async (e) => {
    e.preventDefault();

    const service_id = document.getElementById("service").value.trim();
    const start_date = document.getElementById("start_date").value;
    const end_date = document.getElementById("end_date").value;

    const newBooking = { service_id, start_date, end_date };

    try {
      const response = await fetch("http://localhost:8000/bookings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(newBooking),
      });

      if (!response.ok) {
        const errorMsg = await response.json();
        throw new Error(errorMsg.error || "Errore nella creazione prenotazione");
      }

      const created = await response.json();
      showModal(
        "Prenotazione creata",
        `La tua prenotazione con ID=${created.id} è stata creata con successo.`
      );

      formNewBooking.reset();
      showSection(sectionBookings);
      loadAllBookings(); // Ricarica la lista delle prenotazioni
    } catch (error) {
      console.error("Errore nella creazione della prenotazione:", error);
      showModal("Errore", `Messaggio: ${error.message}`);
    }
  });
}

// collega il pulsante di conferma eliminazione nella modale
document.getElementById("confirmDeleteBtn").addEventListener("click", confirmDeleteBooking);

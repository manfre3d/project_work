import { bookingList, formNewBooking } from "./references.js";
import { showSection } from "./navigationHandlers.js";
import { sectionBookings } from "./references.js";
import { showModal } from "./utility.js";

// traccia l'id della prenotazione selezionata per modifica/eliminazione
let selectedBookingId = null; 

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
 * aggiorna la lista delle prenotazioni nel DOM.
 * @param {Array} bookings - elenco delle prenotazioni dal server.
 */
function renderBookingList(bookings) {
  bookingList.innerHTML = "";

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

async function loadServices() {
  try {
    const response = await fetch("http://localhost:8000/services", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nel caricamento dei servizi");
    }

    const services = await response.json();
    const editServiceSelect = document.getElementById("editService");

    // Svuota le opzioni esistenti
    editServiceSelect.innerHTML = "";

    // Aggiungi le opzioni dei servizi
    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id;
      option.textContent = service.name;
      editServiceSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Errore nel caricamento dei servizi:", error);
    showModal("Errore", `Impossibile caricare i servizi: ${error.message}`);
  }
}


/**
 * mostra la modale per modificare una prenotazione.
 * @param {Event} event - evento click sul pulsante di modifica.
 */
async function handleEditBooking(event) {
  selectedBookingId = event.target.dataset.id;

  // richiama i servizi disponibili, per visualizzarli nella modale di modifica
  await loadServices();

  try {
    const response = await fetch(`http://localhost:8000/bookings/${selectedBookingId}`, {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nel recupero della prenotazione");
    }

    const booking = await response.json();
    populateEditModal(booking); // riempi i dati nella modale di modifica
  } catch (error) {
    console.error("Errore nel recupero della prenotazione:", error);
    showModal("Errore", `Impossibile modificare la prenotazione: ${error.message}`);
  }
}

/**
 * riempi i dati nella modale di modifica.
 * @param {Object} booking - dati della prenotazione.
 */
function populateEditModal(booking) {
  document.getElementById("editService").value = booking.service_id;
  document.getElementById("editStartDate").value = booking.start_date;
  document.getElementById("editEndDate").value = booking.end_date;

  const editModal = new bootstrap.Modal(document.getElementById("editBookingModal"));
  editModal.show();
}

/**
 * conferma e invia la modifica della prenotazione al server.
 */
async function confirmEditBooking() {
  const updatedBooking = {
    service_id: document.getElementById("editService").value.trim(),
    start_date: document.getElementById("editStartDate").value,
    end_date: document.getElementById("editEndDate").value,
  };

  try {
    const response = await fetch(`http://localhost:8000/bookings/${selectedBookingId}`, {
      method: "PUT",
      headers: {
        "Content-Type": "application/json",
      },
      credentials: "include",
      body: JSON.stringify(updatedBooking),
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nella modifica della prenotazione");
    }

    const editModal = bootstrap.Modal.getInstance(
      document.getElementById("editBookingModal")
    );
    editModal.hide();

    showModal("Prenotazione modificata", "La prenotazione è stata modificata con successo.");
    loadAllBookings();
    selectedBookingId = null;
  } catch (error) {
    console.error("Errore nella modifica della prenotazione:", error);
    showModal("Errore", `Impossibile modificare la prenotazione: ${error.message}`);
  }
}

/**
 * mostra la modale di conferma eliminazione.
 * @param {Event} event - evento click sul pulsante di eliminazione.
 */
async function handleDeleteBooking(event) {
  selectedBookingId = event.target.dataset.id;

  const confirmDeleteModal = new bootstrap.Modal(document.getElementById("confirmDeleteModal"));
  confirmDeleteModal.show();
}

/**
 * conferma l'eliminazione della prenotazione selezionata.
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
    confirmDeleteModal.hide();

    document.querySelector(`[data-id="${selectedBookingId}"]`).parentElement.remove();
    showModal("Prenotazione eliminata", "La prenotazione è stata eliminata con successo.");
    selectedBookingId = null;
  } catch (error) {
    console.error("Errore nell'eliminazione della prenotazione:", error);
    showModal("Errore", `Impossibile eliminare la prenotazione: ${error.message}`);
  }
}

/**
 * Recupera i servizi dal server e popola il menu a discesa
 */
async function populateServicesDropdown() {
  try {
    const response = await fetch("http://localhost:8000/services", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nel caricamento dei servizi");
    }

    const services = await response.json();
    const serviceSelect = document.getElementById("service");
    serviceSelect.innerHTML = ""; // Svuota le opzioni esistenti

    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id;
      option.textContent = `${service.name} - ${service.description}`;
      serviceSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Errore nel caricamento dei servizi:", error);
    showModal("Errore", `Impossibile caricare i servizi: ${error.message}`);
  }
}

/**
 * Configura il gestore per la creazione di una nuova prenotazione.
 */
export function setupBookingHandler() {
  
  formNewBooking.addEventListener("submit", async (e) => {
    // Evita il comportamento predefinito del form (ricaricamento della pagina) 
    e.preventDefault();
    // Popola i servizi disponibili
    populateServicesDropdown();

    const service_id = document.getElementById("service").value;
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

      formNewBooking.reset(); // Resetta il form
    } catch (error) {
      console.error("Errore nella creazione della prenotazione:", error);
      showModal("Errore", `Messaggio: ${error.message}`);
    }
  });
}

// collega il pulsante di conferma modifica nella modale
document.getElementById("confirmEditBtn").addEventListener("click", confirmEditBooking);

// collega il pulsante di conferma eliminazione nella modale
document.getElementById("confirmDeleteBtn").addEventListener("click", confirmDeleteBooking);

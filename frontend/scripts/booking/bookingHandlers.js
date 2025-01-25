import { bookingList, formNewBooking } from "../references.js";
import { showModal, calculateTotalPrice } from "../utility.js";
import { renderAdminBookingList } from "./bookingHandlersAdmin.js";
import { 
  selectedBookingId,
    setSelectedBookingId
  } from "../references.js";
import { loadServices } from "../serviceHandlers.js";

/**
 * aggiorna la lista delle prenotazioni nel DOM.
 * caricando dinamicamente i dati delle prenotazioni.
 * @param {Array} bookings - elenco delle prenotazioni dal server.
 */
function renderUserBookingList(bookings) {
  bookingList.innerHTML = "";
  if(bookings.length === 0) 
    bookingList.innerHTML = `
  <h5>Nessuna prenotazione trovata.</h5>
  `;

  bookings.forEach((booking) => {
    const bookingItem = document.createElement("div");
    bookingItem.classList.add("booking-item");

    bookingItem.innerHTML = `
      <h3>${booking.service_name}</h3>
      <p><strong>Periodo:</strong> dal ${booking.start_date} al ${
      booking.end_date
    }</p>
      <p><strong>Prezzo Totale:</strong> €${booking.total_price.toFixed(2)}</p>
      <p><strong>Stato:</strong> ${booking.status}</p>
      <div class="actions">
        <button class="btn btn-edit btn-user-edit" data-id="${booking.id}">Modifica</button>
        <button class="btn btn-delete btn-user-delete" data-id="${booking.id}">Elimina</button>
      </div>
    `;
    bookingList.appendChild(bookingItem);
  });

  attachEventHandlers();
}
/**
 * collega i pulsanti di modifica ed eliminazione alle relative funzioni di prenotazione.
 */
export function attachEventHandlers() {
  document
    .querySelectorAll(".btn-user-edit")
    .forEach((btn) => btn.addEventListener("click", handleEditBooking));

  document
    .querySelectorAll(".btn-user-delete")
    .forEach((btn) => btn.addEventListener("click", handleDeleteBooking));
}
/**
 * mostra la modale per modificare una prenotazione.
 * @param {Event} event - evento click sul pulsante di modifica.
 */
async function handleEditBooking(event) {
  setSelectedBookingId(event.target.dataset.id);

  // richiama i servizi disponibili, per visualizzarli nella modale di modifica
  await loadServices();

  try {
    const response = await fetch(
      `bookings/${selectedBookingId}`,
      {
        method: "GET",
        credentials: "include",
      }
    );

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nel recupero della prenotazione");
    }

    const booking = await response.json();
    populateEditModal(booking);
  } catch (error) {
    console.error("Errore nel recupero della prenotazione:", error);
    showModal(
      "Errore",
      `Impossibile modificare la prenotazione: ${error.message}`
    );
  }
}
/**
 * riempi/inizializza i dati nella modale di modifica.
 * @param {Object} booking - dati della prenotazione.
 */
function populateEditModal(booking) {
  const serviceSelect = document.getElementById("editService");
  const startDateInput = document.getElementById("editStartDate");
  const endDateInput = document.getElementById("editEndDate");
  const totalPriceElement = document.getElementById("userTotalPrice");
  document.getElementById("confirmEditBtn").addEventListener("click", confirmEditBooking);

  serviceSelect.value = booking.service_id;
  startDateInput.value = booking.start_date;
  endDateInput.value = booking.end_date;
  const updateTotalPrice = () => {
    const pricePerDay = parseFloat(serviceSelect.options[serviceSelect.selectedIndex]?.dataset.price || 0);
    console.log("Prezzo giornaliero:", pricePerDay); 
    const totalPrice = calculateTotalPrice(startDateInput.value, endDateInput.value, pricePerDay);
    totalPriceElement.innerHTML = `Prezzo Totale: €${totalPrice.toFixed(2)}`;
  };

  // Aggiungi i listener per aggiornare il prezzo in tempo reale
  serviceSelect.addEventListener("change", updateTotalPrice);
  startDateInput.addEventListener("change", updateTotalPrice);
  endDateInput.addEventListener("change", updateTotalPrice);

  // Aggiorna il prezzo inizialmente
  updateTotalPrice();

  const editModal = new bootstrap.Modal(
    document.getElementById("editBookingModal")
  );
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
    const response = await fetch(
      `bookings/${selectedBookingId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(updatedBooking),
      }
    );

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(
        errMsg.error || "Errore nella modifica della prenotazione"
      );
    }

    const editModal = bootstrap.Modal.getInstance(
      document.getElementById("editBookingModal")
    );
    editModal.hide();

    showModal(
      "Prenotazione modificata",
      "La prenotazione è stata modificata con successo."
    );
    loadAllBookings();
    setSelectedBookingId(null);
  } catch (error) {
    console.error("Errore nella modifica della prenotazione:", error);
    showModal(
      "Errore",
      `Impossibile modificare la prenotazione: ${error.message}`
    );
  }
}
/**
 * mostra la modale di conferma eliminazione.
 * @param {Event} event - evento click sul pulsante di eliminazione.
 */
async function handleDeleteBooking(event) {
  setSelectedBookingId(event.target.dataset.id);
  const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
  confirmDeleteBtn.addEventListener("click", confirmDeleteBooking);
  confirmDeleteBtn.setAttribute("data-context", "user");
  const confirmDeleteModal = new bootstrap.Modal(
    document.getElementById("confirmDeleteModal")
  );
  confirmDeleteModal.show();
}
/**
 * conferma l'eliminazione della prenotazione selezionata.
 */
export async function confirmDeleteBooking() {
  const deleteContext = document
    .getElementById("confirmDeleteBtn")
    .getAttribute("data-context");

  if (!selectedBookingId || !deleteContext) return;

  try {
    const response = await fetch(
      `bookings/${selectedBookingId}`,
      {
        method: "DELETE",
        credentials: "include",
      }
    );

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(
        errMsg.error || "Errore nell'eliminazione della prenotazione"
      );
    }

    const confirmDeleteModal = bootstrap.Modal.getInstance(
      document.getElementById("confirmDeleteModal")
    );
    confirmDeleteModal.hide();

    if (deleteContext === "admin") {
      const adminTableBody = document.getElementById("admin-bookings-tbody");
      const rows = adminTableBody.querySelectorAll("tr");

      rows.forEach((row) => {
        const idCell = row.querySelector("td:first-child");
        if (idCell && idCell.textContent.trim() === selectedBookingId) {
          row.remove();
        }
      });
    } else if (deleteContext === "user") {
      const cardToDelete = document.querySelector(
        `.btn-user-delete[data-id="${selectedBookingId}"]`
      )?.closest(".booking-item");
      if (cardToDelete) cardToDelete.remove();
    }

    showModal(
      "Prenotazione eliminata",
      `La prenotazione con ID=${selectedBookingId} è stata eliminata con successo.`
    );

    setSelectedBookingId(null);
  } catch (error) {
    console.error("Errore nell'eliminazione della prenotazione:", error);
    showModal(
      "Errore",
      `Impossibile eliminare la prenotazione: ${error.message}`
    );
  }
}
/**
 * configura il gestore per la creazione di una nuova prenotazione.
 * collega i listener agli elementi del form di creazione della prenotazione.
 */
export function setupBookingHandler() {
  const serviceSelect = document.getElementById("service");
  const startDateInput = document.getElementById("start_date");
  const endDateInput = document.getElementById("end_date");
  const pricePreview = document.getElementById("pricePreview");

  const updateTotalPrice = () => {
    const pricePerDay = parseFloat(serviceSelect.options[serviceSelect.selectedIndex]?.dataset.price || 0);
    console.log("Prezzo giornaliero:", pricePerDay);
    const totalPrice = calculateTotalPrice(startDateInput.value, endDateInput.value, pricePerDay);
    console.log("Prezzo totale calcolato:", totalPrice);
    pricePreview.innerHTML = `<strong>Prezzo Totale:</strong> €${totalPrice.toFixed(2)}`;
  };

  serviceSelect.addEventListener("change", updateTotalPrice);
  startDateInput.addEventListener("change", updateTotalPrice);
  endDateInput.addEventListener("change", updateTotalPrice);

  formNewBooking.addEventListener("submit", async (e) => {
    // evita il comportamento predefinito del form (ricaricamento della pagina)
    e.preventDefault();

    const service_id = serviceSelect.value;
    const start_date = startDateInput.value;
    const end_date = endDateInput.value;

    const pricePerDay = parseFloat(serviceSelect.options[serviceSelect.selectedIndex]?.dataset.price || 0);
    const total_price = calculateTotalPrice(start_date, end_date, pricePerDay);

    
    const newBooking = { service_id, start_date, end_date, total_price };

    try {
      const response = await fetch("bookings", {
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
      pricePreview.innerHTML = `<strong>Prezzo Totale:</strong> €0.00`; 
    } catch (error) {
      console.error("Errore nella creazione della prenotazione:", error);
      showModal("Errore", `Messaggio: ${error.message}`);
    }
  });
}
/**
 * Carica tutte le prenotazioni dal server e le visualizza nel DOM.
 * gestisce la visualizzazione delle prenotazioni in base al ruolo dell'utente <User> e <Admin>.
 */
export async function loadAllBookings() {
  try {
    const response = await fetch("bookings", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(
        errMsg.error || "Errore nel caricamento delle prenotazioni"
      );
    }

    const bookings = await response.json();
    const role = sessionStorage.getItem("userRole");

    if (role === "admin") {
      renderAdminBookingList(bookings);
    } else {
      renderUserBookingList(bookings);
    }
  } catch (error) {
    console.error("Errore nel caricamento delle prenotazioni:", error);
    showModal(
      "Errore",
      `Impossibile caricare le prenotazioni: ${error.message}`
    );
  }
}





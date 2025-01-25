import { 
    selectedBookingId,
    selectedUserId,
    setSelectedUserId,
    setSelectedBookingId
} from "../references.js";
import { showModal, calculateTotalPrice } from "../utility.js";
import { loadServices } from "../serviceHandlers.js";
import { loadAllBookings, confirmDeleteBooking} from "./bookingHandlers.js";

export async function populateAdminEditModal(booking) {
  const serviceSelect = document.getElementById("editAdminService");
  const startDateInput = document.getElementById("editAdminStartDate");
  const endDateInput = document.getElementById("editAdminEndDate");
  const totalPriceElement = document.getElementById("adminTotalPrice");

  document.getElementById("editAdminUser").value = booking.username || "N/A";
  startDateInput.value = booking.start_date;
  endDateInput.value = booking.end_date;
  document.getElementById("editAdminStatus").value = booking.status;
  document.getElementById("saveAdminBookingBtn").addEventListener("click", saveAdminBooking);

  const updateTotalPrice = () => {
    const pricePerDay = parseFloat(serviceSelect.options[serviceSelect.selectedIndex]?.dataset.price || 0);
    const totalPrice = calculateTotalPrice(startDateInput.value, endDateInput.value, pricePerDay);
    totalPriceElement.innerHTML = `<strong>Prezzo Totale:</strong> €${totalPrice.toFixed(2)}`;
  };

  try {
    await loadServices();
    serviceSelect.value = booking.service_id;

    serviceSelect.addEventListener("change", updateTotalPrice);
    startDateInput.addEventListener("change", updateTotalPrice);
    endDateInput.addEventListener("change", updateTotalPrice);

    updateTotalPrice();
  } catch (error) {
    console.error(
      "Errore nel caricamento dei servizi per la modale admin:",
      error
    );
    showModal("Errore", `Impossibile caricare i servizi: ${error.message}`);
    return;
  }

  const editModal = new bootstrap.Modal(
    document.getElementById("editAdminBookingModal")
  );
  editModal.show();
  document.getElementById("editAdminBookingModal").focus();
}
export function renderAdminBookingList(bookings) {
  const adminTableBody = document.getElementById("admin-bookings-tbody");
  adminTableBody.innerHTML = "";

  bookings.forEach((booking) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td data-label="ID">${booking.id}</td>
      <td data-label="Utente">${booking.username || "N/A"}</td>
      <td data-label="Servizio">${booking.service_name}</td>
      <td data-label="Inizio">${booking.start_date}</td>
      <td data-label="Fine">${booking.end_date}</td>
      <td data-label="Prezzo Totale">€${booking.total_price.toFixed(2)}</td> 
      <td data-label="Stato">${booking.status}</td>
      <td data-label="Azioni">
        <div class="card-actions">
          <button 
            class="btn btn-success btn-sm btn-admin-table-success" data-user-id="${
            booking.user_id
          }" data-id="${booking.id}" data-status="confirmed">
            Conferma
          </button>
          <button 
            class="btn btn-primary btn-sm btn-edit btn-admin-table-edit"
            data-id="${booking.id}" data-user-id="${booking.user_id}"
          >
            Modifica
          </button>
          <button 
            class="btn btn-danger btn-sm btn-delete btn-admin-table-cancel" data-user-id="${booking.user_id}"
            data-id="${booking.id}"
          >
            Cancella
          </button>
          <button class="btn btn-warning btn-sm btn-admin-table-pending" data-user-id="${
            booking.user_id
          }" data-id="${booking.id}" data-status="pending"">
            Rendi Pending
          </button>
          <button 
            class="btn btn-danger btn-sm btn-delete btn-admin-table-delete" data-user-id="${booking.user_id}"
            data-id="${booking.id}">
              Elimina
          </button>
        </div>
      </td>
    `;
    adminTableBody.appendChild(row);
  });

  attachAdminBookingEventHandlers();
}
/**
 * Mostra il modale per la modifica di una prenotazione (Admin).
 * @param {number} bookingId - ID della prenotazione da modificare.
 */
async function handleAdminEditBooking(bookingId, userId) {
  setSelectedBookingId(bookingId);
  setSelectedUserId(userId);
  try {
    const response = await fetch(
      `bookings/${bookingId}`,
      {
        method: "GET",
        credentials: "include",
      }
    );

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(
        errMsg.error || "Errore nel caricamento della prenotazione"
      );
    }

    const booking = await response.json();

    populateAdminEditModal(booking);
  } catch (error) {
    console.error("Errore nel caricamento della prenotazione:", error);
    showModal(
      "Errore",
      `Impossibile modificare la prenotazione: ${error.message}`
    );
  }
}
/**
 * Salva le modifiche alla prenotazione.
 */
async function saveAdminBooking() {
  const bookingId = selectedBookingId;
  const updatedBooking = {
    user_id: selectedUserId,
    service_id: document.getElementById("editAdminService").value,
    start_date: document.getElementById("editAdminStartDate").value,
    end_date: document.getElementById("editAdminEndDate").value,
    status: document.getElementById("editAdminStatus").value,
  };

  try {
    const response = await fetch(
      `bookings/${bookingId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify(updatedBooking),
      }
    );
    setSelectedUserId(null);
    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(
        errMsg.error || "Errore nel salvataggio della prenotazione"
      );
    }

    showModal(
      "Prenotazione Modificata",
      "La prenotazione è stata modificata con successo."
    );
    const editModal = bootstrap.Modal.getInstance(
      document.getElementById("editAdminBookingModal")
    );
    editModal.hide();
    document.getElementById("admin-bookings").focus();
    await loadAllBookings(); // Ricarica la lista delle prenotazioni
  } catch (error) {
    console.error("Errore nel salvataggio della prenotazione:", error);
    showModal(
      "Errore",
      `Impossibile salvare la prenotazione: ${error.message}`
    );
  }
}
export function attachAdminBookingEventHandlers() {
  // Listener per i pulsanti "Modifica"
  document.querySelectorAll(".btn-admin-table-edit").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");
      handleAdminEditBooking(bookingId,userId);
    });
  });

  document.querySelectorAll(".btn-admin-table-cancel").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");

      updateBookingStatus(bookingId, "cancelled", userId);
    });
  });
  document.querySelectorAll(".btn-admin-table-pending").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");

      updateBookingStatus(bookingId, "pending", userId);
    });
  });
  document.querySelectorAll(".btn-admin-table-success").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");

      updateBookingStatus(bookingId, "confirmed", userId);
    });
  });
  document.querySelectorAll(".btn-admin-table-delete").forEach((button) => {
    button.addEventListener("click", async (event) => {
        const bookingId = event.target.getAttribute("data-id");
        setSelectedBookingId(bookingId);
    
        const confirmDeleteBtn = document.getElementById("confirmDeleteBtn");
        confirmDeleteBtn.setAttribute("data-context", "admin");
    
        confirmDeleteBtn.addEventListener("click", confirmDeleteBooking);

        const confirmDeleteModal = new bootstrap.Modal(
          document.getElementById("confirmDeleteModal")
        );
        confirmDeleteModal.show();
      });
  });
  
}
/**
 * Aggiorna lo stato di una prenotazione (Admin).
 * @param {number} bookingId - ID della prenotazione.
 * @param {string} newStatus - Nuovo stato della prenotazione.
 */
export async function updateBookingStatus(bookingId, newStatus, userId) {
  try {
    const response = await fetch(
      `bookings/${bookingId}`,
      {
        method: "PUT",
        headers: {
          "Content-Type": "application/json",
        },
        credentials: "include",
        body: JSON.stringify({ status: newStatus, user_id: userId }),
      }
    );

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Errore nell'aggiornamento dello stato");
    }

    showModal(
      "Stato Aggiornato",
      `La prenotazione è stata aggiornata a "${newStatus}".`
    );
    await loadAllBookings();
  } catch (error) {
    console.error("Errore nell'aggiornamento dello stato:", error);
    showModal("Errore", `Impossibile aggiornare lo stato: ${error.message}`);
  }
}


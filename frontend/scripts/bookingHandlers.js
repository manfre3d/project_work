import { bookingList, formNewBooking } from "./references.js";
import { showModal, calculateTotalPrice } from "./utility.js";

// traccia l'id della prenotazione selezionata per modifica/eliminazione
export let selectedBookingId = null;

/**
 * aggiorna la lista delle prenotazioni nel DOM.
 * @param {Array} bookings - elenco delle prenotazioni dal server.
 */
function renderUserBookingList(bookings) {
  bookingList.innerHTML = "";

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
  document
    .querySelectorAll(".btn-edit")
    .forEach((btn) => btn.addEventListener("click", handleEditBooking));

  document
    .querySelectorAll(".btn-delete")
    .forEach((btn) => btn.addEventListener("click", handleDeleteBooking));
}

async function loadServices() {
  try {
    const response = await fetch("http://localhost:8000/services", {
      method: "GET",
      credentials: "include",
    });

    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.errore || "Errore nel caricamento dei servizi");
    }

    const services = await response.json();

    const editAdminServiceSelect = document.getElementById("editAdminService");
    editAdminServiceSelect.innerHTML = "";

    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id;
      option.dataset.price = service.price;
      option.textContent = service.name;
      editAdminServiceSelect.appendChild(option);
    });

    const editServiceSelect = document.getElementById("editService");
    if (editServiceSelect) {
      editServiceSelect.innerHTML = ""; // Svuota le opzioni esistenti

      services.forEach((service) => {
        const option = document.createElement("option");
        option.value = service.id;
        option.textContent = service.name;
        option.dataset.price = service.price;
        editServiceSelect.appendChild(option);
      });
    }
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
    const response = await fetch(
      `http://localhost:8000/bookings/${selectedBookingId}`,
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
 * riempi i dati nella modale di modifica.
 * @param {Object} booking - dati della prenotazione.
 */
function populateEditModal(booking) {
  const serviceSelect = document.getElementById("editService");
  const startDateInput = document.getElementById("editStartDate");
  const endDateInput = document.getElementById("editEndDate");
  const totalPriceElement = document.getElementById("userTotalPrice");

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


async function populateAdminEditModal(booking) {
  const serviceSelect = document.getElementById("editAdminService");
  const startDateInput = document.getElementById("editAdminStartDate");
  const endDateInput = document.getElementById("editAdminEndDate");
  const totalPriceElement = document.getElementById("adminTotalPrice");

  document.getElementById("editAdminUser").value = booking.username || "N/A";
  startDateInput.value = booking.start_date;
  endDateInput.value = booking.end_date;
  document.getElementById("editAdminStatus").value = booking.status;

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
      `http://localhost:8000/bookings/${selectedBookingId}`,
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
    selectedBookingId = null;
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
  selectedBookingId = event.target.dataset.id;

  const confirmDeleteModal = new bootstrap.Modal(
    document.getElementById("confirmDeleteModal")
  );
  confirmDeleteModal.show();
}

/**
 * conferma l'eliminazione della prenotazione selezionata.
 */
async function confirmDeleteBooking() {
  if (!selectedBookingId) return;

  try {
    const response = await fetch(
      `http://localhost:8000/bookings/${selectedBookingId}`,
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

    document
      .querySelector(`[data-id="${selectedBookingId}"]`)
      .parentElement.remove();
    showModal(
      "Prenotazione eliminata",
      "La prenotazione è stata eliminata con successo."
    );
    selectedBookingId = null;
  } catch (error) {
    console.error("Errore nell'eliminazione della prenotazione:", error);
    showModal(
      "Errore",
      `Impossibile eliminare la prenotazione: ${error.message}`
    );
  }
}

/**
 * Recupera i servizi dal server e popola il menu a discesa
 */

// todo capire se ci sono ripetizione
export async function populateServicesDropdown() {
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
    serviceSelect.innerHTML = "";

    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id;
      option.textContent = `${service.name} - ${service.description}`;
      option.dataset.price = service.price;
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
    // Evita il comportamento predefinito del form (ricaricamento della pagina)
    e.preventDefault();

    const service_id = serviceSelect.value;
    const start_date = startDateInput.value;
    const end_date = endDateInput.value;

    const pricePerDay = parseFloat(serviceSelect.options[serviceSelect.selectedIndex]?.dataset.price || 0);
    const total_price = calculateTotalPrice(start_date, end_date, pricePerDay);

    
    const newBooking = { service_id, start_date, end_date, total_price };

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
        throw new Error(errorMsg.errore || "Errore nella creazione prenotazione");
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

export async function loadAllBookings() {
  try {
    const response = await fetch("http://localhost:8000/bookings", {
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
/**
 * Aggiorna lo stato di una prenotazione (Admin).
 * @param {number} bookingId - ID della prenotazione.
 * @param {string} newStatus - Nuovo stato della prenotazione.
 */
async function updateBookingStatus(bookingId, newStatus, userId) {
  try {
    const response = await fetch(
      `http://localhost:8000/bookings/${bookingId}`,
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

/**
 * Renderizza la lista delle prenotazioni per admin.
 */
function renderAdminBookingList(bookings) {
  const adminTableBody = document.getElementById("admin-bookings-tbody");
  adminTableBody.innerHTML = "";

  bookings.forEach((booking) => {
    const row = document.createElement("tr");
    row.innerHTML = `
      <td>${booking.id}</td>
      <td>${booking.username || "N/A"}</td>
      <td>${booking.service_name}</td>
      <td>${booking.start_date}</td>
      <td>${booking.end_date}</td>
      <td>€${booking.total_price.toFixed(2)}</td> 
      <td>${booking.status}</td>
      <td>
        <button class="btn btn-success btn-sm" data-user-id="${
          booking.user_id
        }" data-id="${booking.id}" data-status="confirmed">
          Conferma
        </button>
        <button class="btn btn-warning btn-sm" data-user-id="${
          booking.user_id
        }" data-id="${booking.id}" data-status="pending"">
          Rendi Pending
        <button 
          class="btn btn-primary btn-sm btn-edit"
          data-id="${booking.id}" data-user-id="${booking.user_id}"
        >
          Modifica
        </button>
        <button 
          class="btn btn-danger btn-sm btn-delete" data-user-id="${booking.user_id}"
          data-id="${booking.id}"
        >
          Cancella
        </button>
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
async function handleAdminEditBooking(bookingId) {
  selectedBookingId = bookingId;

  try {
    const response = await fetch(
      `http://localhost:8000/bookings/${bookingId}`,
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
    user_id: document.getElementById("editAdminUser").value,
    service_id: document.getElementById("editAdminService").value,
    start_date: document.getElementById("editAdminStartDate").value,
    end_date: document.getElementById("editAdminEndDate").value,
    status: document.getElementById("editAdminStatus").value,
  };

  try {
    const response = await fetch(
      `http://localhost:8000/bookings/${bookingId}`,
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
  document.querySelectorAll(".btn-edit").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      handleAdminEditBooking(bookingId);
    });
  });

  document.querySelectorAll(".btn-delete").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");

      updateBookingStatus(bookingId, "cancelled", userId);
    });
  });
  document.querySelectorAll(".btn-warning").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");

      updateBookingStatus(bookingId, "pending", userId);
    });
  });
  document.querySelectorAll(".btn-success").forEach((button) => {
    button.addEventListener("click", async (event) => {
      const bookingId = event.target.getAttribute("data-id");
      const userId = event.target.getAttribute("data-user-id");

      updateBookingStatus(bookingId, "confirmed", userId);
    });
  });
}
document
  .getElementById("saveAdminBookingBtn")
  .addEventListener("click", saveAdminBooking);
document
  .getElementById("confirmEditBtn")
  .addEventListener("click", confirmEditBooking);
document
  .getElementById("confirmDeleteBtn")
  .addEventListener("click", confirmDeleteBooking);

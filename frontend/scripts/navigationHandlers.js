import {
  btnLogin,
  btnLogout,
  btnBookings,
  btnNewBooking,
  sectionLogin,
  sectionBookings,
  sectionNewBooking,
  currentUserId,
  setCurrentUserId,
} from "./references.js";

import { loadAllBookings } from "./bookingHandlers.js";

export function showSection(section) {
  // nascondi tutte
  sectionLogin.classList.remove("active");
  sectionBookings.classList.remove("active");
  sectionNewBooking.classList.remove("active");
  // mostra la sezione selezionata
  section.classList.add("active");
}

function handleBtnLoginClick() {
  showSection(sectionLogin);
}

function handleBtnLogoutClick() {
  setCurrentUserId(null);
  alert("Logout effettuato");
  btnLogout.style.display = "none";
  showSection(sectionLogin);
}

function handleBtnBookingsClick() {
  showSection(sectionBookings);
  loadAllBookings(); // carica e mostra tutte le prenotazioni
}

function handleBtnNewBookingClick() {
  if (!currentUserId) {
    alert("Devi effettuare il login per prenotare!");
    showSection(sectionLogin);
    return;
  }
  showSection(sectionNewBooking);
}

// Funzione che collega i pulsanti ai loro handler
export function setupNavHandlers() {
  btnLogin.addEventListener("click", handleBtnLoginClick);
  btnLogout.addEventListener("click", handleBtnLogoutClick);
  btnBookings.addEventListener("click", handleBtnBookingsClick);
  btnNewBooking.addEventListener("click", handleBtnNewBookingClick);
}

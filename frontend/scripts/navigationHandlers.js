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
import { showModal } from "./utility.js";

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

function handleBtnBookingsClick() {
  showSection(sectionBookings);
  // carica e mostra tutte le prenotazioni
  loadAllBookings();
}

function handleBtnNewBookingClick() {
  if (!currentUserId) {
    showModal("Attenzione","Devi effettuare il login per prenotare!");
    showSection(sectionLogin);
    return;
  }
  showSection(sectionNewBooking);
}

// funzione che collega i pulsanti della navigazione ai relativi gestori/handler
export function setupNavHandlers() {
  btnLogin.addEventListener("click", handleBtnLoginClick);
  btnBookings.addEventListener("click", handleBtnBookingsClick);
  btnNewBooking.addEventListener("click", handleBtnNewBookingClick);
}

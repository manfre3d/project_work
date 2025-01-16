import {
  btnLogin,
  btnBookings,
  btnNewBooking,
  sectionLogin,
  sectionBookings,
  sectionNewBooking,
  currentUserId,
  sectionAdminBooking
} from "./references.js";
import { loadAllBookings } from "./bookingHandlers.js";
import { populateServicesDropdown } from "./bookingHandlers.js";
import { 
  showModal,
  updateBookingUIBasedOnRole
} from "./utility.js";

export function showSection(section) {
  
  sectionLogin.classList.remove("active");
  sectionBookings.classList.remove("active");
  sectionNewBooking.classList.remove("active");
  sectionAdminBooking.classList.remove("active");
  section.classList.add("active");
}

function handleBtnLoginClick() {
  showSection(sectionLogin);
}

function handleBtnBookingsClick() {
  if (!currentUserId) {
    showModal("Attenzione","Devi effettuare il login per visualizzare le prenotazioni!");
    showSection(sectionLogin);
    return;
  }
  updateBookingUIBasedOnRole(sessionStorage.getItem("userRole"));
  // showSection(sectionBookings);
  loadAllBookings();
}

function handleBtnNewBookingClick() {
  if (!currentUserId) {
    showModal("Attenzione","Devi effettuare il login per prenotare!");
    showSection(sectionLogin);
    return;
  }
  populateServicesDropdown();
  showSection(sectionNewBooking);
}

// funzione che collega i pulsanti della navigazione ai relativi gestori/handler
export function setupNavHandlers() {
  btnLogin.addEventListener("click", handleBtnLoginClick);
  btnBookings.addEventListener("click", handleBtnBookingsClick);
  btnNewBooking.addEventListener("click", handleBtnNewBookingClick);
}

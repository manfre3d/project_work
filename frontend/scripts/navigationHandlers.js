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
import { loadAllBookings } from "./booking/bookingHandlers.js";
import { populateServicesDropdown } from "./serviceHandlers.js";
import { 
  showModal,
  updateBookingUIBasedOnRole
} from "./utility.js";

/**
  * funzione per mostrare la sezione richiesta.
  * args: section - la sezione da mostrare
 */
export function showSection(section) {
  
  sectionLogin.classList.remove("active");
  sectionBookings.classList.remove("active");
  sectionNewBooking.classList.remove("active");
  sectionAdminBooking.classList.remove("active");
  section.classList.add("active");
}
/**
  * funzione per gestire il click sul pulsante di login e mostrare la sezione correlata
 */
function handleBtnLoginClick() {
  showSection(sectionLogin);
}
/**
  * funzione per gestire il click sul pulsante delle prenotazioni e mostrare la sezione correlata
 */
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
/**
  * funzione per gestire il click sul pulsante di nuova prenotazione e mostrare la sezione correlata
 */
function handleBtnNewBookingClick() {
  if (!currentUserId) {
    showModal("Attenzione","Devi effettuare il login per prenotare!");
    showSection(sectionLogin);
    return;
  }
  populateServicesDropdown();
  showSection(sectionNewBooking);
}
/**
  * funzione per inizializzare i listener per i pulsanti di navigazione
 */
export function setupNavHandlers() {
  btnLogin.addEventListener("click", handleBtnLoginClick);
  btnBookings.addEventListener("click", handleBtnBookingsClick);
  btnNewBooking.addEventListener("click", handleBtnNewBookingClick);
}

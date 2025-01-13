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

function handleBtnLogoutClick() {
  setupLogoutHandler();
}
function setupLogoutHandler() {
  btnLogout.addEventListener("click", async () => {
    try {
      const response = await fetch("http://localhost:8000/logout", {
        method: "POST",
        credentials: "include", 
      });

      if (!response.ok) {
        const errMsg = await response.json();
        throw new Error(errMsg.error || "Errore durante il logout");
      }

      // Se il logout ha successo, rimuovi l'utente corrente
      setCurrentUserId(null);
      showModal("Logout effettuato", "Sei stato disconnesso con successo.");
      // nascondiamo il pulsante logout poiché l'utente è stato disconnesso
      btnLogout.style.display = "none"; 
       // mostra di nuova la sezione di login
      showSection(sectionLogin);
    } catch (error) {
      console.error("Errore logout:", error);
      showModal("Errore", `Errore nel logout: ${error.message}`);
    }
  });
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
  btnLogout.addEventListener("click", handleBtnLogoutClick);
  btnBookings.addEventListener("click", handleBtnBookingsClick);
  btnNewBooking.addEventListener("click", handleBtnNewBookingClick);
}

import { setupNavHandlers, showSection } from "./navigationHandlers.js";
import {
  setupLoginHandler,
  setupRegisterHandler,
  setupLogoutHandler,
} from "./loginHandlers.js";
import { setupBookingHandler, selectedBookingId } from "./bookingHandlers.js";
import { sectionLogin } from "./references.js";

function init() {
  // collega i pulsanti della navigazione ai gestori
  setupNavHandlers();

  // configura il gestore del form di login
  setupLoginHandler();

  // configura il gestore del pulsante di logout
  setupLogoutHandler();

  // configura il gestore del pulsante di registrazione
  setupRegisterHandler();

  // configura il gestore del form di prenotazione
  setupBookingHandler();

  // mostra la sezione login all'avvio
  showSection(sectionLogin);

  
}

// attende che il DOM sia completamente caricato
document.addEventListener("DOMContentLoaded", init);

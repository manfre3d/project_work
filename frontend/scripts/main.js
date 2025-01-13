import { setupNavHandlers, showSection } from "./navigationHandlers.js";
import { setupLoginHandler } from "./loginHandlers.js";
import { setupBookingHandler } from "./bookingHandlers.js";
import { sectionLogin } from "./references.js";
import { setupLogoutHandler } from "./loginHandlers.js";

function init() {
  // collega i pulsanti della navigazione ai gestori
  setupNavHandlers();

  // configura il gestore del form di login
  setupLoginHandler();

  // configura il gestore del pulsante di logout
  setupLogoutHandler();

  // configura il gestore del form di prenotazione
  setupBookingHandler();

  // mostra la sezione login all'avvio
  showSection(sectionLogin);
}

// attende che il DOM sia completamente caricato
document.addEventListener("DOMContentLoaded", init);

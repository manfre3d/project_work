import { setupNavHandlers, showSection } from "./navigationHandlers.js";
import { setupLoginHandler } from "./loginHandlers.js";
import { setupBookingHandler } from "./bookingHandlers.js";
import { sectionLogin } from "./references.js";

function init() {
  // Imposto i listener sui pulsanti di navigazione
  setupNavHandlers();

  // Imposto l'handler per il login
  setupLoginHandler();

  // Imposto l'handler per form prenotazioni
  setupBookingHandler();

  // Mostro la sezione login all'avvio
  showSection(sectionLogin);
}

// Avvio l'inizializzazione
init();

import { setupNavHandlers, showSection } from "./navigationHandlers.js";
import { setupLoginHandler } from "./loginHandlers.js";
import { setupBookingHandler } from "./bookingHandlers.js";
import { sectionLogin } from "./references.js";

function init() {

  // collego i pulsanti della navigazione ai relativi gestori/handler
  setupNavHandlers();

  // handler per il form di login
  setupLoginHandler();

  //handler per il pulsante di logout
  setupLogoutHandler();
  
  // handler per il form di prenotazione
  setupBookingHandler();

  // mostro la sezione di login all'avvio
  showSection(sectionLogin);
}

// inizializzazione
init();

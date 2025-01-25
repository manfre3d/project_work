import { setupNavHandlers, showSection } from "./navigationHandlers.js";
import {
  checkLoggedUserOnInit,
  setupLoginHandler,
  setupRegisterHandler,
  setupLogoutHandler,
} from "./loginHandlers.js";
import { setupBookingHandler } from "./booking/bookingHandlers.js";
import { sectionLogin } from "./references.js";
/**
  * funzione di inizializzazione dell'applicazione
 */
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
  
  // inizializza l'applicazione verificando se è presente un utente loggato
  checkLoggedUserOnInit();
  
}

// attende che il DOM sia completamente caricato e avvia l'inizializzazione tramite la funzione init
document.addEventListener("DOMContentLoaded", init);

import { showModal,showLoading,hideLoading } from "./utility.js";
import { showSection } from "./navigationHandlers.js";
import {
  loginForm,
  btnLogout,
  sectionLogin,
  setCurrentUserId,
  btnConfirmRegister,
  btnRegister,
  btnLogin
} from "./references.js";
import { updateBookingUIBasedOnRole } from "./utility.js";
import { loadAllBookings } from "./booking/bookingHandlers.js";

/**
  * funzione per verificare se è presente un utente loggato all'avvio dell'applicazione
 */
export async function checkLoggedUserOnInit() {

  console.log("Inizializzazione app...");
  try {
    showLoading();
    const response = await fetch("/current-user", {
      method: "GET",
      credentials: "include",
    });

    if (response.ok) {
      const userData = await response.json();

      setCurrentUserId(userData.id);
      sessionStorage.setItem("userRole", userData.role);

      showModal("Login effettuato", `Bentornato, ${userData.username}!`);

      updateBookingUIBasedOnRole(userData.role);
      loadAllBookings();

      btnLogin.style.display = "none";
      btnLogout.style.display = "inline-block";
      btnRegister.style.display = "none";
    } else {
      console.log("Sessione scaduta. Richiedere il login.");
    }
  } catch (error) {
    console.error("Errore durante il recupero dell'utente:", error);
  }finally {
    hideLoading(); 
  }
}
/**
  * funzione per gestire il login dell'utente, in caso di successo 
  * indirizza l'utente alla pagina di prenotazione inizializzando la pagina di prenotazione
 */
export function setupLoginHandler() {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const response = await fetch("login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // proprieta' necessaria per inviare i cookie al server
        credentials: "include",
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errMsg = await response.json();
        throw new Error(errMsg.error || "Errore durante il login");
      }

      const userData = await response.json();

      // Imposta l'utente corrente
      setCurrentUserId(userData.id);
      // salva il ruolo dell'utente in sessionStorage - storage persistente fino alla chiusura della finestra del browser
      sessionStorage.setItem("userRole", userData.role);

      showModal("Login effettuato", `Bentornato, ${userData.username}!`);

      // Mostra/nascondi elementi basati sul ruolo
      updateBookingUIBasedOnRole(userData.role);
      loadAllBookings();

      // Mostra il pulsante logout e nasconde il pulsante di registrazione
      btnLogin.style.display = "none";
      btnLogout.style.display = "inline-block";
      btnRegister.style.display = "none";
    } catch (error) {
      console.error("Errore durante il login:", error);
      showModal("Errore", `Login fallito: ${error.message}`);
    }
  });
}
/**
  * funzione per gestire il logout dell'utente. 
  * reinizzializza le variabili di sessione e indirizza l'utente alla pagina di login
  * 
*/
export function setupLogoutHandler() {
  console.log("btnLogout:", btnLogout); // log per verificare il riferimento
  if (!btnLogout) {
    console.error("Errore: btnLogout non trovato nel DOM.");
    return;
  }

  btnLogout.addEventListener("click", async () => {
    try {
      const response = await fetch("logout", {
        method: "POST",
        credentials: "include",
      });

      if (!response.ok) {
        const errMsg = await response.json();
        throw new Error(errMsg.error || "Errore durante il logout");
      }

      // mostra un messaggio di conferma logout
      showModal("Logout effettuato", "Sei stato disconnesso con successo.");
      sessionStorage.setItem("userRole", null);
      // Imposta l'utente corrente
      setCurrentUserId(null);

      // nascondi il pulsante logout
      btnLogout.style.display = "none";
      btnRegister.style.display = "inline-block";
      btnLogin.style.display = "inline-block";
      // mostra la sezione di login
      showSection(sectionLogin);
    } catch (error) {
      console.error("Errore durante il logout:", error);
      showModal("Errore", `Logout fallito: ${error.message}`);
    }
  });
}
/**
 * funzione per gestire la registrazione dell'utente
 */
export function setupRegisterHandler() {
  //form di registrazione

  btnConfirmRegister.addEventListener("click", async () => {
    const form = document.getElementById("register-form");
    if (!form.checkValidity()) {
      form.reportValidity();
      return;
    }
    const username = document.getElementById("registerUsername").value.trim();
    const email = document.getElementById("registerEmail").value.trim();
    const password = document.getElementById("registerPassword").value.trim();

    if (!username || !email || !password) {
      showModal("Errore", "Tutti i campi sono obbligatori!");
      return;
    }

    try {
      const response = await fetch("users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, email, password }),
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.error || "Errore durante la registrazione");
      }

      showModal(
        "Registrazione completata",
        "Registrazione avvenuta con successo! Ora puoi accedere."
      );
      document.getElementById("register-form").reset();
      const registerModal = bootstrap.Modal.getInstance(
        document.getElementById("registerModal")
      );
      registerModal.hide();
    } catch (error) {
      console.error("Errore durante la registrazione:", error);
      showModal("Errore", `Registrazione fallita: ${error.message}`);
    }
  });
}

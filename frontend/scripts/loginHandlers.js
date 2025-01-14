import { loginForm, btnLogout } from "./references.js";
import { showModal } from "./utility.js";
import { showSection } from "./navigationHandlers.js";
import { sectionBookings } from "./references.js";
import { loadAllBookings } from "./bookingHandlers.js";
import { setCurrentUserId } from "./references.js";


export function setupLoginHandler() {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        // invia automaticamente il cookie di sessione gestito nel backend al server
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

      showModal("Login effettuato", `Bentornato, ${userData.username}!`);
      // mostra il pulsante logout
      btnLogout.style.display = "inline-block";
      // naviga alla sezione prenotazioni
      await loadAllBookings();
      showSection(sectionBookings);
    } catch (error) {
      console.error("Errore durante il login:", error);
      showModal("Errore", `Login fallito: ${error.message}`);
    }
  });
}
export function setupLogoutHandler() {
  console.log("btnLogout:", btnLogout); // log per verificare il riferimento
  if (!btnLogout) {
    console.error("Errore: btnLogout non trovato nel DOM.");
    return;
  }

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

      // mostra un messaggio di conferma logout
      showModal("Logout effettuato", "Sei stato disconnesso con successo.");

      // nascondi il pulsante logout
      btnLogout.style.display = "none";

      // mostra la sezione di login
      showSection(sectionLogin);
    } catch (error) {
      console.error("Errore durante il logout:", error);
      showModal("Errore", `Logout fallito: ${error.message}`);
    }
  });
}

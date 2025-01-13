import { loginForm, btnLogout } from "./references.js";
import { showModal } from "./utility.js";
import { showSection } from "./navigationHandlers.js";
import { sectionBookings } from "./references.js";

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

      showModal("Login effettuato", `Bentornato, ${userData.username}!`);
      // mostra il pulsante logout
      btnLogout.style.display = "inline-block"; 
      // naviga alla sezione prenotazioni
      showSection(sectionBookings); 
    } catch (error) {
      console.error("Errore durante il login:", error);
      showModal("Errore", `Login fallito: ${error.message}`);
    }
  });
}
export function setupLogoutHandler() {
  const btnLogout = document.getElementById("btnLogout");
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

          showModal("Logout effettuato", "Sei stato disconnesso con successo.");
          btnLogout.style.display = "none"; 
          // naviga alla sezione login dopo il logout
          showSection(sectionLogin);
      } catch (error) {
          console.error("Errore durante il logout:", error);
          showModal("Errore", `Logout fallito: ${error.message}`);
      }
  });
}

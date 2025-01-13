import { loginForm, btnLogout, setCurrentUserId } from "./references.js";
import { showSection } from "./navigationHandlers.js";
import { loadAllBookings } from "./bookingHandlers.js";
import { sectionBookings } from "./references.js";
import { showModal, capitalizeFirstLetter } from "./utility.js";

export function setupLoginHandler() {
  loginForm.addEventListener("submit", async (e) => {
    e.preventDefault();

    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value.trim();

    try {
      console.log("Inviando POST /login");
      const response = await fetch("http://localhost:8000/login", {
        method: "POST",
        headers: {
          "Content-Type": "application/json"
        },
        // necessario per il funzionamento dei cookie/credenziali
        credentials: "include", 
        body: JSON.stringify({ username, password }),
      });
      console.log("Risposta ricevuta:", response);
      if (!response.ok) {
        const errMsg = await response.json();
        throw new Error(errMsg.error || "Login fallito");
      }

      const userData = await response.json();
      // userData = { id, username, email, role, message }

      setCurrentUserId(userData.id);
      showModal(
        `Login effettuato!`, `Bentornato, ${capitalizeFirstLetter(userData.username)}!`
      );

      btnLogout.style.display = "inline-block";
      showSection(sectionBookings);
      loadAllBookings();
    } catch (error) {
      console.error("Errore login:", error);
      showModal("Attenzione", `Errore nel login: ${error.message}`);
    }
  });
}

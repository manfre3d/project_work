import { loginForm, btnLogout, setCurrentUserId } from "./references.js";

import { showSection } from "./navigationHandlers.js";
import { loadAllBookings } from "./bookingHandlers.js";
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
        body: JSON.stringify({ username, password }),
      });

      if (!response.ok) {
        const errMsg = await response.json();
        throw new Error(errMsg.error || "Login fallito");
      }

      const userData = await response.json();
      // userData = { id, username, email, message }

      setCurrentUserId(userData.id);
      alert(
        `Login effettuato! Bentornato, ${userData.username} (ID=${userData.id})`
      );

      btnLogout.style.display = "inline-block";
      showSection(sectionBookings);
      loadAllBookings();
    } catch (error) {
      console.error("Errore login:", error);
      alert(`Errore nel login: ${error.message}`);
    }
  });
}

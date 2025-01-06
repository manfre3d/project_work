import {
  bookingListDiv,
  formNewBooking,
  currentUserId,
  setCurrentUserId,
} from "./references.js";

import { showSection } from "./navigationHandlers.js";
import { sectionLogin, sectionBookings } from "./references.js";

export async function loadAllBookings() {
  bookingListDiv.textContent = "Caricamento prenotazioni...";
  try {
    const response = await fetch("http://localhost:8000/bookings");
    if (!response.ok) {
      throw new Error("Errore nel recupero delle prenotazioni");
    }
    const bookings = await response.json();
    if (bookings.length === 0) {
      bookingListDiv.textContent = "Nessuna prenotazione trovata.";
      return;
    }
    bookingListDiv.innerHTML = "";
    const ul = document.createElement("ul");
    bookings.forEach((b) => {
      const li = document.createElement("li");
      li.textContent = `ID: ${b.id} - Cliente: ${b.customer_name} - Data: ${b.date} - Film: ${b.service} - user_id: ${b.user_id}`;
      ul.appendChild(li);
    });
    bookingListDiv.appendChild(ul);
  } catch (error) {
    bookingListDiv.textContent = "Errore caricamento prenotazioni";
    console.error(error);
  }
}

export function setupBookingHandler() {
  formNewBooking.addEventListener("submit", async (e) => {
    e.preventDefault();
    if (!currentUserId) {
      alert("Devi essere loggato per effettuare una prenotazione.");
      showSection(sectionLogin);
      return;
    }

    const customer_name = document.getElementById("customer_name").value.trim();
    const date = document.getElementById("date").value;
    const service = document.getElementById("service").value.trim();

    const newBooking = {
      customer_name,
      date,
      service,
      user_id: currentUserId,
    };

    try {
      const response = await fetch("http://localhost:8000/bookings", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(newBooking),
      });

      if (!response.ok) {
        const errorMsg = await response.json();
        throw new Error(
          errorMsg.error || "Errore nella creazione prenotazione"
        );
      }

      const created = await response.json();
      alert(`Prenotazione creata con ID=${created.id}`);

      // Puliamo il form e mostriamo la lista
      formNewBooking.reset();
      showSection(sectionBookings);
      loadAllBookings();
    } catch (error) {
      alert(`Errore: ${error.message}`);
      console.error("Errore POST prenotazione:", error);
    }
  });
}

// Riferimenti ai pulsanti
const btnLogin = document.getElementById("btn-login");
const btnLogout = document.getElementById("btn-logout");
const btnBookings = document.getElementById("btn-bookings");
const btnNewBooking = document.getElementById("btn-new-booking");

// Riferimenti alle sezioni
const sectionLogin = document.getElementById("section-login");
const sectionBookings = document.getElementById("section-bookings");
const sectionNewBooking = document.getElementById("section-new-booking");

// Altre variabili
const loginForm = document.getElementById("login-form");
const formNewBooking = document.getElementById("form-new-booking");
const bookingListDiv = document.getElementById("booking-list");

// userID loggato (semplificazione!)
let currentUserId = null;

// ------------------------------------------
// FUNZIONI DI NAVIGAZIONE
// ------------------------------------------
function showSection(section) {
  // nascondi tutte
  sectionLogin.classList.remove("active");
  sectionBookings.classList.remove("active");
  sectionNewBooking.classList.remove("active");
  // mostra la sezione selezionata
  section.classList.add("active");
}

// ------------------------------------------
// EVENT LISTENER PULSANTI NAV
// ------------------------------------------
btnLogin.addEventListener("click", () => {
  showSection(sectionLogin);
});

btnLogout.addEventListener("click", () => {
  currentUserId = null;
  alert("Logout effettuato");
  btnLogout.style.display = "none";
  // Torniamo alla sezione login
  showSection(sectionLogin);
});

btnBookings.addEventListener("click", () => {
  showSection(sectionBookings);
  loadAllBookings(); // carica e mostra tutte le prenotazioni
});

btnNewBooking.addEventListener("click", () => {
  // se non loggato, chiediamo login
  if (!currentUserId) {
    alert("Devi effettuare il login per prenotare!");
    showSection(sectionLogin);
    return;
  }
  showSection(sectionNewBooking);
});

// ------------------------------------------
// LOGIN FORM: POST /login
// ------------------------------------------
loginForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const username = document.getElementById("username").value.trim();
  const password = document.getElementById("password").value.trim();
  console.log(JSON.stringify({ username, password }))
  try {
    // Mandiamo la richiesta di login al server
    const response = await fetch("http://localhost:8000/login", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ username, password })
    });

    // Se il server risponde con un codice di errore (401, 400, ecc.)
    // lanciamo un'eccezione
    if (!response.ok) {
      const errMsg = await response.json();
      throw new Error(errMsg.error || "Login fallito");
    }

    // Se è ok, prendiamo i dati dell'utente
    const userData = await response.json();
    // userData dovrebbe contenere { id, username, email, message } o simile

    currentUserId = userData.id;
    alert(`Login effettuato! Bentornato, ${userData.username} (ID=${currentUserId})`);

    // Mostriamo il pulsante di logout
    btnLogout.style.display = "inline-block";

    // Passiamo alla sezione prenotazioni
    showSection(sectionBookings);
    loadAllBookings();
  } catch (error) {
    console.error("Errore login:", error);
    alert(`Errore nel login: ${error.message}`);
  }
});

// ------------------------------------------
// FUNZIONE PER CARICARE TUTTE LE PRENOTAZIONI
// ------------------------------------------
async function loadAllBookings() {
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
    // Mostra le prenotazioni
    bookingListDiv.innerHTML = "";
    const ul = document.createElement("ul");
    bookings.forEach(b => {
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

// ------------------------------------------
// CREAZIONE NUOVA PRENOTAZIONE (POST /bookings)
// ------------------------------------------
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
    user_id: currentUserId
  };

  try {
    const response = await fetch("http://localhost:8000/bookings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify(newBooking)
    });

    if (!response.ok) {
      const errorMsg = await response.json();
      throw new Error(errorMsg.error || "Errore nella creazione prenotazione");
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

// Alla partenza, mostriamo la sezione login
showSection(sectionLogin);

// script.js

// 1. Riferimenti a elementi HTML
const btnShowBookings = document.getElementById("btn-show-bookings");
const btnNewBooking = document.getElementById("btn-new-booking");
const sectionBookings = document.getElementById("section-bookings");
const sectionNewBooking = document.getElementById("section-new-booking");
const bookingsListDiv = document.getElementById("bookings-list");
const formNewBooking = document.getElementById("form-new-booking");

// Se gestisci anche utenti:
const btnShowUsers = document.getElementById("btn-show-users");
const btnNewUser = document.getElementById("btn-new-user");
const sectionUsers = document.getElementById("section-users");
const sectionNewUser = document.getElementById("section-new-user");
const usersListDiv = document.getElementById("users-list");
const formNewUser = document.getElementById("form-new-user");

// 2. Funzioni di "navigazione" (mostra/nascondi sezioni)
function showSection(section) {
  // Nascondi tutte
  sectionBookings.style.display = "none";
  sectionNewBooking.style.display = "none";
  sectionUsers.style.display = "none";
  sectionNewUser.style.display = "none";

  // Mostra solo la sezione che ci interessa
  section.style.display = "block";
}

// 3. Event listener
btnShowBookings.addEventListener("click", () => {
  showSection(sectionBookings);
  getAllBookings(); // carica le prenotazioni dal server
});

btnNewBooking.addEventListener("click", () => {
  showSection(sectionNewBooking);
});

if (btnShowUsers) {
  btnShowUsers.addEventListener("click", () => {
    showSection(sectionUsers);
    getAllUsers(); // carica gli utenti dal server
  });
}

if (btnNewUser) {
  btnNewUser.addEventListener("click", () => {
    showSection(sectionNewUser);
  });
}

// 4. Funzione per ottenere tutte le prenotazioni (GET /bookings)
async function getAllBookings() {
  try {
    const response = await fetch("http://localhost:8000/bookings");
    if (!response.ok) {
      throw new Error(`Errore server: ${response.status}`);
    }
    const bookings = await response.json();

    // Puliamo il contenitore
    bookingsListDiv.innerHTML = "";

    // Creiamo un elenco o una tabella
    if (bookings.length === 0) {
      bookingsListDiv.textContent = "Nessuna prenotazione trovata.";
      return;
    }

    const ul = document.createElement("ul");
    for (const booking of bookings) {
      const li = document.createElement("li");
      li.textContent = `ID: ${booking.id}, Cliente: ${booking.customer_name}, Data: ${booking.date}, Servizio: ${booking.service}`;
      ul.appendChild(li);
    }
    bookingsListDiv.appendChild(ul);
  } catch (error) {
    console.error("Errore fetch prenotazioni:", error);
    bookingsListDiv.textContent = "Errore nel caricamento prenotazioni.";
  }
}

// 5. Gestione del form di nuova prenotazione (POST /bookings)
formNewBooking.addEventListener("submit", async (e) => {
  e.preventDefault();

  // Ottieni i valori
  const customer_name = document.getElementById("customer_name").value.trim();
  const date = document.getElementById("date").value;
  const service = document.getElementById("service").value.trim();

  // Invia i dati al server
  try {
    const response = await fetch("http://localhost:8000/bookings", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ customer_name, date, service }),
    });

    if (!response.ok) {
      throw new Error(`Errore server: ${response.status}`);
    }

    const createdBooking = await response.json();
    alert(`Prenotazione creata con ID: ${createdBooking.id}`);

    // Resetta form e mostra la lista
    formNewBooking.reset();
    showSection(sectionBookings);
    getAllBookings();
  } catch (error) {
    console.error("Errore creazione prenotazione:", error);
    alert("Si è verificato un errore durante la creazione della prenotazione.");
  }
});

// -- Se gestisci anche gli utenti, analogamente: ----

// Funzione per ottenere tutti gli utenti
async function getAllUsers() {
  try {
    const response = await fetch("http://localhost:8000/users");
    if (!response.ok) {
      throw new Error(`Errore server: ${response.status}`);
    }
    const users = await response.json();

    usersListDiv.innerHTML = "";

    if (users.length === 0) {
      usersListDiv.textContent = "Nessun utente trovato.";
      return;
    }

    const ul = document.createElement("ul");
    for (const user of users) {
      // Attenzione: in un progetto reale non si mostrerebbe la password
      const li = document.createElement("li");
      li.textContent = `ID: ${user.id}, Username: ${user.username}, Email: ${user.email}`;
      ul.appendChild(li);
    }
    usersListDiv.appendChild(ul);
  } catch (error) {
    console.error("Errore fetch utenti:", error);
    usersListDiv.textContent = "Errore nel caricamento utenti.";
  }
}

// Form di nuovo utente
if (formNewUser) {
  formNewUser.addEventListener("submit", async (e) => {
    e.preventDefault();
    const username = document.getElementById("username").value.trim();
    const password = document.getElementById("password").value;
    const email = document.getElementById("email").value.trim();

    try {
      const response = await fetch("http://localhost:8000/users", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ username, password, email }),
      });

      if (!response.ok) {
        throw new Error(`Errore server: ${response.status}`);
      }

      const createdUser = await response.json();
      alert(`Utente creato con ID: ${createdUser.id}`);
      formNewUser.reset();
      showSection(sectionUsers);
      getAllUsers();
    } catch (error) {
      console.error("Errore creazione utente:", error);
      alert("Si è verificato un errore durante la creazione dell'utente.");
    }
  });
}

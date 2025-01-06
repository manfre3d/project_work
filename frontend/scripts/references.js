// Riferimenti ai pulsanti
export const btnLogin = document.getElementById("btn-login");
export const btnLogout = document.getElementById("btn-logout");
export const btnBookings = document.getElementById("btn-bookings");
export const btnNewBooking = document.getElementById("btn-new-booking");

// Riferimenti alle sezioni
export const sectionLogin = document.getElementById("section-login");
export const sectionBookings = document.getElementById("section-bookings");
export const sectionNewBooking = document.getElementById("section-new-booking");

// Altre variabili
export const loginForm = document.getElementById("login-form");
export const formNewBooking = document.getElementById("form-new-booking");
export const bookingListDiv = document.getElementById("booking-list");

// Variabile globale (per ID utente loggato)
export let currentUserId = null;

// Funzione per settare l'ID utente da altri file
export function setCurrentUserId(id) {
  currentUserId = id;
}
// Seleziona gli elementi HTML interni alla modale
export const modalTitleEl = document.getElementById("modalTitle");
export const modalBodyEl = document.getElementById("modalBody");





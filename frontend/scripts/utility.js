import { modalTitleEl, modalBodyEl } from "./references.js";
import { sectionBookings, sectionAdminBooking } from "./references.js";
import { showSection } from "./navigationHandlers.js";

export function showModal(title, message) {
  modalTitleEl.textContent = title;
  modalBodyEl.textContent = message;

  const modalEl = document.getElementById("myModal");
  const modal = new bootstrap.Modal(modalEl);

  modalEl.setAttribute("aria-hidden", "false");

  setTimeout(() => {
    modal.show();

    modalEl.querySelector("button").focus();
  }, 10);

  modalEl.addEventListener("hidden.bs.modal", () => {
    modalEl.setAttribute("aria-hidden", "true");
    document.getElementById("main-content").focus();
  });
}
export function updateBookingUIBasedOnRole(role) {
  if (role === "admin") {
    showSection(sectionAdminBooking);
  } else if (role === "user") {
    showSection(sectionBookings);
  }
}
export function calculateTotalPrice(startDate, endDate, pricePerDay) {
  if (!startDate || !endDate || !pricePerDay) return 0;

  const start = new Date(startDate);
  const end = new Date(endDate);

  // giorni, includendo il giorno iniziale
  const millisecondsPerDay = 1000 * 60 * 60 * 24;
  const days = Math.floor((end - start) / millisecondsPerDay) + 1;

  return days > 0 ? days * pricePerDay : 0;
}
export function showLoading() {
  const loadingScreen = document.getElementById("loading-screen");
  loadingScreen.classList.remove("hidden");
}
export function hideLoading() {
  const loadingScreen = document.getElementById("loading-screen");
  loadingScreen.classList.add("hidden");
}


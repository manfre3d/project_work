import { modalTitleEl, modalBodyEl } from "./references.js";

import {
  sectionBookings,
  sectionAdminBooking
} from "./references.js";
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


export function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}

export function updateBookingUIBasedOnRole(role) {

  // sectionAdminBooking
  // const adminOnlyElements = document.querySelectorAll(".admin-only");
  // const userOnlyElements = document.querySelectorAll(".user-only");

  if (role === "admin") {
    // adminOnlyElements.forEach((el) => (el.style.display = "block"));
    // userOnlyElements.forEach((el) => (el.style.display = "none"));
    showSection(sectionAdminBooking);
  } else if (role === "user") {
    // adminOnlyElements.forEach((el) => (el.style.display = "none"));
    // userOnlyElements.forEach((el) => (el.style.display = "block"));
    showSection(sectionBookings);
  }
}
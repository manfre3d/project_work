import { modalTitleEl, modalBodyEl } from "./references.js";


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
  });
}


export function capitalizeFirstLetter(string) {
  return string.charAt(0).toUpperCase() + string.slice(1);
}
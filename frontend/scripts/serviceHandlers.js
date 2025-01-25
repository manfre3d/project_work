async function getServices() {
  const response = await fetch("services", { method: "GET", credentials: "include" });
  if (!response.ok) {
    const errMsg = await response.json();
    throw new Error(errMsg.error || "Errore nel caricamento dei servizi");
  }
  return response.json();
}


/**
  * recupera i servizi dal server 
 */
export async function loadServices() {

  try {
    const services = await getServices();

    const editAdminServiceSelect = document.getElementById("editAdminService");
    editAdminServiceSelect.innerHTML = "";

    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id;
      option.dataset.price = service.price;
      option.textContent = service.name;
      editAdminServiceSelect.appendChild(option);
    });

    const editServiceSelect = document.getElementById("editService");
    if (editServiceSelect) {
      editServiceSelect.innerHTML = ""; // Svuota le opzioni esistenti

      services.forEach((service) => {
        const option = document.createElement("option");
        option.value = service.id;
        option.textContent = service.name;
        option.dataset.price = service.price;
        editServiceSelect.appendChild(option);
      });
    }
  } catch (error) {
    console.error("Errore nel caricamento dei servizi:", error);
    showModal("Errore", `Impossibile caricare i servizi: ${error.message}`);
  }
}
/**
 * recupera i servizi dal server e popola le liste/select
 */
export async function populateServicesDropdown() {
  try {
    const services = await getServices();
    const serviceSelect = document.getElementById("service");
    serviceSelect.innerHTML = "";

    services.forEach((service) => {
      const option = document.createElement("option");
      option.value = service.id;
      option.textContent = `${service.name} - ${service.description}`;
      option.dataset.price = service.price;
      serviceSelect.appendChild(option);
    });
  } catch (error) {
    console.error("Errore nel caricamento dei servizi:", error);
    showModal("Errore", `Impossibile caricare i servizi: ${error.message}`);
  }
}

document.addEventListener("DOMContentLoaded", function () {
  fetchObjectsStatus();

  function fetchObjectsStatus() {
    fetch("http://4.206.210.212/objects/status")
      .then((response) => response.json())
      .then((data) => populateTable(data))
      .catch((error) => {
        console.log("Erreur fetchObjectsStatus", error);
      });
  }

  function populateTable(objects) {
    const tableBody = document.getElementById("data-rows");
    tableBody.innerHTML = "";
    objects.forEach((object) => {
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${object.id_objet}</td>
        <td>${object.nom_objet}</td>
        <td>${object.local_objet}</td>
        <td>${object.is_localisation ? "Enabled" : "Disabled"}</td>
        <td><button onclick="enableLocalization(${
          object.id_objet
        })">Enable Localization</button></td>
      `;
      tableBody.appendChild(row);
    });
  }
});

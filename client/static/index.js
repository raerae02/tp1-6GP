document.addEventListener("DOMContentLoaded", function () {
  fetchObjectsStatus();

  function fetchObjectsStatus() {
    fetch("http://4.206.210.212:5000/objets/status")
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          populateTable(data.objets);
        } else {
          console.log("Data fetch unsuccessful");
        }
      })
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
        <td>${object[0]}</td>
        <td>${object[1]}</td>
        <td>${object[2]}</td>
        <td>${object[3] ? "Enabled" : "Disabled"}</td>
        <td><button onclick="enableLocalization(${
          object[0]
        })">Enable Localization</button></td>
      `;
      tableBody.appendChild(row);
    });
  }
});

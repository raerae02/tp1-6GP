document.addEventListener("DOMContentLoaded", function () {
  fetchObjectsStatus();
  fetchObjectsStats();
  updateClock();
  setInterval(updateClock, 1000);

  function updateClock() {
    const clockElement = document.getElementById("clock");

    if (clockElement) {
      const now = new Date();
      const hours = String(now.getHours()).padStart(2, "0");
      const minutes = String(now.getMinutes()).padStart(2, "0");
      const seconds = String(now.getSeconds()).padStart(2, "0");
      clockElement.textContent = `${hours}:${minutes}:${seconds}`;
    }
  }

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

  function fetchObjectsStats() {
    fetch("http://4.206.210.212:5000/get-stats")
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          populateTable(data.stats);
        } else {
          console.log("Data fetch unsuccessful");
        }
      })
      .catch((error) => {
        console.log("Erreur fetchObjectsStats", error);
      });
  }

  window.fetchVideos = function (id_objet) {
    fetch(`http://4.206.210.212:5000/get-videos/${id_objet}`)
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          displayVideos(data.videos);
        } else {
          console.log("Failed to fetch videos");
        }
      })
      .catch((error) => {
        console.log("Error fetching videos:", error);
      });
  };

  function displayVideos(videos) {
    const videosList = document.getElementById("videos-list");
    videosList.innerHTML = "";
    videos.forEach((video) => {
      const listItem = document.createElement("li");
      listItem.textContent = `Video ID: ${video.id_video}, Nom: ${video.nom_video}`;
      videosList.appendChild(listItem);
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
        <td>${object.nb_jouer_total || 0}</td>
        <td>${object.temps_total || 0} seconds</td>
        <td>
          <button onclick="sendCommand(${
            object.id_objet
          }, 'next_video')">Prochain video</button>
          <button onclick="sendCommand(${
            object.id_objet
          }, 'stop_video')">Arreter videos</button>
          <button onclick="sendCommand(${
            object.id_objet
          }, 'start_video')">Demarrer videos</button>
          <button onclick="sendCommand(${
            object.id_objet
          }, 'localise')">Activer Localization</button>
          <button onclick="fetchVideos(${object.id_objet})">Voir Videos</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  }

  window.sendCommand = function (id_objet, command) {
    fetch(`http://4.206.210.212:5000/send_command/${id_objet}`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ command: command }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          console.log(
            `Command '${command}' executed successfully for object ${id_objet}`
          );
        } else {
          console.log(
            `Failed to execute command '${command}' for object ${id_objet}`
          );
        }
      })
      .catch((error) => {
        console.log("Error sending command:", error);
      });
  };
});

function uploadVideo() {
  const fileInput = document.getElementById("video-upload");
  const file = fileInput.files[0];

  if (!file) {
    alert("Veuillez sélectionner un fichier.");
    return;
  }

  const formData = new FormData();
  formData.append("video", file);

  fetch("http://4.206.210.212:5000/upload_video", {
    method: "POST",
    body: formData,
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.success) {
        alert("Vidéo uploadée avec succès.");
      } else {
        alert("Erreur lors de l'upload de la vidéo.");
      }
    })
    .catch((error) => {
      console.error("Erreur lors de l'upload de la vidéo:", error);
      alert("Une erreur est survenue lors de l'upload de la vidéo.");
    });
}

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
      const deleteButton = document.createElement("button");
      deleteButton.textContent = "X";
      deleteButton.onclick = () => supprimerVideo(video.id_video);
      listItem.textContent = `Video ID: ${video.id_video}, Nom: ${video.nom_video}`;
      videosList.appendChild(listItem);
    });
  }

  function populateTable(objects) {
    const tableBody = document.getElementById("data-rows");
    tableBody.innerHTML = "";
    objects.forEach((object) => {
      const fileInputId = `video-upload-${object.id_objet}`;
      const row = document.createElement("tr");
      row.innerHTML = `
        <td>${object.id_objet}</td>
        <td>${object.nom_objet}</td>
        <td>${object.local_objet}</td>
        <td>${object.is_localisation ? "Enabled" : "Disabled"}</td>
        <td>${object.nb_jouer_total || 0}</td>
        <td>${object.temps_total || 0} seconds</td>
        <td>
        <button onclick="activerLocalisation(${object.id_objet}, ${
        object.is_localisation ? 0 : 1
      })">Toggle Localisation</button>
          <button onclick="fetchVideos(${object.id_objet})">Voir Videos</button>
          <input type="file" id="${fileInputId}" style="display: none;" accept="video/*" onchange="uploadVideo(${
        object.id_objet
      }, '${fileInputId}')">
          <button onclick="document.getElementById('${fileInputId}').click()">Telecharger Video</button>
        </td>
      `;
      tableBody.appendChild(row);
    });
  }

  window.activerLocalisation = function (id_objet, localisation) {
    fetch(`http://4.206.210.212:5000/activate-localisation`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        id_objet: id_objet,
        localisation: localisation,
      }),
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert(
            `Localisation ${
              localisation ? "activated" : "deactivated"
            } successfully.`
          );
        } else {
          alert("Error: " + data.message);
        }
      })
      .catch((error) => {
        console.error("Error activating localisation:", error);
        alert("An error occurred while activating localisation.");
      });
  };
  window.uploadVideo = function (id_objet, inputId) {
    const fileInput = document.getElementById(inputId);
    const file = fileInput.files[0];

    if (!file) {
      alert("Veuillez sélectionner un fichier.");
      return;
    }

    const formData = new FormData();
    formData.append("video", file);
    formData.append("id_objet", id_objet);

    fetch("http://4.206.210.212:5000/upload_video", {
      method: "POST",
      body: formData,
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Vidéo téléchargée avec succès.");
          fileInput.value = "";
        } else {
          alert("Erreur lors de l'upload de la vidéo.");
        }
      })
      .catch((error) => {
        console.error("Erreur lors de l'upload de la vidéo:", error);
        alert("Une erreur est survenue lors de l'upload de la vidéo.");
      });
  };
  window.supprimerVideo = function (id_video) {
    fetch(`http://4.206.210.212:5000/delete-video/${id_video}`, {
      method: "DELETE",
    })
      .then((response) => response.json())
      .then((data) => {
        if (data.success) {
          alert("Vidéo supprimée avec succès.");
          fetchObjectsStatus();
        } else {
          alert("Erreur lors de la suppression de la vidéo.");
        }
      })
      .catch((error) => {
        console.error("Erreur lors de la suppression de la vidéo:", error);
        alert("Une erreur est survenue lors de la suppression de la vidéo.");
      });
  };
});

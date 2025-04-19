let valeur = 0;
const compteur = document.getElementById('compteur');

// Ajoute 190 chaque seconde
setInterval(() => {
  valeur += 19;
  compteur.textContent = valeur;
}, 100);


const videos = document.querySelectorAll(".myVideo");

videos.forEach(video => {
  video.addEventListener("timeupdate", () => {
    if (video.currentTime >= 30) {
      video.currentTime = 0
      video.play();  // Arrêter la vidéo après 30 secondes
    }
  });
});

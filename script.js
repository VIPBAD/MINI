const urlParams = new URLSearchParams(window.location.search);
const audioSrc = decodeURIComponent(urlParams.get('audio') || '');
const thumb = decodeURIComponent(urlParams.get('thumb') || '');
const title = decodeURIComponent(urlParams.get('title') || 'Unknown Title');

const audio = document.getElementById('audio');
const seek = document.getElementById('seek');
const currentTime = document.getElementById('current');
const totalTime = document.getElementById('total');
const favBtn = document.getElementById('favBtn');

let stopped = false;

document.getElementById('thumb').src = thumb;
document.getElementById('title').innerText = title;
document.getElementById('artist').innerText = 'Now Playing...';

audio.src = audioSrc;
audio.autoplay = true;
audio.loop = false;

audio.addEventListener('loadedmetadata', () => {
  totalTime.innerText = formatTime(audio.duration);
  tryAutoPlay();
});

audio.addEventListener('timeupdate', () => {
  seek.value = (audio.currentTime / audio.duration) * 100;
  currentTime.innerText = formatTime(audio.currentTime);
});

seek.addEventListener('input', () => {
  audio.currentTime = (seek.value / 100) * audio.duration;
});

function tryAutoPlay() {
  if (!stopped) {
    audio.play().catch(err => {
      console.warn("Autoplay blocked:", err);
    });
  }
}

function togglePlay() {
  if (stopped) return;
  if (audio.paused) audio.play();
  else audio.pause();
}

function stopAudio() {
  audio.pause();
  audio.currentTime = 0;
  stopped = true;
}

function endPlayer() {
  stopAudio();
  alert("🔕 Playback ended. Play a new song from Telegram.");
}

function rewind() {
  if (!stopped) audio.currentTime = Math.max(0, audio.currentTime - 10);
}

function forward() {
  if (!stopped) audio.currentTime = Math.min(audio.duration, audio.currentTime + 10);
}

function toggleFav() {
  favBtn.textContent = favBtn.textContent === '❤️' ? '🤍' : '❤️';
}

function formatTime(sec) {
  const m = Math.floor(sec / 60);
  const s = Math.floor(sec % 60);
  return `${m}:${s < 10 ? '0' + s : s}`;
}
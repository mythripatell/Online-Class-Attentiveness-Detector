const video = document.getElementById('webcam');
const statusBox = document.getElementById('statusBox');

async function initWebcam() {
  if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
    statusBox.innerText = 'Webcam not supported on this browser.';
    console.error('Webcam not supported');
    return;
  }

  try {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true });
    video.srcObject = stream;
    statusBox.innerText = 'Detecting...';
  } catch (error) {
    if (error.name === 'NotAllowedError') {
      statusBox.innerText = 'Permission denied. Please allow webcam access.';
    } else if (error.name === 'NotFoundError') {
      statusBox.innerText = 'No webcam device found.';
    } else {
      statusBox.innerText = 'Webcam access denied or unavailable.';
    }
    console.error('Webcam error:', error);
  }
}

initWebcam();
edu.js


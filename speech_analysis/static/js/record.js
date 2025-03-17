let mediaRecorder;
let audioChunks = [];

document.getElementById('start-btn').addEventListener('click', async () => {
    const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
    mediaRecorder = new MediaRecorder(stream);

    audioChunks = [];
    mediaRecorder.ondataavailable = event => {
        audioChunks.push(event.data);
    };

    mediaRecorder.onstop = () => {
        const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
        const audioUrl = URL.createObjectURL(audioBlob);
        const audio = document.getElementById('audio-playback');
        audio.src = audioUrl;

        // Send audio to the backend
        const formData = new FormData();
        formData.append('audio', audioBlob);
        fetch('/record/', {
            method: 'POST',
            body: formData
        })
        .then(response => response.json())
        .then(data => console.log(data))
        .catch(error => console.error('Error:', error));
    };

    mediaRecorder.start();
    document.getElementById('start-btn').disabled = true;
    document.getElementById('stop-btn').disabled = false;
});

document.getElementById('stop-btn').addEventListener('click', () => {
    mediaRecorder.stop();
    document.getElementById('start-btn').disabled = false;
    document.getElementById('stop-btn').disabled = true;
});

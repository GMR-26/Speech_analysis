let mediaRecorder;
let audioChunks = [];

// Event listener for the "Start Recording" button
document.getElementById('start-btn').addEventListener('click', async () => {
    try {
        console.log("Start Recording button clicked");

        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        mediaRecorder = new MediaRecorder(stream);
        console.log("Microphone access granted");

        audioChunks = [];
        mediaRecorder.ondataavailable = event => {
            console.log("Audio chunk received:", event.data);
            audioChunks.push(event.data);
        };

        // Handle the stopping of the recording
        mediaRecorder.onstop = () => {
            console.log("Recording stopped");

            // Create a Blob from the recorded audio chunks
            const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
            console.log("Audio Blob:", audioBlob);

            // Create an audio URL for playback
            const audioUrl = URL.createObjectURL(audioBlob);
            const audio = document.getElementById('audio-playback');
            audio.src = audioUrl;

            console.log("Sending audio to the backend...");

            // Prepare the FormData to send the audio file
            const formData = new FormData();
            formData.append('audio', audioBlob);
            console.log("FormData audio file:", formData.get('audio'));

            // Get the CSRF token from the meta tag in the HTML
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');

            // Send the audio file to the backend
            fetch('/record/', {
                method: 'POST',
                headers: {
                    'X-CSRFToken': csrfToken, // Include the CSRF token
                },
                body: formData
            })
            .then(response => response.json())
            .then(data => {
                console.log("Response from server:", data);

                // If the response includes the spectrogram URL, display it
                if (data.spectrogram_url) {
                    const spectrogramImg = document.createElement('img');
                    spectrogramImg.src = data.spectrogram_url;
                    spectrogramImg.alt = "Spectrogram";
                    spectrogramImg.style.marginTop = "20px"; // Add some spacing
                    document.body.appendChild(spectrogramImg);
                } else {
                    console.error("No spectrogram URL found in the response.");
                    alert("Spectrogram not found. Please check the backend process.");
                }
            })
            .catch(async (error) => {
                console.error("Error while sending audio:", error);

                // Log raw response if available for debugging
                const rawResponse = await error.response?.text();
                console.error("Raw server response:", rawResponse);
                alert("An error occurred while processing the audio. Please check the backend logs.");
            });
        };

        // Start the recording process
        mediaRecorder.start();
        console.log("Recording started");

        // Disable the "Start Recording" button and enable the "Stop Recording" button
        document.getElementById('start-btn').disabled = true;
        document.getElementById('stop-btn').disabled = false;

    } catch (error) {
        console.error("Error accessing microphone or recording audio:", error);
        alert("Microphone access is required for recording.");
    }
});

// Event listener for the "Stop Recording" button
document.getElementById('stop-btn').addEventListener('click', () => {
    console.log("Stop Recording button clicked");

    if (mediaRecorder) {
        mediaRecorder.stop();
        console.log("MediaRecorder stopped");
    }

    // Re-enable the "Start Recording" button and disable the "Stop Recording" button
    document.getElementById('start-btn').disabled = false;
    document.getElementById('stop-btn').disabled = true;
});

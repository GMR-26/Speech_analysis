let mediaRecorder;
let audioChunks = [];
let audioContext;
let sourceNode;
let scriptProcessorNode;

// Event listener for the "Start Recording" button
document.getElementById('start-btn').addEventListener('click', async () => {
    try {
        console.log("Start Recording button clicked");

        // Request microphone access
        const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
        audioContext = new AudioContext();

        // Create a MediaStreamAudioSourceNode from the microphone stream
        sourceNode = audioContext.createMediaStreamSource(stream);

        // Create a ScriptProcessorNode to process audio and convert it to 16-bit
        scriptProcessorNode = audioContext.createScriptProcessor(4096, 1, 1);
        scriptProcessorNode.onaudioprocess = (event) => {
            const inputBuffer = event.inputBuffer;
            const outputBuffer = event.outputBuffer;

            // Process the audio data (convert to 16-bit)
            for (let channel = 0; channel < inputBuffer.numberOfChannels; channel++) {
                const inputData = inputBuffer.getChannelData(channel);
                const outputData = outputBuffer.getChannelData(channel);

                // Convert 32-bit float to 16-bit PCM
                for (let i = 0; i < inputData.length; i++) {
                    const sample = inputData[i];
                    outputData[i] = Math.max(-1, Math.min(1, sample)); // Clamp to [-1, 1]
                }
            }
        };

        // Connect the nodes: source -> scriptProcessor -> destination
        sourceNode.connect(scriptProcessorNode);
        scriptProcessorNode.connect(audioContext.destination);

        // Create a MediaRecorder to record the processed audio
        mediaRecorder = new MediaRecorder(stream);
        console.log("Microphone access granted");

        audioChunks = [];
        mediaRecorder.ondataavailable = (event) => {
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

            // Enable the "Analyze" button
            document.getElementById('analyze-btn').disabled = false;
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

        // Disconnect the audio nodes to stop processing
        if (sourceNode && scriptProcessorNode) {
            sourceNode.disconnect(scriptProcessorNode);
            scriptProcessorNode.disconnect(audioContext.destination);
        }
    }

    // Re-enable the "Start Recording" button and disable the "Stop Recording" button
    document.getElementById('start-btn').disabled = false;
    document.getElementById('stop-btn').disabled = true;
});

// Event listener for the "Analyze" button
document.getElementById('analyze-btn').addEventListener('click', () => {
    console.log("Analyze button clicked");

    // Check if audioChunks is not empty
    if (audioChunks.length === 0) {
        console.error("No audio data recorded.");
        alert("No audio data recorded. Please record audio first.");
        return;
    }

    // Create a Blob from the recorded audio chunks
    const audioBlob = new Blob(audioChunks, { type: 'audio/wav' });
    console.log("Audio Blob:", audioBlob);

    // Prepare the FormData to send the audio file
    const formData = new FormData();
    formData.append('audio', audioBlob, 'recorded_audio.wav'); // Add a filename
    console.log("FormData audio file:", formData.get('audio'));

    // Get the CSRF token from the meta tag in the HTML
    const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
    console.log("CSRF Token:", csrfToken);

    // Send the audio file to the backend
    fetch('/record/', {
        method: 'POST',
        headers: {
            'X-CSRFToken': csrfToken, // Include the CSRF token
        },
        body: formData,
    })
        .then((response) => {
            console.log("Response status:", response.status);
            if (response.redirected) {
                // Redirect to the display page
                console.log("Redirecting to:", response.url);
                window.location.href = response.url;
            } else {
                return response.json();
            }
        })
        .then((data) => {
            if (data) {
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
            }
        })
        .catch(async (error) => {
            console.error("Error while sending audio:", error);

            // Log raw response if available for debugging
            const rawResponse = await error.response?.text();
            console.error("Raw server response:", rawResponse);
            alert("An error occurred while processing the audio. Please check the backend logs.");
        });
});
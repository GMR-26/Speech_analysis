from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
import os
from pydub import AudioSegment
import uuid  # For unique filenames
from google.cloud import speech
import matplotlib
matplotlib.use('Agg')  # Non-GUI backend
import matplotlib.pyplot as plt
import numpy as np
import speech_recognition as sr
from django.views.decorators.csrf import csrf_exempt
from .forms import AudioFileForm
from pydub import AudioSegment

# Ensure the uploads directory exists
UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    print("Created global 'uploads' directory")


def index(request):
    return render(request, 'index.html')

from django.shortcuts import render, redirect
from .forms import AudioFileForm  # Ensure the form is imported

def upload(request):
    if request.method == 'POST':
        form = AudioFileForm(request.POST, request.FILES)  # Ensure files are included
        if form.is_valid():
            audio_file = form.cleaned_data['audio_file']  # Get the actual file object
            file_path = save_audio_file(audio_file)  # Pass the file object, not a string
            mono_file_path = convert_to_mono(file_path)  # Process the saved file
            transcription = transcribe_speech(mono_file_path)  # Transcribe
            generate_spectrogram(mono_file_path)  # Generate the spectrogram
            return redirect('display', filename=os.path.basename(mono_file_path))
    else:
        form = AudioFileForm()
    return render(request, 'upload.html', {'form': form})

def record(request):
    return render(request, 'analysis/record.html')


def record_page(request):
    return render(request, 'analysis/record.html')


@csrf_exempt
def record_audio(request):
    if request.method == 'POST':
        try:
            print("POST request received")
            print(f"request.FILES: {request.FILES}")

            # Ensure 'uploads/' directory exists
            if not os.path.exists('uploads'):
                os.makedirs('uploads')
                print("Created 'uploads' directory")

            # Get the audio file
            audio_file = request.FILES.get('audio')
            if not audio_file:
                print("No 'audio' file found in request.FILES")
                return JsonResponse({'error': 'No audio file provided'}, status=400)

            # Save the audio file
            save_path = os.path.join('uploads', 'recorded_audio.wav')
            print(f"Saving file to: {save_path}")
            with open(save_path, 'wb+') as destination:
                for chunk in audio_file.chunks():
                    destination.write(chunk)
            print(f"File successfully saved at: {save_path}")

            # Further processing: Convert to mono, generate spectrogram
            mono_file_path = convert_to_mono(save_path)
            print(f"Mono file created at: {mono_file_path}")
            spectrogram_path = generate_spectrogram(mono_file_path)
            print(f"Spectrogram created at: {spectrogram_path}")

            # Redirect to the display page
            filename = os.path.basename(mono_file_path)
            return redirect('display', filename=filename)

        except Exception as e:
            print(f"Error processing audio: {e}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    else:
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request'}, status=400)

def display(request, filename):
    spectrogram_url = f'/static/spectrograms/{filename}.png'
    return render(request, 'display.html', {'spectrogram_url': spectrogram_url})


def save_audio_file(file):
    upload_dir = 'uploads'

    # Ensure the uploads directory exists
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
        print("Created 'uploads' directory")

    # Generate a unique filename
    file_name = f"{uuid.uuid4()}_{file.name}"
    file_path = os.path.join(upload_dir, file_name)

    # Save the file
    with open(file_path, 'wb+') as dest:
        for chunk in file.chunks():  # Correctly handle chunks of the file
            dest.write(chunk)

    print(f"File saved at: {file_path}")
    return file_path

def convert_to_mono(file_path):
    sound = AudioSegment.from_file(file_path)
    sound = sound.set_channels(1)
    sound=sound.set_sample_width(2)
    mono_file_path = file_path.replace(".wav", "_mono_16bit.wav")
    sound.export(mono_file_path, format="wav")
    return mono_file_path


def transcribe_speech(file_path):
    client = speech.SpeechClient()
    with open(file_path, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        language_code='en-US'
    )

    response = client.recognize(config=config, audio=audio)
    transcription = ''
    for result in response.results:
        transcription += result.alternatives[0].transcript

    return transcription


def generate_spectrogram(file_path):
    recognizer = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = recognizer.record(source)

    audio_data = np.frombuffer(audio.get_raw_data(), np.int16)

    plt.specgram(audio_data, NFFT=1024, Fs=16000, noverlap=900)
    plt.xlabel('Time')
    plt.ylabel('Frequency')
    plt.title('Spectrogram')

    # Define the directory and ensure it exists
    spectrogram_dir = os.path.join('static', 'spectrograms')
    if not os.path.exists(spectrogram_dir):
        os.makedirs(spectrogram_dir)  # Create the directory

    # Save the spectrogram
    spectrogram_path = os.path.join(spectrogram_dir, f'{os.path.basename(file_path)}.png')
    plt.savefig(spectrogram_path)
    plt.close()
    return spectrogram_path

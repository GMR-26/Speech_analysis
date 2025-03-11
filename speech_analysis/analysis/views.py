from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from .forms import AudioFileForm
from google.cloud import speech
import matplotlib.pyplot as plt
import numpy as np
import speech_recognition as sr

def index(request):
    return render(request, 'index.html')

def upload(request):
    if request.method == 'POST':
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['audio_file']
            file_path = save_audio_file(file)
            transcription = transcribe_speech(file_path)
            generate_spectrogram(file_path)
            return redirect('display', filename=os.path.basename(file_path))
    else:
        form = AudioFileForm()
    return render(request, 'upload.html', {'form': form})

def record(request):
    # This is a placeholder for the record functionality
    return HttpResponse("Recording feature is under development.")

def display(request, filename):
    spectrogram_url = f'/static/spectrograms/{filename}.png'
    return render(request, 'display.html', {'spectrogram_url': spectrogram_url})

def save_audio_file(file):
    upload_dir = 'uploads'
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir)
    file_path = os.path.join(upload_dir, file.name)
    with open(file_path, 'wb+') as dest:
        for chunk in file.chunks():
            dest.write(chunk)
    return file_path

def transcribe_speech(file_path):
    client = speech.SpeechClient()
    with open(file_path, 'rb') as audio_file:
        content = audio_file.read()

    audio = speech.RecognitionAudio(content=content)
    config = speech.RecognitionConfig(
        encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
        sample_rate_hertz=16000,
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
    
    spectrogram_path = os.path.join('static', 'spectrograms', f'{os.path.basename(file_path)}.png')
    plt.savefig(spectrogram_path)
    plt.close()

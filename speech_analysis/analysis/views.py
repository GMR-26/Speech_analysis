from django.shortcuts import render, redirect
from django.http import HttpResponse
import os
from pydub import AudioSegment
from .forms import AudioFileForm
from google.cloud import speech
import matplotlib.pyplot as plt
import numpy as np
import speech_recognition as sr
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

def index(request):
    return render(request, 'index.html')

def upload(request):
    if request.method == 'POST':
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            file = form.cleaned_data['audio_file']
            file_path = save_audio_file(file)
            # Convert to mono
            mono_file_path = convert_to_mono(file_path)
            # Transcribe speech using the mono file
            transcription = transcribe_speech(mono_file_path)
            generate_spectrogram(mono_file_path)
            return redirect('display', filename=os.path.basename(mono_file_path))
    else:
        form = AudioFileForm()
    return render(request, 'upload.html', {'form': form})

def record(request):
    return render(request, 'analysis/record.html')

def record_page(request):
    return render(request, 'analysis/record.html')

def record_audio(request):
    if request.method == 'POST':
        audio_file = request.FILES['audio']
        save_path = os.path.join('uploads', 'recorded_audio.wav')

        # Save the uploaded audio file
        with open(save_path, 'wb+') as destination:
            for chunk in audio_file.chunks():
                destination.write(chunk)

        # Optional: Add additional processing here
        return JsonResponse({'message': 'Audio file saved successfully!'})

    return JsonResponse({'error': 'Invalid request'}, status=400)

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

def convert_to_mono(file_path):
    sound = AudioSegment.from_file(file_path)
    sound = sound.set_channels(1)
    mono_file_path = file_path.replace(".wav", "_mono.wav")
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


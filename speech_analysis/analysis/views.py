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
import joblib
import librosa
from django.conf import settings
import pandas as pd

# Load the trained model
try:
    # Use a raw string or forward slashes for the file path
    model_path = os.path.join(settings.BASE_DIR, 'analysis', 'speech_disorder_model.pkl')
    model = joblib.load(model_path)
except FileNotFoundError:
    print("Error: Model file 'speech_disorder_model.pkl' not found. Please train the model first.")
    model = None
except Exception as e:
    print(f"Error loading the model: {e}")
    model = None

def extract_features(file_path):
    try:
        audio, sr = librosa.load(file_path, sr=None)
        print(f"\nAudio stats - Length: {len(audio)}, SR: {sr}, Mean: {np.mean(audio):.2f}")
        
        n_fft = min(2048, len(audio))
        mfccs = librosa.feature.mfcc(y=audio, sr=sr, n_mfcc=40, n_fft=n_fft)
        features = np.mean(mfccs.T, axis=0)
        
        print(f"MFCC stats - Mean: {np.mean(features):.2f}, Min: {np.min(features):.2f}, Max: {np.max(features):.2f}")
        return features
        
    
        # DEBUG: Print feature statistics
        print(f"\nFeature stats for {file_path}:")
        print(f"Mean: {np.mean(mfccs):.2f}")
        print(f"Min: {np.min(mfccs):.2f}")
        print(f"Max: {np.max(mfccs):.2f}")
        
        return np.mean(mfccs.T, axis=0)
        
    except Exception as e:
        print(f"Error extracting features: {str(e)}")
        return None
# Load the model
model = joblib.load('analysis/speech_disorder_model.pkl')


# Ensure the uploads directory exists
UPLOAD_DIR = 'uploads'
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
    print("Created global 'uploads' directory")


def index(request):
    return render(request, 'index.html')

from django.shortcuts import render, redirect
from .forms import AudioFileForm  # Ensure the form is imported
def predict_disorder(file_path):
    """Predict speech disorder with proper feature handling"""
    features = extract_features(file_path)
    if features is not None:
        # Ensure features is 1D numpy array
        features = np.array(features).flatten()
        
        # Reshape for sklearn (1 sample, n_features)
        features = features.reshape(1, -1)
        
        # Convert to DataFrame with correct feature names
        if hasattr(model, 'feature_names_in_'):
            try:
                features_df = pd.DataFrame(features, columns=model.feature_names_in_)
                prediction = model.predict(features_df)[0]
            except:
                # Fallback to numpy array if DataFrame fails
                prediction = model.predict(features)[0]
        else:
            prediction = model.predict(features)[0]
        
        # Get probabilities for debugging
        proba = model.predict_proba(features)[0]
        print(f"\nPrediction details:")
        print(f"Raw features mean: {np.mean(features):.2f}")
        print(f"Class probabilities: {proba}")
        print(f"Predicted class: {prediction} (0=Dysarthria, 1=Healthy)")
        
        return int(prediction)
    return 0  # Default to Dysarthria if features extraction fails

def upload(request):
    if request.method == 'POST':
        form = AudioFileForm(request.POST, request.FILES)
        if form.is_valid():
            audio_file = form.cleaned_data['audio_file']
            file_path = save_audio_file(audio_file)
            
            # Predict speech disorder
            prediction = predict_disorder(file_path)
            
            # Process the audio (convert to mono, generate spectrogram, etc.)
            mono_file_path = convert_to_mono(file_path)
            spectrogram_path = generate_spectrogram(mono_file_path)
            
            # Redirect to the display page with spectrogram and prediction
            filename = os.path.basename(mono_file_path)
            return redirect('display', filename=filename)
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

            # Convert to mono and generate spectrogram
            mono_file_path = convert_to_mono(save_path)
            print(f"Mono file created at: {mono_file_path}")
            spectrogram_path = generate_spectrogram(mono_file_path)
            print(f"Spectrogram created at: {spectrogram_path}")

            # Predict speech disorder
            prediction = predict_disorder(mono_file_path)
            print(f"Prediction: {prediction}")

            # Redirect to the display page with spectrogram and prediction
            filename = os.path.basename(mono_file_path)
            return redirect('display', filename=filename)

        except Exception as e:
            print(f"Error processing audio: {e}")
            return JsonResponse({'error': f'Server error: {str(e)}'}, status=500)
    else:
        print("Invalid request method")
        return JsonResponse({'error': 'Invalid request'}, status=400)

def display(request, filename):
    # Construct the spectrogram URL
    spectrogram_url = os.path.join('spectrograms', f'{filename}.png')
    
    # Construct the path to the mono audio file
    mono_file_path = os.path.join('uploads', filename)
    
    # Predict speech disorder
    prediction = predict_disorder(mono_file_path)
    
    # Render the result
    return render(request, 'display.html', {
        'spectrogram_url': spectrogram_url,
        'prediction': prediction  # Pass the prediction to the template
    })

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
    try:
        # Load the audio file
        audio, sample_rate = librosa.load(file_path, sr=None)
        
        # Generate the spectrogram
        plt.specgram(audio, Fs=sample_rate)
        plt.xlabel('Time')
        plt.ylabel('Frequency')
        plt.title('Spectrogram')

        # Define the spectrogram directory
        spectrogram_dir = os.path.join('static', 'spectrograms')
        if not os.path.exists(spectrogram_dir):
            os.makedirs(spectrogram_dir)

        # Save the spectrogram
        spectrogram_filename = f'{os.path.basename(file_path)}.png'
        spectrogram_path = os.path.join(spectrogram_dir, spectrogram_filename)
        plt.savefig(spectrogram_path)
        plt.close()

        print(f"Spectrogram saved at: {spectrogram_path}")
        return os.path.join('spectrograms', spectrogram_filename)
    except Exception as e:
        print(f"Error generating spectrogram: {e}")
        return None
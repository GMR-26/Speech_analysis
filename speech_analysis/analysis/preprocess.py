import os
import librosa
import numpy as np
import pandas as pd

def extract_features(file_path):
    # Check if the file exists
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        return None
    
    # Load audio file
    try:
        audio, sample_rate = librosa.load(file_path, res_type='kaiser_fast')
    except Exception as e:
        print(f"Error loading {file_path}: {e}")
        return None
    
    # Skip files that are too short
    min_length = 100  # Minimum number of samples required (adjust as needed)
    if len(audio) < min_length:
        print(f"File too short: {file_path} (length={len(audio)})")
        return None
    
    # Adjust n_fft based on the length of the audio signal
    n_fft = min(512, len(audio))  # Use a smaller n_fft value for short audio files
    
    # Extract MFCC features
    mfccs = librosa.feature.mfcc(y=audio, sr=sample_rate, n_mfcc=40, n_fft=n_fft)
    mfccs_scaled = np.mean(mfccs.T, axis=0)
    
    return mfccs_scaled

def create_dataset(csv_path):
    # Load the CSV file
    df = pd.read_csv(csv_path)
    
    features = []
    labels = []

    # Iterate through each row in the CSV
    for index, row in df.iterrows():
        file_path = row['Wav_path']
        # Fix the file path (replace single backslashes with double backslashes)
        file_path = file_path.replace("\\", "\\\\")
        
        label = row['Is_dysarthria']  # Use 'Is_dysarthria' column as the label
        
        # Extract features
        feature = extract_features(file_path)
        if feature is not None:
            features.append(feature)
            labels.append(label)

    # Create DataFrame
    df_features = pd.DataFrame(features)
    df_features['label'] = labels
    return df_features

# Save the dataset
csv_path = r"F:\FILES\S6_MiniProj\Speech_analysis\speech_analysis\analysis\data_with_path.csv"  # Use raw string
df = create_dataset(csv_path)
df.to_csv("speech_dataset.csv", index=False)
print("Dataset saved as speech_dataset.csv")
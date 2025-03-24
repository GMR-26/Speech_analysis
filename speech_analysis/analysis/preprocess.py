import os
import librosa
import numpy as np
import pandas as pd
from pathlib import Path

def extract_features(file_path):
    """Extract MFCC features with error handling"""
    try:
        if not Path(file_path).exists():
            print(f"❌ File not found: {file_path}")
            return None
        
        audio, sample_rate = librosa.load(file_path, sr=None, res_type='kaiser_fast')
        
        if len(audio) < 100:
            print(f"⚠️ Skipped (too short): {file_path}")
            return None
            
        n_fft = min(2048, len(audio))
        mfccs = librosa.feature.mfcc(
            y=audio,
            sr=sample_rate,
            n_mfcc=40,
            n_fft=n_fft,
            hop_length=512
        )
        print(f"✅ Processed: {file_path}")
        return np.mean(mfccs.T, axis=0)
        
    except Exception as e:
        print(f"❌ Error processing {file_path}: {str(e)}")
        return None

def create_dataset(csv_path):
    """Create dataset with progress tracking"""
    try:
        df = pd.read_csv(csv_path)
        features, labels = [], []
        total_files = len(df)
        success_count = 0
        
        print(f"\n🔍 Starting processing of {total_files} audio files...\n")
        
        for index, row in df.iterrows():
            file_path = Path(row['Wav_path']).resolve()
            if not file_path.exists():
                file_path = Path.cwd() / row['Wav_path']
                
            feature = extract_features(str(file_path))
            if feature is not None:
                features.append(feature)
                labels.append(row['Is_dysarthria'])
                success_count += 1
            
            # Progress update every 10 files
            if (index + 1) % 10 == 0:
                print(f"\n📊 Progress: {index + 1}/{total_files} files")
                print(f"✔ Success: {success_count} | ✖ Failed: {index + 1 - success_count}\n")
                
        print("\n🎉 Processing complete!")
        print(f"📋 Results: {success_count}/{total_files} files processed successfully")
        
        return pd.DataFrame(features).assign(label=labels)
        
    except Exception as e:
        print(f"\n🔥 Dataset creation failed: {str(e)}")
        return pd.DataFrame()

if __name__ == "__main__":
    dataset_path = Path(r"C:\Users\user\OneDrive\Documents\GitHub\Speech_analysis\speech_analysis\analysis\data_with_path.csv")
    output_path = dataset_path.parent / "speech_dataset.csv"
    
    df = create_dataset(dataset_path)
    df.to_csv(output_path, index=False)
    print(f"\n💾 Dataset saved to: {output_path}")
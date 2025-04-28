
# 🗣️ Speech Analysis Tool

A Python-based tool developed to assist speech therapists in analyzing patient speech patterns. This project visualizes acoustic features like pitch, energy, and waveform to support diagnosis and treatment planning for individuals with speech disorders.

## 📌 Features

- 🎵 **Waveform Plotting**: Visualizes the raw waveform of audio input.
- 📈 **Pitch Analysis**: Detects and plots pitch variation over time.
- ⚡ **Energy Plotting**: Analyzes and displays energy levels in speech.
- 💾 **Local Database Support**: Uses SQLite to store patient data and analysis outcomes.
- 🧠 **Speech Disorder Support**: Aimed at aiding in diagnosing speech disorders.

## 🛠️ Tech Stack

- **Python**
- **Librosa** – Audio analysis
- **Matplotlib** – Visualization
- **SQLite** – Local storage
- **NumPy**, **Soundfile**, **Tkinter** – Supporting libraries and GUI

## 🚀 How to Run

1. **Clone the Repository**

```bash
git clone https://github.com/GMR-26/Speech_analysis.git
cd Speech_analysis/speech_analysis
```

2. **Install the Dependencies**

Install the required Python packages:

```bash
pip install numpy matplotlib librosa soundfile
```

3. **Run the Application**

```bash
python manage.py runserver
```

## 📂 Folder Structure

```bash
speech_analysis/
├── uploads/                  # Folder to store patient audio files
├── db/                       # SQLite database file for patient records
├── static/spectograms        # Generated waveform, pitch, energy plots
├── analysis                  # Python script for GUI and analysis
└── README.md                 # Project documentation
```

## 👩‍⚕️ Target Audience

Designed for use by **speech therapists**, **linguists**, and **researchers** working in the field of **speech-language pathology**.


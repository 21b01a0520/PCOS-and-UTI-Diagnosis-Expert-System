# PCOS and UTI Diagnosis Expert System

## Overview
This is a Flask-based web application designed as an expert system for diagnosing PCOS (Polycystic Ovary Syndrome) and UTIs (Urinary Tract Infections). The system leverages AI/ML models, speech processing, and text analysis to provide accurate diagnoses and relevant health tips.

## Features
- Web interface built using Flask
- MySQL database integration for storing patient data
- Speech recognition using `SpeechRecognition` for symptom input
- Text translation with `googletrans` to support multiple languages
- Text-to-speech conversion using `gTTS` for audio-based responses
- Natural Language Processing with `nltk`
- Symptom-based diagnosis using AI/ML models
- Text similarity detection using `TfidfVectorizer` and `cosine_similarity` from `scikit-learn`
- Secure password hashing with `bcrypt`
- Health recommendations for PCOS and UTI management

## Project Structure
### 1. Source Code
- `app.py`: Main Flask application.
- `diagnosis_dataset.csv`: Dataset used for symptom-based diagnosis.
- `random_forest_model.joblib`: Pretrained ML model for predictions.

### 2. Documentation
- `README.md`: Instructions on setup, usage, and dependencies.
- `requirements.txt`: List of required dependencies.
- `report.pdf`: Detailed project documentation (if available).
- `architecture.png`: Diagram showcasing the system pipeline.

### 3. Additional Resources
- `Dataset columns information.txt`: Description of dataset fields.
- `logs/`: Training logs and model checkpoints.
- `visualizations/`: Plots, confusion matrices, and analysis results.

### 4. Deployment & UI (if applicable)
- `frontend/`: Frontend UI files (HTML, CSS, JS).
- `static/`: Static resources like images and styles.
- `templates/`: HTML templates for Flask views.

## Requirements
- XAMPP (for Apache and MySQL database)
- Miniconda3 (for environment management)
- Conda environment with required dependencies installed

## Installation
1. Clone the repository:
   ```bash
   git clone <repo_url>
   cd <repo_folder>
   ```
2. Create and activate the conda environment:
   ```bash
   conda create --name flask_env python=3.8
   conda activate flask_env
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Usage
1. Start Apache and MySQL server using XAMPP.
2. Run the Flask application:
   ```bash
   python app.py
   ```
3. Open the browser and navigate to `http://127.0.0.1:5000/`.
4. Input symptoms via text or speech.
5. Receive a diagnosis along with management tips for PCOS or UTI.

## Dependencies
See [`requirements.txt`](./requirements.txt) for a full list of dependencies.

## Contributing
Feel free to submit issues or pull requests to improve this project.

## License
This project is licensed under the MIT License.

from . import data_helper as datah
from . import pdf_helper as pdfh
import base64
import nltk
from nltk.corpus import stopwords
from nltk.stem import PorterStemmer
import os
import pandas as pd
from pathlib import Path
import pickle
import string
import pandas as pd
import numpy as np
import spacy
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
from tensorflow.keras.models import load_model
import subprocess
import sys


def download_model(model_name="en_core_web_sm"):
    """Download the SpaCy model if it's not already installed."""
    subprocess.check_call([sys.executable, "-m", "spacy", "download", model_name])


def load_spacy_model(model_name="en_core_web_sm"):
    """Load the SpaCy model, downloading it if necessary."""
    try:
        # Try to load the model
        return spacy.load(model_name)
    except OSError:
        # If the model is not found, download it and load again
        print(f"Model {model_name} not found. Downloading it now...")
        download_model(model_name)
        return spacy.load(model_name)


def run_once():
    nltk.download("stopwords")


def extract_features(text):
    nlp = load_spacy_model("en_core_web_sm")
    doc = nlp(text)
    pos_tags = [token.pos_ for token in doc]
    entities = [ent.label_ for ent in doc.ents]
    return " ".join(pos_tags + entities)


def preprocess_text(text):
    no_punctuation = [char for char in text if char not in string.punctuation]
    no_punctuation = "".join(no_punctuation)
    words = no_punctuation.lower().split()

    stop_words = set(stopwords.words("english"))
    ps = PorterStemmer()

    processed_words = [ps.stem(word) for word in words if word not in stop_words]
    return " ".join(processed_words)


def get_absolute_path(relative_path):
    return Path(__file__).parent / relative_path


def load(type: str, version: str):
    current_directory = os.getcwd()
    if type == "classifier":
        file_to_be_loaded = os.path.join(
            current_directory,
            "app",
            "ml",
            "models",
            "classifiers",
            f"resume_classifier-{version}.pkl",
        )
    elif type == "vectorizer":
        file_to_be_loaded = os.path.join(
            current_directory,
            "app",
            "ml",
            "models",
            "vectorizers",
            f"vectorizer-{version}.pkl",
        )

    # Check if the file exists before attempting to open it
    if os.path.exists(file_to_be_loaded):
        with open(file_to_be_loaded, "rb") as file:
            return pickle.load(file)
    else:
        print(f"Error: File not found at {file_to_be_loaded}")
        raise FileNotFoundError(f"File not found: {file_to_be_loaded}")


# TODO: deprecate the below two and use the above load(...) method
def load_model_classifier(version):
    return load("classifier", version=version)


def load_vectorizer(version):
    return load("vectorizer", version=version)


def load_lstm_model(version):
    current_directory = os.getcwd()
    file_to_be_loaded = os.path.join(
        current_directory, "app", "ml", "models", "classifiers", f"lstm_model.h5"
    )
    if os.path.exists(file_to_be_loaded):
        return load_model(file_to_be_loaded)  # Keras model loading
    else:
        raise FileNotFoundError(f"File not found: {file_to_be_loaded}")


class_labels = {0: "Match", 1: "Moderate Match", 2: "Not Match"}

get_class_key = lambda value: next(
    (k for k, v in class_labels.items() if v == value), None
)


def classify_message(message, model_version, vectorizer_version):
    preprocessed_message = preprocess_text(message)
    loaded_model = load_model_classifier(model_version)
    loaded_vectorizer = load_vectorizer(vectorizer_version)
    message_vector = loaded_vectorizer.transform([preprocessed_message])
    prediction = loaded_model.predict(message_vector)
    prediction_probs = loaded_model.predict_proba(message_vector)
    predicted_class_label = class_labels[prediction[0]]
    return predicted_class_label, prediction_probs[0]


def classify_lstm(message, selected_model_classifier):
    tokenizer = Tokenizer(num_words=10000)
    input_text = extract_features(message)
    tokenizer.fit_on_texts([input_text])
    sequences = tokenizer.texts_to_sequences([input_text])
    max_sequence_length = 500
    data = pad_sequences(sequences, maxlen=max_sequence_length)
    model = load_lstm_model(selected_model_classifier)
    prediction = model.predict(data)
    return prediction


def process_resumes(
    job_description,
    job_title,
    company_name,
    classifier_version,
    vectorizer_version,
    files,
):
    selected_model_classifier = classifier_version
    selected_model_vectorizer = vectorizer_version

    run_once()  # Ensure the models are initialized

    results = []
    class_labels_lstm_model = {0: "match", 1: "moderate match", 2: "not match"}

    for file in files:
        # Read the PDF and extract text
        resume_text = pdfh.get_text_from_stream(file.file)

        if not resume_text:
            continue

        message = job_description + " " + resume_text

        if selected_model_classifier == "v0.001-08":
            prediction = classify_lstm(message, selected_model_classifier)
            if prediction.shape[0] > 0:
                predictions = np.array(prediction)
                if predictions.shape[1] > 2:
                    predicted_index = np.argmax(predictions, axis=1)[0]
                else:
                    predicted_index = 0
                predicted_label = class_labels_lstm_model[predicted_index]

                probabilities = "; ".join(
                    [
                        f"{class_labels_lstm_model[i].capitalize()}: {prob:.4f}"
                        for i, prob in enumerate(predictions[0])
                    ]
                )
                if len(prediction) > predicted_index:
                    score = prediction[predicted_index][predicted_index] * 100
                else:
                    score = np.max(predictions[0]) * 100

                # Store LSTM prediction results
                results.append(
                    {
                        "Candidate Name": datah.get_candidate_name(file.filename),
                        "Result": predicted_label,
                        "Score": score,
                        "Probabilities": probabilities,  # Convert to a list for JSON serialization
                        "Job Title": job_title,
                        "Company/Client": company_name or "Not provided",
                    }
                )
            else:
                print(f"No valid predictions for file: {file.filename}")
                return f"No valid predictions for file: {file.filename}"
        else:
            # Classification using other models
            result, probs = classify_message(
                message, selected_model_classifier, selected_model_vectorizer
            )
            # Extract candidate details
            candidate_name = datah.get_candidate_name(file.filename)

            # Construct result
            probabilities = "; ".join(
                [f"{class_labels[i]}: {prob:.4f}" for i, prob in enumerate(probs)]
            )
            score = probs[get_class_key(result)] * 100

            # Append the classification results
            results.append(
                {
                    "Candidate Name": candidate_name,
                    "Result": result,
                    "Score": score,
                    "Probabilities": probabilities,
                    "Job Title": job_title,
                    "Company/Client": company_name or "Not provided",
                }
            )

    # Convert results to DataFrame and JSON
    if results:
        results_df = pd.DataFrame(results)
        csv_data = results_df.to_csv(index=False)
        json_data = results_df.to_dict(orient="records")

        # Encode CSV to base64 for download
        b64_csv = base64.b64encode(csv_data.encode()).decode()
        return {"csv": b64_csv, "json": json_data}
    else:
        return {"message": "No valid resumes processed."}

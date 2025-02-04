from app.helpers import classifier_helper as classifierh
from app.core.config import settings

def get_match_score(job_description: str, resume_text: str):
    message = job_description + " " + resume_text
    result, probs = classifierh.classify_message(message=message, model_version=settings.CLASSIFIER_VERSION, vectorizer_version=settings.VECTORIZER_VERSION)

    match_score = str(round(probs[classifierh.get_class_key(result)] * 100, 2))
    
    probabilities = []
    
    for i, prob in enumerate(probs):
        probabilities.append(
            {
                "label": classifierh.class_labels[i],
                "probability": round(float(prob), 4)
            }
        )

    match = {
        "result": result,
        "score": match_score,
        "probabilities": probabilities
    }
    
    return match
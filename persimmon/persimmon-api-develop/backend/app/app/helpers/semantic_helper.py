# from sentence_transformers import SentenceTransformer, util
# from app.helpers.log_helper import log_execution_time

# # Load the pre-trained Sentence-BERT model
# model = SentenceTransformer('all-MiniLM-L6-v2')  #Lightweight and fast, but effective

# @log_execution_time
# def compute_bert_skill_similarity(jd: str, resume: str) -> float:
#     """
#     Compute cosine similarity using BERT embeddings between JD skills and resume skills.

#     Args:
#         jd_skills (str): Comma-separated string of JD skills.
#         resume_skills (str): Comma-separated string of resume skills.

#     Returns:
#         float: Cosine similarity score (0 to 1).
#     """
#     # Get BERT embeddings
#     jd_embedding = model.encode(jd, convert_to_tensor=True)
#     resume_embedding = model.encode(resume, convert_to_tensor=True)
    
#     # Compute cosine similarity
#     cosine_sim = util.cos_sim(jd_embedding, resume_embedding)
    
#     return float(cosine_sim[0][0])

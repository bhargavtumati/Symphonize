import re


# Function to extract candidate's name from resume text
def get_candidate_name(file_name):
    candidate_name = file_name.split(".")[0]
    return candidate_name

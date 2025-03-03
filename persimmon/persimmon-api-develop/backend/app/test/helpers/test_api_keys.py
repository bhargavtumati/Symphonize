from app.helpers import ai_helper as aih

def test_api_key_rotator():
    length = len(aih.api_key_rotator.api_keys)
    keys = []
    for i in range(length):
        key = aih.api_key_rotator.get_next_key()
        assert key not in keys
        keys.append(key)
    for i in range(3):
        key = aih.api_key_rotator.get_next_key()
        assert key == keys[i]

#put this in the ai.py and test the api_keys are working
# @app.get("/extract_features_from_resume")
# async def extract_features_from_resume_endpoint(
#     text: str, 
# ):
#     """
#     FastAPI endpoint to extract features from resume text.
#     """
#     result = await aih.extract_features_from_resume(text)
#     return result
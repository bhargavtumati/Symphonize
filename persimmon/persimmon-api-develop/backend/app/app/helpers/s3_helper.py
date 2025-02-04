from io import BytesIO

import boto3
from joblib import load


def load_model_from_s3(bucket_name, model_key):
  """Loads a model from an S3 bucket.

  Args:
    bucket_name: The name of the S3 bucket.
    model_key: The path to the model file within the bucket.

  Returns:
    The loaded model.
  """

  s3 = boto3.client('s3')
  obj = s3.get_object(Bucket=bucket_name, Key=model_key)
  model_bytes = obj['Body'].read()
  model = load(BytesIO(model_bytes))
  return model


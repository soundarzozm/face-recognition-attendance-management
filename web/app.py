import creds
import boto3

s3 = boto3.client(
    's3',
    region_name = creds.REGION_NAME,
    aws_access_key_id = creds.AWS_ACCESS_KEY_ID,
    aws_secret_access_key = creds.AWS_SECRET_ACCESS_KEY
)

s3.download_file('zomz-test','0.jpeg','/home/soundarzozm/s3/0.jpeg')
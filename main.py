import boto3
import os
from datetime import datetime, timedelta, timezone

aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
aws_secret_access_key = os.environ.get('AWS_SECRET_ACCESS_KEY')
aws_session_token = os.environ.get('AWS_SESSION_TOKEN')

# Resource IDs collected from Config (Dummy Sample)
rotate_needed_id_list = ['XXXXXXXXXXXXXXXXXXXXX','YYYYYYYYYYYYYYYYYYYYY','ZZZZZZZZZZZZZZZZZZZZZ']

client = boto3.client('iam')

# List Users
users = client.list_users()['Users']

for user in users:
    user_name = user['UserName']
    user_id = user['UserId']

    # Mapping user ID based on resource IDs collect from Config
    if user_id in rotate_needed_id_list:
        # Get access key info from the matching user
        access_keys = client.list_access_keys(
            UserName=user_name
        )['AccessKeyMetadata']

        # Check if access key created more than 90 days
        for access_key in access_keys:
            if datetime.now(timezone.utc) - access_key['CreateDate'] > timedelta(days=90):
                access_key_id = access_key['AccessKeyId']

                # Deactivate the matching access key
                client.update_access_key(
                    UserName=user_name,
                    AccessKeyId=access_key_id,
                    Status='Inactive'
                )

                # Delete the matching access key
                client.delete_access_key(
                    UserName=user_name,
                    AccessKeyId=access_key_id
                )

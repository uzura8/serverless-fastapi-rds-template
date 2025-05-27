import os
import json
import subprocess
from datetime import datetime, timezone

import boto3

s3 = boto3.client('s3')


def handler(event, context):

    raw_host = os.environ['DB_HOST']
    try:
        host_cfg = json.loads(raw_host)
        db_host = host_cfg['write']['address']
    except json.JSONDecodeError:
        # If not JSON, use it as is
        db_host = raw_host

    # Add timestamp to the dump file name
    ts = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ')
    dump_file = f"/tmp/{os.environ['DB_NAME']}_{ts}.sql"

    # execute mysqldump command
    cmd = [
        "mysqldump",
        "-h", db_host,
        "-P", str(os.environ['DB_PORT']),
        "-u", os.environ['DB_USER'],
        f"-p{os.environ['DB_PASSWORD']}",
        os.environ['DB_NAME']
    ]
    with open(dump_file, "wb") as f:
        subprocess.check_call(cmd, stdout=f)

    # upload to S3
    bucket = os.environ['DEPLOYMENT_BUCKET_NAME']
    prefix = f"rds-backup/{os.environ['PRJ_PREFIX']}/"
    key = prefix + os.path.basename(dump_file)
    s3.upload_file(dump_file, bucket, key)

    # Delete old backups if more than the specified count
    keep = os.environ['BACKUP_FILE_COUNT']

    # Get the list of objects with the specified prefix
    resp = s3.list_objects_v2(Bucket=bucket, Prefix=prefix)
    objs = resp.get('Contents', []) or []

    # Sorting by LastModified in ascending order (oldest first)
    objs_sorted = sorted(objs, key=lambda o: o['LastModified'])

    # Get the number of objects to delete
    to_delete = objs_sorted[:-keep]
    if to_delete:
        delete_req = {'Objects': [{'Key': obj['Key']} for obj in to_delete]}
        s3.delete_objects(Bucket=bucket, Delete=delete_req)

    return {
        "status": "OK",
        "bucket": bucket,
        "key": key,
        "deleted_old": [obj['Key'] for obj in to_delete]
    }

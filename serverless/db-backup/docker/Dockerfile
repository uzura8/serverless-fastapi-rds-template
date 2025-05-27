# Use Official Python image for AWS Lambda
FROM public.ecr.aws/lambda/python:3.10

# Install MySQL client to use mysqldump command
# Install by yum command because it is based on Amazon Linux 2
RUN yum update -y \
 && yum install -y mysql \
 && yum clean all

COPY requirements.txt  .
RUN pip install --no-cache-dir -r requirements.txt

# Include the handler code in the image
COPY app/ /var/task/app/

# Set the CMD to your handler
CMD ["app/db_backup_handler.handler"]


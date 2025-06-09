# Sample FastAPI App

Constructed by

- ServerSide:
  - Python/FastAPI on Lambda + APIGateway
  - Deploy by Terraform and Serverless Framework ver4

## Instration

### Preparation

You need below

- common
  - aws-cli >= 2.22.X
  - Terraform >= 1.12.X
- serverless
  - nodeJS >= 22.14.X
  - Python >= 3.13.X

#### Install Terraform

Install terraform on mac

```bash
brew install tfenv
tfenv install 1.11.
tfenv use 1.11.3
```

#### Install Poetry

Install Poetry for python package management

```bash
curl -sSL https://install.python-poetry.org | python -
echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
poetry --version
```

Install poetry-plugin-export plugin

```bash
poetry self add poetry-plugin-export
```

### Install Packages

Install npm packages

```bash
# At project root dir
cd (project_root/)serverless
npm install
```

Install python packages

```bash
# At project root dir
cd (project_root/)serverless
poetry install --without dev
```

You need to install Poetry to manage python packages.
Refer to [Poetry Installation](https://python-poetry.org/docs/#installation) for more details.

## Deploy AWS Resources by Terraform

### Create AWS S3 Bucket for terraform state and frontend config

Create S3 Buckets like below in ap-northeast-1 region

- **your-serverless-deployment**
  - Store deployment state files by terraform and serverless framework
  - Create directory "terraform/your-project-name"
- **your-serverless-configs**
  - Store config files for app
  - Create directory "your-project-name/frontend/prd" and "your-project-name/frontend/dev"

#### 1. Edit Terraform config file

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp terraform.tfvars.sample terraform.tfvars
vi terraform.tfvars
```

#### 2. Edit remote setup script for EC2

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp bin/remote_setup_webapp.sh.sample bin/remote_setup_webapp.sh
vi bin/remote_setup_webapp.sh
```

#### 3. Prepare Lambda@Edge for Viewer Request

Copy sample file and edit variables for your env

```bash
cd (project_root_dir)/terraform
cp functions/src/viewer_request/configs/config.js.sample functions/src/viewer_request/configs/config.js
vi functions/src/viewer_request/configs/config.js
```

Execute below command to package Lambda@Edge function

```bash
sh bin/package_lambda_edge_function.sh
```

#### 4. Set AWS profile name to environment variable

```bash
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE=your-aws-profile-name
export AWS_REGION="ap-northeast-1"
```

#### 5. Execute terraform init

Command Example to init

```bash
terraform init -backend-config="bucket=your-deployment" -backend-config="key=terraform/your-project/terraform.tfstate" -backend-config="region=ap-northeast-1" -backend-config="profile=your-aws-profile-name"
```

#### 6. Execute terraform apply

```bash
terraform apply
```

## Deploy Server Side Resources

### Setup configs

Setup config files per stage

```bash
cd (project_root/)serverless
cp -r config/stages-sample config/stages
vi config/stages/*
```

### Create Domains for API

Execute below command

```bash
cd (project_root/)serverless
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

npx sls create_domain --stage target-env
```

### Deploy to Lambda

Execute below command

```bash
cd (project_root/)serverless
export AWS_SDK_LOAD_CONFIG=1
export AWS_PROFILE="your-profile-name"
export AWS_REGION="ap-northeast-1"

npx sls deploy --stage target-env --verbose
```

## Deploy Frontend Resources

### Set Environment Variables

- Access to <https://github.com/{your-account}/{repository-name}/settings/secrets/actions>
- Push "New repository secret"
- Add Below
  - Common
    - **AWS_ACCESS_KEY_ID** : your-aws-access_key
    - **AWS_SECRET_ACCESS_KEY** : your-aws-secret_key
  - For Production
    - **CLOUDFRONT_DISTRIBUTION** : your cloudfront distribution created by terraform for production
    - **S3_CONFIG_BUCKET**: "your-serverles-configs/your-project/frontend/prd" for production
    - **S3_RESOURCE_BUCKET**: "your-domain-static-site.example.com" for production
  - For Develop
    - **CLOUDFRONT_DISTRIBUTION_DEV** : your cloudfront distribution created by terraform for develop
    - **S3_CONFIG_BUCKET_DEV**: "your-serverles-configs/your-project/frontend/dev" for develop
    - **S3_RESOURCE_BUCKET_DEV**: "your-domain-static-site-dev.example.com" for develop

### Upload config file for frontend app

#### Edit config file

#### Basic config

```bash
cd (project_root_dir/)frontend
cp src/config/config.json.sample src/config/config.json
vi src/config/config.json
```

#### Upload S3 Bucket "your-serverless-configs/your-project-name/frontend/{stage}"

- config.json

#### Deploy continually on pushed to git

## DB Backup by MySQL Dump on Lambda

Prepare

```bash
cd (project_root/)serverless
aws-vault exec your-aws-role-for-deploy
. .venv/bin/activate
```

Edit config file

```bash
vi config/stages/Target-stage.yml
# Edit item for dbBackup
```

```bash
cd (project_root/)serverless/
cd db-backup/ # It's important to run this command in the db-backup directory
```

```bash
npx sls deploy --stage Target-stage --verbose
```

## Development

### Local Development

Install packages for development

```bash
cd (project_root/)serverless
poetry install --only dev
```

### Work on local

#### Prepare Local Environment

```bash
cd (project_root/)serverless
cp develop/env.sh.sample develop/env.sh
vi develop/env.sh
# Edit variables for your local environment
```

Apply environment variables

```bash
source develop/env.sh
```

#### WEB App on local

Build Docker container and start

```bash
cd (project_root/)serverless
poetry shell
uvicorn app.main:app --reload
```

Request [http://127.0.0.1:8000](http://127.0.0.1:8000)
API document is available at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

#### Execute Script

```bash
cd (project_root/)serverless
npx sls invoke local --function funcName --data param
```

### Test

```bash
cd (project_root/)serverless
poetry run pytest
```

## Destroy Resources

If you deployed dbBackup function, execute below command

```bash
cd (project_root/)serverless/
cd db-backup/ # It's important to run this command in the db-backup directory
npx sls remove --stage Target-stage --verbose
```

Destroy for serverless resources

```bash
cd (project_root/)serverless
npx sls remove --stage Target-stage --verbose
npx sls delete_domain --stage Target-stage
```

Removed files in S3 Buckets named "your-domain.example.com-cloudfront-logs" and "your-domain.example.com"

Destroy for static server resources by Terraform

```bash
cd (project_root/)terraform
terraform destroy
```

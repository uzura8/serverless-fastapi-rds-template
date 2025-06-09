variable "prj_prefix" {}
variable "environment" {}

variable "region_api" {}
variable "region_site" {}
variable "region_lambda_edge" {}
variable "region_acm" {}
variable "route53_zone_id" {}
variable "domain_api" {}

variable "domain_static_site" {}
variable "s3_static_site_force_destroy" {
  description = "S3 bucket force_destroy control. If true, it can be deleted even if objects exist"
  type        = bool
  default     = false
}

#variable "aws_db_instance_count" {}
variable "aws_db_instance_type" {}
variable "aws_db_allocated_storage" {}
variable "aws_db_block_volume_type" {}
variable "aws_db_engine" {}
variable "aws_db_engine_version" {}
variable "aws_db_backup_retention_period" {}
#variable "aws_db_backtrack_window_seconds" {}
variable "aws_db_deletion_protection" {}
variable "aws_db_port" {}
variable "aws_db_username" {}
variable "aws_db_password" {}
#variable "aws_db_name" {}
#variable "vpc_availability_zones" {}
variable "app_is_enabled" {}
variable "key_name" {}
variable "key_file_path" {}
variable "security_ssh_ingress_cidrs" {}
variable "ec2_instance_type" {}
#variable "ec2_ami_type" {}
variable "ec2_ami_id" {}
variable "ec2_root_block_volume_type" {}
variable "ec2_root_block_volume_size" {}
#variable "ec2_ebs_block_volume_type" {}
#variable "ec2_ebs_block_volume_size" {}

terraform {
  backend "s3" {
  }
  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "= 5.94.1"
    }
  }
}

module "module_domain_api" {
  source          = "./modules/aws/domain_api"
  prj_prefix      = var.prj_prefix
  route53_zone_id = var.route53_zone_id
  domain_api      = var.domain_api
  region_api      = var.region_api
  region_acm      = var.region_acm
}

module "module_static_site" {
  source                       = "./modules/aws/static_site"
  prj_prefix                   = var.prj_prefix
  route53_zone_id              = var.route53_zone_id
  domain_static_site           = var.domain_static_site
  region_site                  = var.region_site
  region_acm                   = var.region_acm
  region_lambda_edge           = var.region_lambda_edge
  s3_static_site_force_destroy = var.s3_static_site_force_destroy
}

# VPC
module "module_vpc" {
  source = "./modules/aws/vpc"
  #availability_zones = var.vpc_availability_zones
  prj_prefix = var.prj_prefix
}

# EC2
module "module_ec2" {
  source                     = "./modules/aws/ec2"
  vpc_id                     = module.module_vpc.vpc_id
  subnet_public_id           = module.module_vpc.subnet_public_ids[0]
  key_name                   = var.key_name
  security_ssh_ingress_cidrs = var.security_ssh_ingress_cidrs
  prj_prefix                 = var.prj_prefix
  ec2_instance_type          = var.ec2_instance_type
  ec2_root_block_volume_type = var.ec2_root_block_volume_type
  ec2_root_block_volume_size = var.ec2_root_block_volume_size
  #ec2_ami_type               = var.ec2_ami_type
  ec2_ami_id = var.ec2_ami_id
  #ec2_ebs_block_volume_type = var.ec2_ebs_block_volume_type
  #ec2_ebs_block_volume_size = var.ec2_ebs_block_volume_size
  #public_key_value          = module.module_keygen.public_key_openssh
}

# RDS
module "module_rds" {
  source                           = "./modules/aws/rds"
  vpc_id                           = module.module_vpc.vpc_id
  security_group_private_lambda_id = module.module_vpc.security_group_private_lambda_id
  security_group_web_id            = module.module_ec2.security_group_web_id
  subnet_group_db_name             = module.module_vpc.subnet_group_db_name
  subnet_private_db_ids            = module.module_vpc.subnet_private_db_ids
  #db_instance_count                = var.aws_db_instance_count
  db_instance_type           = var.aws_db_instance_type
  db_allocated_storage       = var.aws_db_allocated_storage
  db_block_volume_type       = var.aws_db_block_volume_type
  db_engine                  = var.aws_db_engine
  db_engine_version          = var.aws_db_engine_version
  db_backup_retention_period = var.aws_db_backup_retention_period
  db_deletion_protection     = var.aws_db_deletion_protection
  db_port                    = var.aws_db_port
  db_username                = var.aws_db_username
  db_password                = var.aws_db_password
  #db_name           = var.aws_db_name
  prj_prefix  = var.prj_prefix
  environment = var.environment
}

# Setup WebApp
module "module_webapp" {
  source         = "./modules/remote/webapp"
  app_is_enabled = var.app_is_enabled
  key_name       = var.key_name
  key_file_path  = var.key_file_path
  public_ip      = module.module_ec2.public_ip
  ec2_obj        = module.module_ec2.ec2_obj
  #rds_obj   = module.module_rds.rds_obj
}

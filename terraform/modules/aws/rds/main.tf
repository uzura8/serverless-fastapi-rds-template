#variable "db_is_enabled" {}
variable "vpc_id" {}
variable "subnet_group_db_name" {}
variable "subnet_private_db_ids" {}
variable "security_group_private_lambda_id" {}
variable "security_group_web_id" {}
variable "db_instance_type" {}
variable "db_block_volume_type" {}
variable "db_allocated_storage" {}
variable "db_engine" {}
variable "db_engine_version" {}
variable "db_backup_retention_period" {}
variable "db_deletion_protection" {}
variable "db_port" {}
variable "db_username" {}
variable "db_password" {}
#variable "db_name" {}
variable "prj_prefix" {}
variable "environment" {}

resource "aws_security_group" "db" {
  vpc_id = var.vpc_id

  ingress {
    description     = "MySQL TLS from sg_rds_proxy"
    from_port       = var.db_port
    to_port         = var.db_port
    protocol        = "tcp"
    security_groups = [var.security_group_web_id, var.security_group_private_lambda_id]
  }

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }
}

# Parameter group
resource "aws_db_parameter_group" "mysql" {
  name   = join("-", [var.prj_prefix, "sg-parameter-group-mysql"])
  family = "mysql8.0"

  parameter {
    name  = "character_set_server"
    value = "utf8mb4"
  }
  parameter {
    name  = "collation_server"
    value = "utf8mb4_unicode_ci"
  }
  parameter {
    name         = "time_zone"
    value        = "Asia/Tokyo"
    apply_method = "immediate"
  }

  # If you want to debug, set the value to 1
  parameter {
    name         = "general_log"
    value        = "0"
    apply_method = "immediate"
  }

  parameter {
    name         = "slow_query_log"
    value        = "1"
    apply_method = "immediate"
  }
  parameter {
    name         = "long_query_time"
    value        = "0.5"
    apply_method = "immediate"
  }
  parameter {
    name         = "log_output"
    value        = "FILE"
    apply_method = "immediate"
  }

  parameter {
    name  = "max_connections"
    value = "200"
  }
  parameter {
    name  = "innodb_file_per_table"
    value = "1"
  }
  parameter {
    name  = "innodb_flush_log_at_trx_commit"
    value = "1"
  }
}

data "aws_iam_policy" "rds_monitoring_role" {
  arn = "arn:aws:iam::aws:policy/service-role/AmazonRDSEnhancedMonitoringRole"
}
data "aws_iam_policy_document" "rds_monitoring_role" {
  statement {
    actions = ["sts:AssumeRole"]

    principals {
      type        = "Service"
      identifiers = ["monitoring.rds.amazonaws.com"]
    }
  }
}
resource "aws_iam_role" "rds_monitoring_role" {
  name               = join("-", [var.prj_prefix, "rds-enhanced-monitoring-role"])
  assume_role_policy = data.aws_iam_policy_document.rds_monitoring_role.json
}
resource "aws_iam_role_policy_attachment" "rds_monitoring_role" {
  role       = aws_iam_role.rds_monitoring_role.name
  policy_arn = data.aws_iam_policy.rds_monitoring_role.arn
}

resource "aws_db_instance" "db" {
  # count             = var.db_is_enabled
  identifier        = join("-", [var.prj_prefix, "rds-db1"])
  allocated_storage = var.db_allocated_storage
  engine            = var.db_engine
  engine_version    = var.db_engine_version
  instance_class    = var.db_instance_type
  storage_type      = var.db_block_volume_type
  username          = var.db_username
  password          = var.db_password
  #name             = var.db_name != "" ? var.db_name : ""
  parameter_group_name                  = aws_db_parameter_group.mysql.name
  performance_insights_enabled          = var.environment == "prd"
  performance_insights_retention_period = var.environment == "prd" ? 7 : null
  monitoring_interval                   = 60
  monitoring_role_arn                   = aws_iam_role.rds_monitoring_role.arn
  enabled_cloudwatch_logs_exports       = ["error", "general", "slowquery"]
  backup_retention_period               = var.db_backup_retention_period
  vpc_security_group_ids                = [aws_security_group.db.id]
  db_subnet_group_name                  = var.subnet_group_db_name
  publicly_accessible                   = false

  deletion_protection       = var.db_deletion_protection
  apply_immediately         = var.environment != "prd"
  skip_final_snapshot       = var.environment != "prd"
  final_snapshot_identifier = var.environment == "prd" ? join("-", [var.prj_prefix, "rds", "final-snapshot"]) : null

  tags = {
    Name      = join("-", [var.prj_prefix, "rds-db1"])
    ManagedBy = "terraform"
  }
}


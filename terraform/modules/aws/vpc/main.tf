variable "prj_prefix" {}

# Get availability zones
data "aws_availability_zones" "available" {
  state = "available"
}

resource "aws_vpc" "main" {
  cidr_block           = "10.0.0.0/16"
  instance_tenancy     = "default" # Default is shared tenancy
  enable_dns_support   = true      # Enable to refer host names of RDS instances from EC2 and Lambda
  enable_dns_hostnames = true      # Enable to refer host names of RDS instances from EC2 and Lambda

  tags = {
    Name      = join("-", [var.prj_prefix, "vpc"])
    ManagedBy = "terraform"
  }
}

resource "aws_internet_gateway" "main" {
  vpc_id = aws_vpc.main.id

  tags = {
    Name      = join("-", [var.prj_prefix, "igw"])
    ManagedBy = "terraform"
  }
}

resource "aws_route_table" "public" {
  vpc_id = aws_vpc.main.id
  route {
    cidr_block = "0.0.0.0/0"
    gateway_id = aws_internet_gateway.main.id
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "rtb", "public"])
    ManagedBy = "terraform"
  }
}

resource "aws_subnet" "public" {
  count  = 2
  vpc_id = aws_vpc.main.id
  #cidr_block              = "10.0.0.0/24"
  #cidr_block              = "10.0.1.0/24"
  cidr_block              = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index) # Generated 10.0.0.0/20 and 10.0.16.0/20
  availability_zone       = data.aws_availability_zones.available.names[count.index]
  map_public_ip_on_launch = true

  tags = {
    Name      = "${var.prj_prefix}-subnet-public-${count.index + 1}"
    ManagedBy = "terraform"
  }
}
resource "aws_route_table_association" "public" {
  count          = length(aws_subnet.public)
  subnet_id      = aws_subnet.public[count.index].id
  route_table_id = aws_route_table.public.id
}

#resource "aws_subnet" "public_web1" {
#  vpc_id                  = aws_vpc.main.id
#  cidr_block              = "10.0.0.0/24"
#  availability_zone       = var.availability_zones[0]
#  map_public_ip_on_launch = true
#  #availability_zone = data.aws_availability_zones.available.names[0]
#
#  tags = {
#    Name      = join("-", [var.prj_prefix, "subnet", "web-1"])
#    ManagedBy = "terraform"
#  }
#}
#resource "aws_route_table_association" "public_web1" {
#  subnet_id      = aws_subnet.public_web1.id
#  route_table_id = aws_route_table.public.id
#}
#
#resource "aws_subnet" "public_web2" {
#  vpc_id                  = aws_vpc.main.id
#  cidr_block              = "10.0.1.0/24"
#  availability_zone       = var.availability_zones[1]
#  map_public_ip_on_launch = true
#  #availability_zone = data.aws_availability_zones.available.names[0]
#
#  tags = {
#    Name      = join("-", [var.prj_prefix, "subnet", "web-2"])
#    ManagedBy = "terraform"
#  }
#}
#resource "aws_route_table_association" "public_web2" {
#  subnet_id      = aws_subnet.public_web2.id
#  route_table_id = aws_route_table.public.id
#}

# network db
resource "aws_subnet" "private_db" {
  count  = 2
  vpc_id = aws_vpc.main.id
  #cidr_block        = "10.0.10.0/24"
  cidr_block        = cidrsubnet(aws_vpc.main.cidr_block, 4, count.index + 8) # Generated 10.0.128.0/20 and 10.0.144.0/20
  availability_zone = data.aws_availability_zones.available.names[count.index]

  tags = {
    Name      = "${var.prj_prefix}-subnet-db-${count.index + 1}"
    ManagedBy = "terraform"
  }
}
#resource "aws_subnet" "private_db1" {
#  vpc_id            = aws_vpc.main.id
#  cidr_block        = "10.0.10.0/24"
#  availability_zone = var.availability_zones[0]
#  #availability_zone = data.aws_availability_zones.available.names[0]
#
#  tags = {
#    Name      = join("-", [var.prj_prefix, "subnet", "db-1"])
#    ManagedBy = "terraform"
#  }
#}
#
#resource "aws_subnet" "private_db2" {
#  vpc_id            = aws_vpc.main.id
#  cidr_block        = "10.0.20.0/24"
#  availability_zone = var.availability_zones[1]
#  #availability_zone = data.aws_availability_zones.available.names[1]
#
#  tags = {
#    Name      = join("-", [var.prj_prefix, "subnet", "db-2"])
#    ManagedBy = "terraform"
#  }
#}

resource "aws_db_subnet_group" "main" {
  description = "It is a DB subnet group on tf_vpc."
  name        = "${var.prj_prefix}-db-subnet-group"
  subnet_ids  = aws_subnet.private_db[*].id

  tags = {
    Name      = "${var.prj_prefix}-db-subnet-group"
    ManagedBy = "terraform"
  }
}
#resource "aws_db_subnet_group" "main" {
#  description = "It is a DB subnet group on tf_vpc."
#  subnet_ids  = [aws_subnet.private_db1.id, aws_subnet.private_db2.id]
#
#  tags = {
#    Name      = join("-", [var.prj_prefix, "subnet", "db"])
#    ManagedBy = "terraform"
#  }
#}

# Security Group for Lambda
resource "aws_security_group" "private_lambda_sg" {
  name        = "${var.prj_prefix}-private-lambda-sg"
  description = "Security group for Lambda functions in VPC"
  vpc_id      = aws_vpc.main.id

  egress {
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "${var.prj_prefix}-lambda-sg"
    ManagedBy = "terraform"
  }
}

# Private Subnet for Lambada and NAT oGateway: for availability_zones[0]
# 運用で使用するので、冗長構成は不要と判断
resource "aws_subnet" "private_lambda1" {
  #count             = length(data.aws_availability_zones.available.names)
  vpc_id            = aws_vpc.main.id
  cidr_block        = "10.0.100.0/24"
  availability_zone = data.aws_availability_zones.available.names[0]

  tags = {
    Name      = join("-", [var.prj_prefix, "subnet", "lambda-1"])
    ManagedBy = "terraform"
  }
}
resource "aws_eip" "nat1" {
  domain = "vpc"
}
resource "aws_nat_gateway" "nat1" {
  allocation_id = aws_eip.nat1.id
  subnet_id     = aws_subnet.public[0].id
  depends_on    = [aws_internet_gateway.main]
}
# Route Table to use NAT Gateway for lambda subnet
resource "aws_route_table" "private_lambda1_rt" {
  vpc_id = aws_vpc.main.id

  route {
    cidr_block     = "0.0.0.0/0"
    nat_gateway_id = aws_nat_gateway.nat1.id
  }

  tags = {
    Name      = join("-", [var.prj_prefix, "rtb", "private-lambda"])
    ManagedBy = "terraform"
  }
}
resource "aws_route_table_association" "private_lambda1" {
  subnet_id      = aws_subnet.private_lambda1.id
  route_table_id = aws_route_table.private_lambda1_rt.id
}

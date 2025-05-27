output "vpc_id" {
  value = aws_vpc.main.id
}

output "subnet_public_ids" {
  description = "Public subnet id list"
  value       = aws_subnet.public[*].id
  # value = [aws_subnet.public_web1.id, aws_subnet.public_web2.id]
}

output "subnet_private_db_ids" {
  description = "Private DB subnet id list"
  value       = aws_subnet.private_db[*].id
  #value = [aws_subnet.private_db1.id, aws_subnet.private_db2.id]
}

output "subnet_group_db_name" {
  description = "DB subnet group name"
  value       = aws_db_subnet_group.main.name
}

output "security_group_private_lambda_id" {
  description = "Security group id for Lambda"
  value       = aws_security_group.private_lambda_sg.id
}

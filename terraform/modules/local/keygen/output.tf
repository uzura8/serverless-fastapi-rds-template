# path of private key to use for access to server
# public key value
output "public_key_openssh" {
  value = "${tls_private_key.keygen.public_key_openssh}"
}

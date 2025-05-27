#!/bin/shell

KEY_FILE=$1
IP=`cat ./terraform.tfstate|jq -r '.resources[]|select(.type == "aws_eip")|.instances[0] | .attributes | .public_ip'`
#echo ${IP}

ssh -i ${KEY_FILE} ec2-user@${IP}

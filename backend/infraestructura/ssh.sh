host=$(aws ec2 describe-instances \
  --instance-ids i-0f79edab0d8431e5a \
  --region sa-east-1 \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text \
  --no-cli-pager)

echo "IP de la VM: $host"
ssh -i "~/seadd-key.pem" ubuntu@$host
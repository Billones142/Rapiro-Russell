host=$(aws ec2 describe-instances \
  --instance-ids i-0e79c2f83e445cd55 \
  --region sa-east-1 \
  --query "Reservations[0].Instances[0].PublicIpAddress" \
  --output text \
  --no-cli-pager)

echo "IP de la VM: $host"
ssh -i "~/seadd-key.pem" ubuntu@$host
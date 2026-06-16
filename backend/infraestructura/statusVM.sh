aws ec2 describe-instances \
  --instance-ids i-0f79edab0d8431e5a \
  --region sa-east-1 \
  --query "Reservations[0].Instances[0].{Estado: State.Name, IP_Publica: PublicIpAddress}" \
  --output table \
  --no-cli-pager
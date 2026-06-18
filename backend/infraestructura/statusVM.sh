aws ec2 describe-instances \
  --instance-ids i-0e79c2f83e445cd55 \
  --region sa-east-1 \
  --query "Reservations[0].Instances[0].{Estado: State.Name, IP_Publica: PublicIpAddress}" \
  --output table \
  --no-cli-pager
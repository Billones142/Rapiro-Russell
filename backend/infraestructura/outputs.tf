output "instancia_id" {
  description = "ID de la instancia EC2 creada"
  value       = aws_instance.web_server.id
}

output "ip_publica" {
  description = "Dirección IP pública de la máquina virtual"
  value       = aws_instance.web_server.public_ip
}
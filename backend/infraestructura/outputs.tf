output "container_id" {
  description = "ID del contenedor Docker creado"
  value       = docker_container.seadd_service.id
}

output "container_name" {
  description = "Nombre del contenedor Docker"
  value       = docker_container.seadd_service.name
}

output "url_acceso" {
  description = "URL para acceder al dashboard"
  value       = "http://localhost:${var.external_port}/"
}
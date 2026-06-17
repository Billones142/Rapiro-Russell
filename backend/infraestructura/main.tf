# Construir la imagen Docker local de la aplicación
resource "docker_image" "seadd_backend" {
  name = "seadd-backend:latest"
  build {
    context    = "${path.module}/.."
    dockerfile = "Dockerfile"
  }
  keep_locally = true
}

# Crear y ejecutar el contenedor Docker
resource "docker_container" "seadd_service" {
  image = docker_image.seadd_backend.image_id
  name  = "seadd-service"
  restart = "always"

  ports {
    internal = 8000
    external = var.external_port
  }
}
variable "aws_region" {
  description = "Región de AWS donde se crearán los recursos"
  type        = string
  default     = "us-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia para la máquina virtual"
  type        = string
  default     = "t2.micro" # Incluida en la capa gratuita (Free Tier)
}

variable "instance_name" {
  description = "Valor para la etiqueta Name de la instancia"
  type        = string
  default     = "MiMaquinaVirtual"
}
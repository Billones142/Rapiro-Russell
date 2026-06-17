variable "aws_region" {
  description = "Región de AWS donde se crearán los recursos"
  type        = string
  default     = "sa-east-1"
}

variable "instance_type" {
  description = "Tipo de instancia para la máquina virtual"
  type        = string
  default     = "t3.micro" # Capa gratuita (Free Tier) para la región sa-east-1
}


variable "instance_name" {
  description = "Valor para la etiqueta Name de la instancia"
  type        = string
  default     = "MiMaquinaVirtual"
}

variable "key_name" {
  description = "Nombre del par de claves SSH registrado en AWS"
  type        = string
  default     = "seadd-key"
}
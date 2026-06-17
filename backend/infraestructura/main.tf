# Buscar la última AMI de Ubuntu 22.04 LTS activa
data "aws_ami" "ubuntu" {
  most_recent = true

  filter {
    name     = "name"
    values   = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name     = "virtualization-type"
    values   = ["hvm"]
  }

  owners = ["099720109477"] # ID oficial de Canonical (creadores de Ubuntu)
}

# Crear un Security Group para permitir SSH (22) y HTTP (80)
resource "aws_security_group" "sg_seadd" {
  name        = "seadd_security_group"
  description = "Permitir SSH en puerto 22 y HTTP en puerto 80"

  ingress {
    description      = "SSH"
    from_port        = 22
    to_port          = 22
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  ingress {
    description      = "HTTP"
    from_port        = 80
    to_port          = 80
    protocol         = "tcp"
    cidr_blocks      = ["0.0.0.0/0"]
  }

  egress {
    from_port        = 0
    to_port          = 0
    protocol         = "-1"
    cidr_blocks      = ["0.0.0.0/0"]
  }
}

# Definir la instancia EC2
resource "aws_instance" "web_server" {
  ami                    = data.aws_ami.ubuntu.id
  instance_type          = var.instance_type
  key_name               = var.key_name
  vpc_security_group_ids = [aws_security_group.sg_seadd.id]

  # Script de inicio para instalar Docker y arrancar el contenedor
  user_data = <<-EOF
              #!/bin/bash
              apt-get update -y
              apt-get install -y docker.io git
              systemctl start docker
              systemctl enable docker
              
              # Agregar el usuario ubuntu al grupo docker
              usermod -aG docker ubuntu

              # Clonar y construir la aplicación
              git clone https://github.com/Billones142/Rapiro-Russell.git /home/ubuntu/Rapiro-Russell || true
              
              if [ -d "/home/ubuntu/Rapiro-Russell/backend" ]; then
                cd /home/ubuntu/Rapiro-Russell/backend
                docker build -t seadd-backend .
                docker run -d --restart always -p 80:8000 --name seadd-service seadd-backend
              fi
              EOF

  tags = {
    Name = var.instance_name
  }
}
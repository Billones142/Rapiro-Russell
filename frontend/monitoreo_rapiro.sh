#!/bin/bash
# Forzar formato numérico universal (evita problemas de comas en los decimales)
export LC_ALL=C
export AWS_DEFAULT_REGION="sa-east-1"

while true; do
    # 1. Temperatura de la Raspberry Pi
    RAW_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp 2>/dev/null)
    CPU_TEMP=$(echo "scale=2; $RAW_TEMP / 1000" | bc)

    # 2. Latencia de red hacia AWS San Pablo
    LATENCY=$(ping -c 1 sa-east-1.ec2.amazonaws.com | grep 'rtt' | cut -d'/' -f5)
    if [ -z "$LATENCY" ]; then LATENCY=0; fi

    # 3. Uso de CPU (Filtro nativo ultraestable con top)
    CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | sed "s/.*, *\([0-9.]*\)%* id.*/\1/" | awk '{print 100 - $1}')

    # 4. Uso de Memoria RAM en porcentaje
    RAM_USAGE=$(free | awk '/Mem:/ {print $3/$2 * 100.0}')

    # --- Envío de Métricas a AWS CloudWatch ---

    aws cloudwatch put-metric-data \
      --namespace "RAPIRO/PercepcionEdge" \
      --metric-name "Temperatura_CPU" \
      --value "$CPU_TEMP" \
      --unit "Count"

    aws cloudwatch put-metric-data \
      --namespace "RAPIRO/PercepcionEdge" \
      --metric-name "Latencia_Red_Cloud" \
      --value "$LATENCY" \
      --unit "Milliseconds"

    aws cloudwatch put-metric-data \
      --namespace "RAPIRO/PercepcionEdge" \
      --metric-name "Rapiro_Uso_CPU" \
      --value "$CPU_USAGE" \
      --unit "Percent"

    aws cloudwatch put-metric-data \
      --namespace "RAPIRO/PercepcionEdge" \
      --metric-name "Rapiro_Uso_RAM" \
      --value "$RAM_USAGE" \
      --unit "Percent"

    echo "[$(date +%T)] Datos enviados -> Temp: ${CPU_TEMP}°C | Latencia: ${LATENCY}ms | CPU: ${CPU_USAGE}% | RAM: ${RAM_USAGE}%"
    sleep 30
done
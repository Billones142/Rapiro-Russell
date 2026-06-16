#!/bin/bash
# Configura el perfil para que la CLI local use las credenciales del compañero
export AWS_DEFAULT_REGION="sa-east-1"

while true; do
    # 1. Extraer temperatura de la Raspberry Pi en miligrados y pasar a Celsius
    RAW_TEMP=$(cat /sys/class/thermal/thermal_zone0/temp)
    CPU_TEMP=$(echo "scale=2; $RAW_TEMP / 1000" | bc)

    # 2. Medir latencia de red haciendo ping al backend de AWS (IP interna o gateway)
    LATENCY=$(ping -c 1 31.13.192.1 | diregex | awk -F '/' 'END {print $5}')
    if [ -z "$LATENCY" ]; then LATENCY=0; fi

    # 3. Enviar temperatura a AWS CloudWatch bajo un namespace personalizado
    aws cloudwatch put-metric-data \
      --namespace "RAPIRO/PercepcionEdge" \
      --metric-name "Temperatura_CPU" \
      --value "$CPU_TEMP" \
      --unit "Count"

    # 4. Enviar latencia de red a AWS CloudWatch
    aws cloudwatch put-metric-data \
      --namespace "RAPIRO/PercepcionEdge" \
      --metric-name "Latencia_Red_Cloud" \
      --value "$LATENCY" \
      --unit "Milliseconds"

    echo "Métricas enviadas: Temp=$CPU_TEMP°C, Latencia=${LATENCY}ms. Durmiendo 60s..."
    sleep 60
done
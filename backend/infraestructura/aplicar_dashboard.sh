aws cloudwatch put-dashboard \
  --dashboard-name "SEADD-Monitoreo-Clinico" \
  --dashboard-body '{
    "widgets": [
      {
        "type": "metric",
        "x": 0,
        "y": 0,
        "width": 12,
        "height": 6,
        "properties": {
          "metrics": [
            [ "RAPIRO/PercepcionEdge", "Temperatura_CPU" ]
          ],
          "period": 60,
          "stat": "Maximum",
          "region": "sa-east-1",
          "title": "🌡️ RAPIRO - Temperatura CPU (°C)"
        }
      },
      {
        "type": "metric",
        "x": 12,
        "y": 0,
        "width": 12,
        "height": 6,
        "properties": {
          "metrics": [
            [ "RAPIRO/PercepcionEdge", "Latencia_Red_Cloud" ]
          ],
          "period": 60,
          "stat": "Average",
          "region": "sa-east-1",
          "title": "⚡ RAPIRO - Latencia Edge-to-Cloud (ms)"
        }
      },
      {
        "type": "metric",
        "x": 0,
        "y": 6,
        "width": 12,
        "height": 6,
        "properties": {
          "metrics": [
            [ "RAPIRO/PercepcionEdge", "Rapiro_Uso_CPU" ]
          ],
          "period": 60,
          "stat": "Average",
          "region": "sa-east-1",
          "title": "📊 RAPIRO - Uso de CPU (%)",
          "view": "timeSeries",
          "stacked": false,
          "yAxis": { "left": { "max": 100, "min": 0 } }
        }
      },
      {
        "type": "metric",
        "x": 12,
        "y": 6,
        "width": 12,
        "height": 6,
        "properties": {
          "metrics": [
            [ "RAPIRO/PercepcionEdge", "Rapiro_Uso_RAM" ]
          ],
          "period": 60,
          "stat": "Average",
          "region": "sa-east-1",
          "title": "🧠 RAPIRO - Uso de Memoria RAM (%)",
          "view": "timeSeries",
          "stacked": false,
          "yAxis": { "left": { "max": 100, "min": 0 } }
        }
      }
    ]
  }' \
  --region sa-east-1
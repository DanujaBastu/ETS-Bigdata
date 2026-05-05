# Start ETS WeatherPulse Pipeline

Write-Host "===============================================" -ForegroundColor Cyan
Write-Host "Starting ETS WeatherPulse Data Pipeline" -ForegroundColor Cyan
Write-Host "===============================================" -ForegroundColor Cyan

Write-Host "`nActivating Python virtual environment..." -ForegroundColor Yellow
& ".\.venv\Scripts\Activate.ps1"

Write-Host "`nStopping any existing producer/consumer processes..." -ForegroundColor Yellow
Get-Process python -ErrorAction SilentlyContinue | Stop-Process -Force -ErrorAction SilentlyContinue
Write-Host "Old processes stopped" -ForegroundColor Green

Write-Host "`nStarting Producer (API)..." -ForegroundColor Yellow
Start-Process -FilePath python -ArgumentList "kafka/producer_api.py" -NoNewWindow
Write-Host "Producer API started" -ForegroundColor Green
Start-Sleep -Seconds 2

Write-Host "`nStarting Consumer (HDFS Writer)..." -ForegroundColor Yellow
Start-Process -FilePath python -ArgumentList "kafka/consumer_to_hdfs.py" -NoNewWindow
Write-Host "Consumer started" -ForegroundColor Green

Write-Host "`nWaiting 30 seconds for data to accumulate..." -ForegroundColor Yellow
for ($i = 30; $i -gt 0; $i--) {
    Write-Host "  $i seconds remaining..." -ForegroundColor Cyan
    Start-Sleep -Seconds 1
}

Write-Host "`nVerifying data in HDFS..." -ForegroundColor Yellow
docker exec namenode hdfs dfs -ls -R /data/weather/

Write-Host "`nPipeline ready!" -ForegroundColor Green

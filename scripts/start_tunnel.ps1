# Start Localhost.run Tunnel
# Simple SSH-based tunnel that bypasses firewall issues

Write-Host "`n================================" -ForegroundColor Cyan
Write-Host "🌐 Localhost.run Tunnel Starter" -ForegroundColor Cyan
Write-Host "================================`n" -ForegroundColor Cyan

Write-Host "📋 Instructions:" -ForegroundColor Yellow
Write-Host "1. Make sure your server is running (python run.py)" -ForegroundColor White
Write-Host "2. This will create a public HTTPS URL" -ForegroundColor White
Write-Host "3. Copy the URL shown and use it for webhooks`n" -ForegroundColor White

Write-Host "🚀 Starting tunnel to localhost:8000...`n" -ForegroundColor Green

# Start SSH tunnel
ssh -o StrictHostKeyChecking=no -R 80:localhost:8000 nokey@localhost.run

Write-Host "`n✅ Tunnel stopped" -ForegroundColor Green

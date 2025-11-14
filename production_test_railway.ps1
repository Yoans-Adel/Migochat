# Railway Production Testing Script
# Tests: https://migochat-production.up.railway.app/

$BaseUrl = "https://migochat-production.up.railway.app"
$TestResults = @()

Write-Host "🚂 Railway Production Testing Started" -ForegroundColor Cyan
Write-Host "URL: $BaseUrl" -ForegroundColor Yellow
Write-Host ""

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Path,
        [hashtable]$Query = @{},
        [int]$ExpectedStatus = 200
    )
    
    $url = "$BaseUrl$Path"
    if ($Query.Count -gt 0) {
        $queryString = ($Query.GetEnumerator() | ForEach-Object { "$($_.Key)=$($_.Value)" }) -join "&"
        $url = "$url`?$queryString"
    }
    
    try {
        $response = Invoke-WebRequest -Uri $url -Method Get -TimeoutSec 10
        $status = $response.StatusCode
        $size = $response.Content.Length
        $success = $status -eq $ExpectedStatus
        
        if ($success) {
            Write-Host "✅ $Name" -ForegroundColor Green
            Write-Host "   Status: $status | Size: $([math]::Round($size/1024,2)) KB" -ForegroundColor Gray
        } else {
            Write-Host "❌ $Name" -ForegroundColor Red
            Write-Host "   Expected: $ExpectedStatus | Got: $status" -ForegroundColor Gray
        }
        
        $script:TestResults += [PSCustomObject]@{
            Name = $Name
            Path = $Path
            Status = $status
            Expected = $ExpectedStatus
            Success = $success
            Size = $size
        }
        
        return $success
    } catch {
        Write-Host "❌ $Name - ERROR" -ForegroundColor Red
        Write-Host "   $($_.Exception.Message)" -ForegroundColor Gray
        
        $script:TestResults += [PSCustomObject]@{
            Name = $Name
            Path = $Path
            Status = 0
            Expected = $ExpectedStatus
            Success = $false
            Size = 0
        }
        
        return $false
    }
}

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🏥 Health & Status Endpoints" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Test-Endpoint "Health Check" "/health"
Test-Endpoint "Home Page" "/"
Test-Endpoint "Dashboard Home" "/dashboard/"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📊 Dashboard & CRM Endpoints" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Test-Endpoint "CRM Page" "/dashboard/crm"
Test-Endpoint "Messages Page" "/dashboard/messages"
Test-Endpoint "Leads Page" "/dashboard/leads"
Test-Endpoint "Users Page" "/dashboard/users"
Test-Endpoint "Settings Page" "/dashboard/settings"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🔌 API Endpoints" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Test-Endpoint "API Users" "/api/users"
Test-Endpoint "API Messages" "/api/messages"
Test-Endpoint "API Leads" "/api/leads"
Test-Endpoint "API Stats" "/api/stats"

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "🪝 Webhook Verification Endpoints" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

Test-Endpoint "Messenger Webhook" "/webhook/messenger" @{
    "hub.mode" = "subscribe"
    "hub.challenge" = "test123"
    "hub.verify_token" = "BWW_MESSENGER_VERIFY_TOKEN_2025"
}

Test-Endpoint "WhatsApp Webhook" "/webhook/whatsapp" @{
    "hub.mode" = "subscribe"
    "hub.challenge" = "test123"
    "hub.verify_token" = "BWW_WHATSAPP_VERIFY_TOKEN_2025"
}

Test-Endpoint "Lead Center Webhook" "/webhook/leadgen" @{
    "hub.mode" = "subscribe"
    "hub.challenge" = "test123"
    "hub.verify_token" = "BWW_LEADCENTER_VERIFY_TOKEN_2025"
}

Write-Host ""
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "📈 Test Summary" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan

$TotalTests = $TestResults.Count
$PassedTests = ($TestResults | Where-Object { $_.Success }).Count
$FailedTests = $TotalTests - $PassedTests
$PassRate = [math]::Round(($PassedTests / $TotalTests) * 100, 2)

Write-Host ""
Write-Host "Total Tests:  $TotalTests" -ForegroundColor White
Write-Host "Passed:       $PassedTests" -ForegroundColor Green
Write-Host "Failed:       $FailedTests" -ForegroundColor $(if ($FailedTests -eq 0) { "Green" } else { "Red" })
Write-Host "Pass Rate:    $PassRate%" -ForegroundColor $(if ($PassRate -eq 100) { "Green" } else { "Yellow" })
Write-Host ""

# Export results
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$reportPath = "F:\working - yoans\Migochat\tests\production_test_results_$timestamp.json"
$TestResults | ConvertTo-Json -Depth 5 | Out-File $reportPath -Encoding UTF8
Write-Host "📄 Results saved to: $reportPath" -ForegroundColor Cyan

if ($PassRate -eq 100) {
    Write-Host ""
    Write-Host "🎉 ALL TESTS PASSED! Production is healthy ✅" -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "⚠️  Some tests failed. Review the results above." -ForegroundColor Yellow
}

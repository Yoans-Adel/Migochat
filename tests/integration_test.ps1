# Integration Testing Script for Migochat
# Tests all critical endpoints and functionality

Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "🧪 Migochat Integration Test Suite" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$baseUrl = "http://localhost:8000"
$testResults = @()

function Test-Endpoint {
    param(
        [string]$Name,
        [string]$Url,
        [string]$Method = "GET",
        [object]$Body = $null,
        [string]$ExpectedStatus = "200"
    )
    
    Write-Host "Testing: $Name..." -NoNewline
    
    try {
        $params = @{
            Uri = "$baseUrl$Url"
            Method = $Method
            ErrorAction = 'Stop'
        }
        
        if ($Body) {
            $params['Body'] = ($Body | ConvertTo-Json)
            $params['ContentType'] = 'application/json'
        }
        
        $response = Invoke-WebRequest @params
        
        if ($response.StatusCode -eq $ExpectedStatus) {
            Write-Host " ✅ PASS" -ForegroundColor Green
            $script:testResults += [PSCustomObject]@{
                Test = $Name
                Status = "PASS"
                StatusCode = $response.StatusCode
                ContentLength = $response.Content.Length
            }
            return $true
        } else {
            Write-Host " ❌ FAIL (Expected $ExpectedStatus, got $($response.StatusCode))" -ForegroundColor Red
            $script:testResults += [PSCustomObject]@{
                Test = $Name
                Status = "FAIL"
                StatusCode = $response.StatusCode
                Error = "Unexpected status code"
            }
            return $false
        }
    }
    catch {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        Write-Host "   Error: $($_.Exception.Message)" -ForegroundColor Red
        $script:testResults += [PSCustomObject]@{
            Test = $Name
            Status = "FAIL"
            Error = $_.Exception.Message
        }
        return $false
    }
}

# Check if server is running
Write-Host "`n📡 Checking server status..." -ForegroundColor Yellow
try {
    $null = Invoke-WebRequest -Uri "$baseUrl/health" -Method GET -ErrorAction Stop
    Write-Host "✅ Server is running`n" -ForegroundColor Green
}
catch {
    Write-Host "❌ Server is not running!" -ForegroundColor Red
    Write-Host "Please start the server with: python run.py" -ForegroundColor Yellow
    exit 1
}

# Core API Tests
Write-Host "`n🔍 Testing Core API Endpoints" -ForegroundColor Yellow
Write-Host "--------------------------------`n"

Test-Endpoint -Name "Health Check" -Url "/health"
Test-Endpoint -Name "Root Redirect" -Url "/"
Test-Endpoint -Name "Users API" -Url "/api/users"
Test-Endpoint -Name "Messages API" -Url "/api/messages"
Test-Endpoint -Name "Leads API" -Url "/api/leads"

# Dashboard Tests
Write-Host "`n📊 Testing Dashboard Pages" -ForegroundColor Yellow
Write-Host "--------------------------------`n"

Test-Endpoint -Name "Main Dashboard" -Url "/dashboard/"
Test-Endpoint -Name "CRM Dashboard" -Url "/dashboard/crm"
Test-Endpoint -Name "Settings Page" -Url "/dashboard/settings"

# Webhook Tests (GET for verification)
Write-Host "`n🔗 Testing Webhook Endpoints" -ForegroundColor Yellow
Write-Host "--------------------------------`n"

# Facebook Messenger Webhook Verification
$verifyToken = "BWW_MESSENGER_VERIFY_TOKEN_2025"
Test-Endpoint -Name "Messenger Webhook Verify" `
    -Url "/webhook/messenger?hub.mode=subscribe&hub.challenge=test123&hub.verify_token=$verifyToken"

# WhatsApp Webhook Verification
$waToken = "BWW_WHATSAPP_VERIFY_TOKEN_2025"
Test-Endpoint -Name "WhatsApp Webhook Verify" `
    -Url "/webhook/whatsapp?hub.mode=subscribe&hub.challenge=test456&hub.verify_token=$waToken"

# Lead Center Webhook Verification
$leadToken = "BWW_LEADCENTER_VERIFY_TOKEN_2025"
Test-Endpoint -Name "Lead Center Webhook Verify" `
    -Url "/webhook/leadgen?hub.mode=subscribe&hub.challenge=test789&hub.verify_token=$leadToken"

# Static Files Tests
Write-Host "`n📁 Testing Static Resources" -ForegroundColor Yellow
Write-Host "--------------------------------`n"

Test-Endpoint -Name "CSS - Dashboard Styles" -Url "/static/css/dashboard.css"
Test-Endpoint -Name "JS - CRM Scripts" -Url "/static/js/crm.js"

# Database Tests
Write-Host "`n💾 Testing Database Operations" -ForegroundColor Yellow
Write-Host "--------------------------------`n"

try {
    Write-Host "Testing database connectivity..." -NoNewline
    python -c "from config.database_config import check_database_health; result = check_database_health(); exit(0 if result.get('status') == 'healthy' else 1)" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $testResults += [PSCustomObject]@{
            Test = "Database Health"
            Status = "PASS"
        }
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $testResults += [PSCustomObject]@{
            Test = "Database Health"
            Status = "FAIL"
        }
    }
}
catch {
    Write-Host " ❌ FAIL" -ForegroundColor Red
}

# Configuration Tests
Write-Host "`n⚙️ Testing Configuration" -ForegroundColor Yellow
Write-Host "--------------------------------`n"

try {
    Write-Host "Testing settings import..." -NoNewline
    python -c "from config.settings import settings; assert settings.ENVIRONMENT; exit(0)" 2>$null
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host " ✅ PASS" -ForegroundColor Green
        $testResults += [PSCustomObject]@{
            Test = "Settings Import"
            Status = "PASS"
        }
    } else {
        Write-Host " ❌ FAIL" -ForegroundColor Red
        $testResults += [PSCustomObject]@{
            Test = "Settings Import"
            Status = "FAIL"
        }
    }
}
catch {
    Write-Host " ❌ FAIL" -ForegroundColor Red
}

# Summary
Write-Host "`n========================================" -ForegroundColor Cyan
Write-Host "📋 Test Summary" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

$passed = ($testResults | Where-Object { $_.Status -eq "PASS" }).Count
$failed = ($testResults | Where-Object { $_.Status -eq "FAIL" }).Count
$total = $testResults.Count

Write-Host "Total Tests: $total" -ForegroundColor White
Write-Host "Passed: $passed" -ForegroundColor Green
Write-Host "Failed: $failed" -ForegroundColor Red
Write-Host "Success Rate: $([math]::Round(($passed / $total) * 100, 2))%`n" -ForegroundColor Cyan

# Detailed Results Table
$testResults | Format-Table -AutoSize

if ($failed -eq 0) {
    Write-Host "`n✨ All tests passed! System is production ready.`n" -ForegroundColor Green
    exit 0
} else {
    Write-Host "`n⚠️ Some tests failed. Please review the results above.`n" -ForegroundColor Yellow
    exit 1
}

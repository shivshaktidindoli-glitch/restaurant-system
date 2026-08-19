$url = "https://restaurant-system-wfwb.onrender.com/api/place_order"
$json = @{
    table_name = "T-1"
    customer_name = "Speed Test"
    customer_mobile = "9999999999"
    items = @(
        @{ id = 1; name = "Test Item"; price = 100; quantity = 1 }
    )
    order_type = "dine-in"
} | ConvertTo-Json

Write-Host "Sending Place Order request with intentionally broken WhatsApp backend..."
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    $res = Invoke-RestMethod -Uri $url -Method POST -Body $json -ContentType "application/json"
    $stopwatch.Stop()
    Write-Host "SUCCESS!"
    Write-Host "Time taken: $($stopwatch.Elapsed.TotalSeconds) seconds"
    Write-Host "Response: $($res | ConvertTo-Json -Compress)"
} catch {
    $stopwatch.Stop()
    Write-Host "FAILED!"
    Write-Host "Time taken: $($stopwatch.Elapsed.TotalSeconds) seconds"
    Write-Host "Error: $_"
}

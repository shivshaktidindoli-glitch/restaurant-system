$url = "https://restaurant-system-wfwb.onrender.com/api/speed_test"
$stopwatch = [System.Diagnostics.Stopwatch]::StartNew()
try {
    $res = Invoke-RestMethod -Uri $url -Method GET
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

# 端口释放
$port = 8000
$pids = (Get-NetTCPConnection -LocalPort $port -ErrorAction SilentlyContinue | Select-Object -ExpandProperty OwningProcess -Unique)
foreach ($pid in $pids) {
    Stop-Process -Id $pid -Force -ErrorAction SilentlyContinue
    Write-Host "已释放端口 $port (PID $pid)"
    Start-Sleep 1
}

# 启动
uvicorn main:app --reload --host 0.0.0.0 --port $port

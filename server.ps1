# Azure Tower - Multi-Threaded HTTP Server
$port = 3000
$url = "http://127.0.0.1:$port/"
$folder = $PSScriptRoot

$listener = New-Object System.Net.HttpListener
$listener.Prefixes.Add($url)

try {
    $listener.Start()
} catch {
    Write-Host "[XƏTA] Port $port artıq istifadədədir: $_" -ForegroundColor Red
    pause
    exit 1
}

Write-Host "==========================================================" -ForegroundColor Cyan
Write-Host "  AZURE TOWER - 3D DAŞINMAZ ƏMLAK SİSTEMİ İŞƏ DÜŞDÜ!      " -ForegroundColor Green
Write-Host "  Ünvan: $url" -ForegroundColor Yellow
Write-Host "  Server multi-threaded rejimdə aktivdir.                 " -ForegroundColor Gray
Write-Host "==========================================================" -ForegroundColor Cyan

$mimeTypes = @{
    ".html" = "text/html; charset=utf-8"
    ".htm"  = "text/html; charset=utf-8"
    ".js"   = "application/javascript; charset=utf-8"
    ".css"  = "text/css; charset=utf-8"
    ".json" = "application/json; charset=utf-8"
    ".glb"  = "model/gltf-binary"
    ".gltf" = "model/gltf+json"
    ".bin"  = "application/octet-stream"
    ".png"  = "image/png"
    ".jpg"  = "image/jpeg"
    ".jpeg" = "image/jpeg"
    ".svg"  = "image/svg+xml"
    ".ico"  = "image/x-icon"
    ".wasm" = "application/wasm"
}

function ProcessRequest($context) {
    try {
        $req = $context.Request
        $res = $context.Response

        $path = $req.Url.LocalPath
        if ($path -eq "/" -or $path -eq "") {
            $path = "/index.html"
        }

        $decoded = [System.Uri]::UnescapeDataString($path).TrimStart("/").Replace("/", "\")
        $filePath = Join-Path $folder $decoded

        # CORS
        $res.Headers.Add("Access-Control-Allow-Origin", "*")
        $res.Headers.Add("Access-Control-Allow-Methods", "GET, POST, OPTIONS, HEAD")
        $res.Headers.Add("Access-Control-Allow-Headers", "*")

        if ($req.HttpMethod -eq "OPTIONS") {
            $res.StatusCode = 200
            $res.Close()
            return
        }

        if (Test-Path $filePath -PathType Leaf) {
            $ext = [System.IO.Path]::GetExtension($filePath).ToLower()
            $contentType = "application/octet-stream"
            if ($mimeTypes.ContainsKey($ext)) {
                $contentType = $mimeTypes[$ext]
            }
            $res.ContentType = $contentType
            $res.StatusCode = 200

            $fi = New-Object System.IO.FileInfo($filePath)
            $res.ContentLength64 = $fi.Length

            if ($req.HttpMethod -ne "HEAD") {
                $fs = [System.IO.File]::OpenRead($filePath)
                try {
                    $fs.CopyTo($res.OutputStream)
                } finally {
                    $fs.Dispose()
                }
            }
        } else {
            $res.StatusCode = 404
            $msg = [System.Text.Encoding]::UTF8.GetBytes("404 Fayl Tapılmadı: $path")
            $res.ContentType = "text/plain; charset=utf-8"
            $res.ContentLength64 = $msg.Length
            if ($req.HttpMethod -ne "HEAD") {
                $res.OutputStream.Write($msg, 0, $msg.Length)
            }
        }
    } catch {
        # Client abort or disconnect handled silently
    } finally {
        try { $context.Response.Close() } catch {}
    }
}

try {
    while ($listener.IsListening) {
        $ctx = $listener.GetContext()
        [System.Threading.ThreadPool]::QueueUserWorkItem({
            param($c)
            ProcessRequest $c
        }, $ctx) | Out-Null
    }
} finally {
    $listener.Stop()
    $listener.Close()
    Write-Host "`nServer dayandırıldı." -ForegroundColor Yellow
}

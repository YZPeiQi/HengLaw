Add-Type -AssemblyName System.Drawing
Add-Type -AssemblyName System.Runtime.InteropServices

$src = "frontend/public/brand/logo-transparent.png"
$dst = "frontend/public/brand/logo-transparent.png"

$bmpSrc = New-Object System.Drawing.Bitmap($src)
$bmp = New-Object System.Drawing.Bitmap($bmpSrc.Width, $bmpSrc.Height, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$g = [System.Drawing.Graphics]::FromImage($bmp)
$g.DrawImage($bmpSrc, 0, 0, $bmpSrc.Width, $bmpSrc.Height)
$g.Dispose()
$bmpSrc.Dispose()

$w = $bmp.Width
$h = $bmp.Height
$rect = New-Object System.Drawing.Rectangle(0, 0, $w, $h)
$data = $bmp.LockBits($rect, [System.Drawing.Imaging.ImageLockMode]::ReadWrite, [System.Drawing.Imaging.PixelFormat]::Format32bppArgb)
$stride = $data.Stride
$bytes = [Math]::Abs($stride) * $h
$arr = New-Object byte[] $bytes
[System.Runtime.InteropServices.Marshal]::Copy($data.Scan0, $arr, 0, $bytes)

function PIdx([int]$x, [int]$y, [int]$stride) {
  return $y * $stride + $x * 4
}

$sumR = 0.0
$sumG = 0.0
$sumB = 0.0
$count = 0

for ($x = 0; $x -lt $w; $x++) {
  foreach ($y in @(0, ($h - 1))) {
    $i = PIdx $x $y $stride
    if ($arr[$i + 3] -gt 0) {
      $sumB += $arr[$i]
      $sumG += $arr[$i + 1]
      $sumR += $arr[$i + 2]
      $count++
    }
  }
}

for ($y = 1; $y -lt ($h - 1); $y++) {
  foreach ($x in @(0, ($w - 1))) {
    $i = PIdx $x $y $stride
    if ($arr[$i + 3] -gt 0) {
      $sumB += $arr[$i]
      $sumG += $arr[$i + 1]
      $sumR += $arr[$i + 2]
      $count++
    }
  }
}

if ($count -eq 0) { $count = 1 }
$bgR = [double]($sumR / $count)
$bgG = [double]($sumG / $count)
$bgB = [double]($sumB / $count)
$tol = 62.0

$visited = New-Object bool[] ($w * $h)
$q = New-Object 'System.Collections.Generic.Queue[int]'

function Idx([int]$x, [int]$y, [int]$w) {
  return $y * $w + $x
}

function IsBg([int]$x, [int]$y, [byte[]]$arr, [int]$stride, [double]$bgR, [double]$bgG, [double]$bgB, [double]$tol) {
  $pi = PIdx $x $y $stride
  if ($arr[$pi + 3] -eq 0) {
    return $true
  }

  $r = [double]$arr[$pi + 2]
  $g = [double]$arr[$pi + 1]
  $b = [double]$arr[$pi]

  $dr = $r - $bgR
  $dg = $g - $bgG
  $db = $b - $bgB
  $dist = [Math]::Sqrt($dr * $dr + $dg * $dg + $db * $db)

  return ($dist -le $tol -and ($r + $g + $b) -le 230)
}

for ($x = 0; $x -lt $w; $x++) {
  foreach ($y in @(0, ($h - 1))) {
    $id = Idx $x $y $w
    if ((-not $visited[$id]) -and (IsBg $x $y $arr $stride $bgR $bgG $bgB $tol)) {
      $visited[$id] = $true
      $q.Enqueue($id)
    }
  }
}

for ($y = 1; $y -lt ($h - 1); $y++) {
  foreach ($x in @(0, ($w - 1))) {
    $id = Idx $x $y $w
    if ((-not $visited[$id]) -and (IsBg $x $y $arr $stride $bgR $bgG $bgB $tol)) {
      $visited[$id] = $true
      $q.Enqueue($id)
    }
  }
}

$removed = 0
while ($q.Count -gt 0) {
  $id = $q.Dequeue()
  $x = $id % $w
  $y = [int]($id / $w)
  $pi = PIdx $x $y $stride

  if ($arr[$pi + 3] -ne 0) {
    $arr[$pi + 3] = 0
    $removed++
  }

  foreach ($n in @(@(($x - 1), $y), @(($x + 1), $y), @($x, ($y - 1)), @($x, ($y + 1)))) {
    $nx = $n[0]
    $ny = $n[1]

    if ($nx -ge 0 -and $nx -lt $w -and $ny -ge 0 -and $ny -lt $h) {
      $nid = Idx $nx $ny $w
      if ((-not $visited[$nid]) -and (IsBg $nx $ny $arr $stride $bgR $bgG $bgB $tol)) {
        $visited[$nid] = $true
        $q.Enqueue($nid)
      }
    }
  }
}

[System.Runtime.InteropServices.Marshal]::Copy($arr, 0, $data.Scan0, $bytes)
$bmp.UnlockBits($data)
$bmp.Save($dst, [System.Drawing.Imaging.ImageFormat]::Png)
$bmp.Dispose()

Write-Output "saved=$dst bg=($([int]$bgR),$([int]$bgG),$([int]$bgB)) removed=$removed"

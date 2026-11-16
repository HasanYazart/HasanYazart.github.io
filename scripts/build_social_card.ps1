# Original code-drawn typography asset; no external images or invented project output.
Add-Type -AssemblyName System.Drawing
$cardRoot = Split-Path -Parent $PSScriptRoot
$bitmap = New-Object System.Drawing.Bitmap(1200, 630)
$canvas = [System.Drawing.Graphics]::FromImage($bitmap)
$canvas.SmoothingMode = [System.Drawing.Drawing2D.SmoothingMode]::AntiAlias
$canvas.TextRenderingHint = [System.Drawing.Text.TextRenderingHint]::AntiAliasGridFit
$background = [System.Drawing.ColorTranslator]::FromHtml('#19191f')
$lavender = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#bbb2f5'))
$white = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#f5f4f1'))
$muted = New-Object System.Drawing.SolidBrush([System.Drawing.ColorTranslator]::FromHtml('#b8b4c8'))
$canvas.Clear($background)
$canvas.FillRectangle($lavender, 72, 73, 50, 3)
$small = New-Object System.Drawing.Font('Segoe UI', 24, [System.Drawing.FontStyle]::Regular, [System.Drawing.GraphicsUnit]::Pixel)
$nameFont = New-Object System.Drawing.Font('Segoe UI', 76, [System.Drawing.FontStyle]::Bold, [System.Drawing.GraphicsUnit]::Pixel)
$titleFont = New-Object System.Drawing.Font('Georgia', 64, [System.Drawing.FontStyle]::Italic, [System.Drawing.GraphicsUnit]::Pixel)
$canvas.DrawString('SOFTWARE DEVELOPMENT & AI', $small, $lavender, 144, 55)
$canvas.DrawString('Hasan Yazar', $nameFont, $white, 66, 175)
$canvas.DrawString('From idea to working product.', $titleFont, $lavender, 68, 285)
$canvas.DrawString('Projects / Research / Systems', $small, $muted, 72, 453)
$canvas.DrawString('hasanyazart.github.io', $small, $white, 72, 548)
$pen = New-Object System.Drawing.Pen([System.Drawing.ColorTranslator]::FromHtml('#494352'), 1)
$canvas.DrawLine($pen, 72, 515, 1128, 515)
$bitmap.Save((Join-Path $cardRoot 'assets/social-card.png'), [System.Drawing.Imaging.ImageFormat]::Png)
$pen.Dispose(); $small.Dispose(); $nameFont.Dispose(); $titleFont.Dispose()
$lavender.Dispose(); $white.Dispose(); $muted.Dispose(); $canvas.Dispose(); $bitmap.Dispose()
Write-Output 'Created 1200 x 630 social card.'

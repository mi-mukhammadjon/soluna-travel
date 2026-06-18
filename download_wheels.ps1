# Wheels papkasini yaratish
New-Item -ItemType Directory -Force -Path .\wheels | Out-Null

# Linux uchun binary wheels yuklab olish
pip download `
  --only-binary :all: `
  --platform manylinux_2_17_x86_64 `
  --python-version 3.11 `
  --implementation cp `
  --abi cp311 `
  -r requirements.txt `
  -d .\wheels

Write-Host "Yuklab olindi: $(Get-ChildItem .\wheels\*.whl | Measure-Object | Select-Object -ExpandProperty Count) ta wheel fayl"

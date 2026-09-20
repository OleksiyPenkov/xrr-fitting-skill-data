# Skill qualification test, stage 1 (2026-09-18/19): a fresh headless session gets ONLY the task header and the
# skill text, and the xrc tools on an isolated workdir holding one curve. No reference numbers.
# usage: .\run-skilltest.ps1 -Tag T05 -Model claude-sonnet-5 -Task prompt-T05-task.md -Skill ..\brief\manual\xrr-fitting-skill.md [-MaxTurns 2500]
param(
  [Parameter(Mandatory)] [string] $Tag,
  [string] $Model = "claude-sonnet-5",
  [Parameter(Mandatory)] [string] $Task,
  [Parameter(Mandatory)] [string] $Skill,
  [int] $MaxTurns = 2500
)
$dir = "D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments\skill-dev-2026-09-18"
Set-Location $dir
$prompt = Join-Path $dir "prompt-$Tag-as-sent.md"
$mcp = Join-Path $dir "mcp.skilltest-$Tag.json"
(Get-Content -Raw $Task) + "`n`n---`n`n" + (Get-Content -Raw $Skill) | Set-Content -Encoding utf8 -NoNewline $prompt
Add-Content -Path (Join-Path $dir "skilltest-started.txt") -Value ("{0} {1} launched, model {2}, max-turns {3}" -f (Get-Date -Format s), $Tag, $Model, $MaxTurns)
$env:MCP_TOOL_TIMEOUT = "900000"   # ms; job_wait blocks up to 300 s per call (XRC 2accc0c)
$stream = Join-Path $dir "stream-$Tag.jsonl"
$stderr = Join-Path $dir "stderr-$Tag.txt"
Get-Content -Raw $prompt | claude -p --strict-mcp-config --mcp-config $mcp --tools "" --allowedTools mcp__xrc --model $Model --max-turns $MaxTurns --output-format stream-json --verbose > $stream 2> $stderr
Add-Content -Path (Join-Path $dir "skilltest-started.txt") -Value ("{0} {1} exited {2}" -f (Get-Date -Format s), $Tag, $LASTEXITCODE)

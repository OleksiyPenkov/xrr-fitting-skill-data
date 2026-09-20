
# Independent verification of X-Ray Calc 02e7b63: cross-engine agreement, design-v4, and the
# Co/C vs Ni/C comparison now computed natively instead of by the sigma/sqrt2 emulation.
$ErrorActionPreference='Stop'
$Exe='D:\DelphiProjects\X-RayCalc\X-RayCalc3_Working\_Out\BIN\XRC_MCP.exe'
$W=Join-Path $env:TEMP 'xrc-verify02'; if(Test-Path $W){Remove-Item $W -Recurse -Force}
New-Item -ItemType Directory (Join-Path $W 'projects')|Out-Null
Copy-Item 'D:\MultilayerLab\Papers\LLM-XRay-Optics-Lab\experiments\runs\exp-02\workdir\projects\design-v4.xrcx' (Join-Path $W 'projects') -Force
$psi=[System.Diagnostics.ProcessStartInfo]::new(); $psi.FileName=$Exe; $psi.Arguments='--workdir "'+$W+'"'
$psi.UseShellExecute=$false; $psi.RedirectStandardInput=$true; $psi.RedirectStandardOutput=$true
$psi.StandardInputEncoding=[System.Text.UTF8Encoding]::new($false); $psi.StandardOutputEncoding=[System.Text.UTF8Encoding]::new($false)
$P=[System.Diagnostics.Process]::Start($psi); $script:Id=0
function S($m,$pa,[switch]$N){ $r=[ordered]@{jsonrpc='2.0'}; if(-not $N){$script:Id++; $r['id']=$script:Id}; $r['method']=$m; if($pa){$r['params']=$pa}
  $P.StandardInput.WriteLine(($r|ConvertTo-Json -Depth 30 -Compress)); $P.StandardInput.Flush(); if($N){return}
  $t=$P.StandardOutput.ReadLineAsync(); $t.Wait(300000)|Out-Null; $t.Result|ConvertFrom-Json }
function T($n,$a){ $r=S 'tools/call' @{name=$n;arguments=$a}; $txt=$r.result.content[0].text
  if($r.result.PSObject.Properties['isError'] -and $r.result.isError){throw $txt}; ($txt|ConvertFrom-Json) }
S 'initialize' @{protocolVersion='2024-11-05';capabilities=@{};clientInfo=@{name='p';version='0'}}|Out-Null
S 'notifications/initialized' $null -N
"git_revision: " + (T 'describe_server' @{}).git_revision
$Lines=@('B','C','N','O','F','Na','Mg','Al','Si')

# --- 1. cross-engine agreement, window taken from evaluate_lines itself
function CoCs([double]$sig){ [ordered]@{ substrate=[ordered]@{material='SiO2';density=2.65;sigma=$sig}
    stacks=@([ordered]@{N=150;layers=@(
      [ordered]@{material='C';thickness=31.92;sigma=$sig;density=1.90},
      [ordered]@{material='Co';thickness=10.08;sigma=$sig;density=8.79})})
    cap=[ordered]@{material='C';thickness=12;sigma=$sig;density=1.90} } }
"--- cross-engine (calc_reflectivity max over the window evaluate_lines used) ---"
foreach($sig in 0.0,3.0,5.0){
  $st=CoCs $sig
  $ev=T 'evaluate_lines' ([ordered]@{structure=$st;lines=@('B','Na','Si')})
  foreach($L in $ev.lines){
    $h=$L.scan_half_deg; if(-not $h -or $h -le 0){$h=[math]::Max(3*$L.fwhm_deg,0.25)}
    $t0=[math]::Max(0.05,$L.theta_peak_deg-$h); $t1=$L.theta_peak_deg+$h
    $c=T 'calc_reflectivity' ([ordered]@{structure=$st;lambda=$L.lambda_used;theta_min=$t0;theta_max=$t1;step=(($t1-$t0)/4000);polarization='sp'})
    $mx=($c.curve|ForEach-Object{$_[1]}|Measure-Object -Maximum).Maximum
    '  {0,-3} sigma={1,4:0.0}  fitness={2:0.00000}  curve={3:0.00000}  diff={4,6:0.00} %' -f $L.name,$sig,$L.r_peak,$mx,(100*($mx-$L.r_peak)/$L.r_peak) } }

# --- 2. design-v4 exactly as the agent saved it
$p=T 'load_project' @{name='design-v4'}
$ev=T 'evaluate_lines' ([ordered]@{structure=$p.structure;lines=$Lines})
"--- design-v4 as saved: fom = " + $ev.fom
($ev.lines|ForEach-Object{ '  {0,-3} R={1:0.00000}  2theta={2,7:0.00}' -f $_.name,$_.r_peak,(2*$_.theta_peak_deg) })

# --- 3. Co/C against Ni/C at matched geometry, natively
function Pair([string]$m,[double]$rho,[double]$d,[double]$g){
  [ordered]@{ substrate=[ordered]@{material='SiO2';density=2.65;sigma=5}
    stacks=@([ordered]@{N=150;layers=@(
      [ordered]@{material='C';thickness=($d*(1-$g));sigma=5.5;density=1.90},
      [ordered]@{material=$m;thickness=($d*$g);sigma=3.0;density=$rho})})
    cap=[ordered]@{material='C';thickness=12;sigma=5.5;density=1.90} } }
function Row($lab,$s){ $e=T 'evaluate_lines' ([ordered]@{structure=$s;lines=$Lines})
  $b=($e.lines|Where-Object{$_.name -eq 'B'}); $n=($e.lines|Where-Object{$_.name -eq 'N'})
  $dark=@($e.lines|Where-Object{$_.r_peak -lt 0.02}).Count
  '  {0,-22} fom={1,8:0.000}  N={2:0.000}  dark={3}  B_2theta={4,6:0.0}' -f $lab,[double]$e.fom,[double]$n.r_peak,$dark,(2*[double]$b.theta_peak_deg) }
"--- Co/C vs Ni/C at matched geometry (corrected engine, native) ---"
foreach($d in 38.0,40.0,41.0,42.0,44.0){ foreach($g in 0.18,0.20,0.24){
  Row "Co/C d=$d G=$g" (Pair 'Co' 8.79 $d $g); Row "Ni/C d=$d G=$g" (Pair 'Ni' 8.90 $d $g) } ; "" }
$P.StandardInput.Close(); $P.WaitForExit(15000)|Out-Null

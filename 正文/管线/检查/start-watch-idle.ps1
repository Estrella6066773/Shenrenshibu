# 可选：启动「空闲自动退出」的链接监视（不提交也会在校存 .md 时检查）
# 关闭：等待无活动 30 分钟自动退出，或在本终端 Ctrl+C
$ErrorActionPreference = "Stop"
$root = git rev-parse --show-toplevel
if (-not $root) { throw "请在 Git 仓库内运行" }
Set-Location $root
python "正文/管线/检查/watch-links-idle.py" @args

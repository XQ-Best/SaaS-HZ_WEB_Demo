import { TEMU_API_BASE_URL } from '@/api/config'

const BAT_BOM = '\uFEFF'

function escapeBatValue(value = '') {
  return String(value).replace(/"/g, '""')
}

function resolveLauncherRoot() {
  const configured = import.meta.env.VITE_AGENT_LAUNCHER_ROOT
  if (configured) return configured.replace(/\//g, '\\')
  return 'D:\\NIUBI\\SaaS-HZ_WEB_Demo'
}

function resolveJavaApiUrl() {
  return TEMU_API_BASE_URL.replace(/\/$/, '')
}

function downloadTextFile(filename, content) {
  const blob = new Blob([`${BAT_BOM}${content}`], { type: 'text/plain;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = filename
  document.body.appendChild(link)
  link.click()
  link.remove()
  URL.revokeObjectURL(url)
}

function buildZiniaoSection() {
  return `echo [1/2] Starting Ziniao WebDriver (port 16851)...
echo       Quit normal Ziniao first, including the tray icon.
echo.
set "ZINIAO_EXE=C:\\Program Files\\ziniao\\ziniao.exe"
if not exist "%ZINIAO_EXE%" (
  echo [ERROR] Ziniao not found: %ZINIAO_EXE%
  echo         Ask IT to install the Ziniao client.
  pause
  exit /b 3
)
netstat -ano | findstr ":16851" | findstr "LISTENING" >nul
if errorlevel 1 (
  start "" "%ZINIAO_EXE%" --run_type=web_driver --ipc_type=http --port=16851
  echo Waiting for Ziniao WebDriver...
  timeout /t 8 /nobreak >nul
  netstat -ano | findstr ":16851" | findstr "LISTENING" >nul
  if errorlevel 1 (
    echo [ERROR] Port 16851 is not listening.
    echo         Quit normal Ziniao and enable WebDriver in Ziniao Boss settings.
    pause
    exit /b 4
  )
) else (
  echo Ziniao WebDriver is already running.
)
echo.`
}

function buildAgentSection({ agentToken, projectRoot, javaApiUrl }) {
  const root = escapeBatValue(projectRoot)
  const token = escapeBatValue(agentToken)
  const apiUrl = escapeBatValue(javaApiUrl)
  return `echo [2/2] Starting Amazon sync agent...
echo       Keep this window open. Closing it stops Amazon sync.
echo API: ${apiUrl}
echo Health check: http://127.0.0.1:18765/health
echo.
set "AGENT_TOKEN=${token}"
set "JAVA_API_URL=${apiUrl}"
set "AGENT_HEALTH_PORT=18765"
set "PYTHONPATH=${root}\\backend\\python"
cd /d "${root}"
where py >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Python not found. Install Python 3 and add it to PATH.
  pause
  exit /b 5
)
if not exist "${root}\\backend\\python\\scripts\\run_agent.py" (
  echo [ERROR] Agent script not found. Check project path: ${root}
  pause
  exit /b 6
)
:agent_loop
py "${root}\\backend\\python\\scripts\\run_agent.py"
if errorlevel 1 (
  echo.
  echo [WARN] Agent exited unexpectedly. Retrying in 5 seconds...
  timeout /t 5 /nobreak >nul
  goto agent_loop
)
echo.
echo Agent stopped.
pause`
}

function batHeader(title) {
  return `@echo off
setlocal EnableExtensions
chcp 65001 >nul 2>&1
title ${title}
`
}

export function buildZiniaoLauncherBat(projectRoot = resolveLauncherRoot()) {
  return `${batHeader('CrossHub Ziniao Launcher')}${buildZiniaoSection()}
echo.
echo Ziniao WebDriver is ready. Return to CrossHub and click Refresh Status.
pause
`
}

export function buildAmazonAgentLauncherBat({
  agentToken,
  projectRoot = resolveLauncherRoot(),
  javaApiUrl = resolveJavaApiUrl(),
}) {
  return `${batHeader('CrossHub Amazon Sync Agent')}${buildAgentSection({ agentToken, projectRoot, javaApiUrl })}
`
}

export function buildCombinedLauncherBat({
  agentToken,
  projectRoot = resolveLauncherRoot(),
  javaApiUrl = resolveJavaApiUrl(),
}) {
  return `${batHeader('CrossHub Amazon Sync Helper')}${buildZiniaoSection()}
echo.
${buildAgentSection({ agentToken, projectRoot, javaApiUrl })}
`
}

export function downloadZiniaoLauncher() {
  downloadTextFile('CrossHub-Ziniao-Launcher.bat', buildZiniaoLauncherBat())
}

export function downloadAmazonAgentLauncher(setupData) {
  const token = setupData?.agent_token || setupData?.token
  if (!token) {
    throw new Error('未获取到同步助手凭证')
  }
  downloadTextFile('CrossHub-Amazon-Sync-Agent.bat', buildAmazonAgentLauncherBat({ agentToken: token }))
}

export function downloadCombinedLauncher(setupData) {
  const token = setupData?.agent_token || setupData?.token
  if (!token) {
    throw new Error('未获取到同步助手凭证')
  }
  downloadTextFile(
    'CrossHub-Amazon-Sync-Helper.bat',
    buildCombinedLauncherBat({ agentToken: token }),
  )
}

export function getLauncherRootHint() {
  return resolveLauncherRoot()
}

@echo off
setlocal EnableExtensions EnableDelayedExpansion

rem =========================================================
rem CONFIGURACAO
rem =========================================================
set GITHUB_BASE_URL=https://github.seudominio.com/sua-org
set LOG_DIR=%~dp0logs
set TEMP_BASE=%TEMP%\RepoMigration

rem =========================================================
rem PREPARACAO
rem =========================================================
if not exist "%LOG_DIR%" mkdir "%LOG_DIR%" >nul 2>nul
if not exist "%TEMP_BASE%" mkdir "%TEMP_BASE%" >nul 2>nul

set YYYY=%date:~-4%
set MM=%date:~3,2%
set DD=%date:~0,2%
set HH=%time:~0,2%
set MN=%time:~3,2%
set SS=%time:~6,2%

if "%HH:~0,1%"==" " set HH=0%HH:~1,1%

set TS=%YYYY%%MM%%DD%_%HH%%MN%%SS%
set LOG_FILE=%LOG_DIR%\migracao_%TS%.log
set WORK_DIR=%TEMP_BASE%\repo_%RANDOM%_%RANDOM%
set REPO_DIR=%WORK_DIR%\repo.git

call :log =========================================================
call :log INICIO DA MIGRACAO
call :log LOG FILE: %LOG_FILE%
call :log WORK DIR: %WORK_DIR%
call :log =========================================================

rem =========================================================
rem VALIDAR GIT
rem =========================================================
where git >nul 2>nul
if errorlevel 1 (
    call :log ERRO: Git nao encontrado no PATH.
    echo.
    echo ERRO: Git nao encontrado no PATH.
    echo Verifique se o Git esta instalado e configurado.
    goto fail
)

call :log Git encontrado com sucesso.

rem =========================================================
rem ENTRADA DE DADOS
rem =========================================================
echo.
set /p SOURCE_URL=Informe a URL COMPLETA do repositorio de origem: 
if "%SOURCE_URL%"=="" (
    call :log ERRO: URL de origem nao informada.
    echo ERRO: URL de origem nao informada.
    goto fail
)

echo.
set /p NEW_REPO_NAME=Informe o nome do novo repositorio no GitHub: 
if "%NEW_REPO_NAME%"=="" (
    call :log ERRO: Nome do novo repositorio nao informado.
    echo ERRO: Nome do novo repositorio nao informado.
    goto fail
)

set TARGET_URL=%GITHUB_BASE_URL%/%NEW_REPO_NAME%.git

call :log SOURCE URL: %SOURCE_URL%
call :log TARGET URL: %TARGET_URL%

rem =========================================================
rem CONFIRMACAO
rem =========================================================
echo.
echo Repositorio de origem : %SOURCE_URL%
echo Repositorio de destino: %TARGET_URL%
echo.
choice /C SN /M "Deseja continuar com a migracao?"
if errorlevel 2 (
    call :log Operacao cancelada pelo usuario.
    echo Operacao cancelada pelo usuario.
    goto end
)

rem =========================================================
rem CRIAR PASTA TEMPORARIA
rem =========================================================
mkdir "%WORK_DIR%" >nul 2>nul
if errorlevel 1 (
    call :log ERRO: Nao foi possivel criar a pasta temporaria.
    echo ERRO: Nao foi possivel criar a pasta temporaria.
    goto fail
)

call :log Pasta temporaria criada com sucesso.

rem =========================================================
rem CLONE --MIRROR
rem =========================================================
echo.
echo Clonando repositorio de origem...
call :log Executando clone --mirror...
git clone --mirror "%SOURCE_URL%" "%REPO_DIR%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log ERRO: Falha no clone --mirror.
    echo ERRO: Falha no clone do repositorio de origem.
    goto fail
)
call :log Clone --mirror concluido com sucesso.

rem =========================================================
rem CONFIGURAR PUSH
rem =========================================================
echo.
echo Configurando URL de push...
git -C "%REPO_DIR%" remote set-url --push origin "%TARGET_URL%" >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log ERRO: Falha ao configurar URL de push.
    echo ERRO: Falha ao configurar a URL de destino.
    goto fail
)
call :log URL de push configurada com sucesso.

rem =========================================================
rem PUSH --MIRROR
rem =========================================================
echo.
echo Enviando repositorio para o GitHub...
call :log Executando push --mirror...
git -C "%REPO_DIR%" push --mirror >> "%LOG_FILE%" 2>&1
if errorlevel 1 (
    call :log ERRO: Falha no push --mirror.
    echo ERRO: Falha ao enviar o repositorio para o GitHub.
    goto fail
)
call :log Push --mirror concluido com sucesso.

rem =========================================================
rem SUCESSO
rem =========================================================
echo.
echo Migracao concluida com sucesso.
call :log MIGRACAO CONCLUIDA COM SUCESSO.
goto cleanup_success

:fail
call :log PROCESSO FINALIZADO COM ERRO.
echo.
echo Consulte o log em:
echo %LOG_FILE%
goto cleanup_error

:cleanup_success
echo.
echo Limpando arquivos temporarios...
call :log Limpando arquivos temporarios...
if exist "%WORK_DIR%" rmdir /S /Q "%WORK_DIR%" >> "%LOG_FILE%" 2>&1
call :log Arquivos temporarios removidos.
echo Log gravado em:
echo %LOG_FILE%
goto end

:cleanup_error
echo.
echo Limpando arquivos temporarios...
call :log Tentando limpar arquivos temporarios...
if exist "%WORK_DIR%" rmdir /S /Q "%WORK_DIR%" >> "%LOG_FILE%" 2>&1
call :log Limpeza finalizada.
goto end

:log
echo [%date% %time%] %*>>"%LOG_FILE%"
goto :eof

:end
echo.
pause
endlocal
exit /b

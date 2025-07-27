@echo off
echo Iniciando Postman Automatizado...
echo.

REM Verificar se o Python está instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Por favor, instale o Python 3.6 ou superior.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit /b
)

REM Verificar se as dependências estão instaladas
echo Verificando dependencias...
pip install -r requirements.txt

REM Iniciar o aplicativo
echo.
echo Iniciando aplicativo...
echo.
python postman_automatizado.py

pause
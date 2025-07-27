@echo off
echo Verificando ambiente para criar executavel do Postman Automatizado...
echo.

REM Verificar se o Python está instalado
echo Verificando instalacao do Python...
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo ERRO: Python nao encontrado. Por favor, instale o Python 3.6 ou superior.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit /b
)
echo Python encontrado com sucesso!
echo.

REM Verificar e instalar as dependências
echo Instalando dependencias necessarias...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo ERRO: Falha ao instalar dependencias.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit /b
)
echo Dependencias instaladas com sucesso!
echo.

REM Criar o executável com PyInstaller
echo Criando arquivo executavel...
echo (Este processo pode demorar alguns minutos)

REM Criar pasta para o executável se não existir
if not exist "dist" mkdir dist

REM Executar PyInstaller para criar o executável
pyinstaller --noconfirm --onefile --windowed --icon="icon.png" --add-data="icon.png;." --name="Postman_Automatizado" postman_automatizado.py

if %errorlevel% neq 0 (
    echo ERRO: Falha ao criar o executavel.
    echo Pressione qualquer tecla para sair...
    pause >nul
    exit /b
)

echo.
echo Executavel criado com sucesso!
echo O arquivo executavel esta disponivel em: %CD%\dist\Postman_Automatizado.exe
echo.

REM Copiar arquivos necessários para a pasta dist
echo Copiando arquivos de configuracao para a pasta do executavel...
if exist "config.json" copy "config.json" "dist\"
if exist "caminhos.json" copy "caminhos.json" "dist\"
if exist "icon.png" copy "icon.png" "dist\"

REM Criar estrutura de pastas necessárias
if not exist "dist\arquivos" mkdir "dist\arquivos"
if not exist "dist\arquivos\input" mkdir "dist\arquivos\input"
if not exist "dist\arquivos\output" mkdir "dist\arquivos\output"
if not exist "dist\log" mkdir "dist\log"

echo.
echo Processo concluido! O executavel e todos os arquivos necessarios
echo foram criados na pasta "dist".
echo.
echo Pressione qualquer tecla para sair...
pause >nul
@echo off
REM Beast Mode AI Development Framework - Windows Installation Script
REM Supports: Windows 10/11 with Python 3.9+

setlocal enabledelayedexpansion

REM Configuration
set PYTHON_MIN_VERSION=3.9
set PROJECT_NAME=Beast Mode AI Development Framework
set REDIS_PORT=6379

REM Colors (limited support in Windows)
set INFO=[INFO]
set SUCCESS=[SUCCESS]
set WARNING=[WARNING]
set ERROR=[ERROR]

echo.
echo 🚀 Installing %PROJECT_NAME%...
echo.

REM Check if we're in the project directory
if not exist "requirements.txt" (
    echo %ERROR% requirements.txt not found. Please run this script from the project root directory.
    exit /b 1
)

REM Check Python installation
echo %INFO% Checking Python installation...

python --version >nul 2>&1
if %errorlevel% neq 0 (
    python3 --version >nul 2>&1
    if %errorlevel% neq 0 (
        echo %ERROR% Python is not installed or not in PATH.
        echo Please install Python %PYTHON_MIN_VERSION% or later from https://python.org
        echo Make sure to check "Add Python to PATH" during installation.
        pause
        exit /b 1
    ) else (
        set PYTHON_CMD=python3
    )
) else (
    set PYTHON_CMD=python
)

REM Get Python version
for /f "tokens=2" %%i in ('%PYTHON_CMD% --version 2^>^&1') do set PYTHON_VERSION=%%i

echo %SUCCESS% Python %PYTHON_VERSION% found

REM Check Python version (basic check)
for /f "tokens=1,2 delims=." %%a in ("%PYTHON_VERSION%") do (
    set MAJOR=%%a
    set MINOR=%%b
)

if %MAJOR% lss 3 (
    echo %ERROR% Python %PYTHON_VERSION% is too old. Python 3.9+ is required.
    pause
    exit /b 1
)

if %MAJOR% equ 3 if %MINOR% lss 9 (
    echo %ERROR% Python %PYTHON_VERSION% is too old. Python 3.9+ is required.
    pause
    exit /b 1
)

REM Check for pip
echo %INFO% Checking pip installation...
%PYTHON_CMD% -m pip --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %ERROR% pip is not installed. Please install pip.
    pause
    exit /b 1
)

echo %SUCCESS% pip is available

REM Create virtual environment
echo %INFO% Creating Python virtual environment...

if exist ".venv" (
    echo %WARNING% Virtual environment already exists. Removing old one...
    rmdir /s /q .venv
)

%PYTHON_CMD% -m venv .venv
if %errorlevel% neq 0 (
    echo %ERROR% Failed to create virtual environment.
    pause
    exit /b 1
)

REM Activate virtual environment
echo %INFO% Activating virtual environment...
call .venv\Scripts\activate.bat

REM Upgrade pip
echo %INFO% Upgrading pip...
python -m pip install --upgrade pip

echo %SUCCESS% Virtual environment created and activated

REM Install Python dependencies
echo %INFO% Installing Python dependencies...
pip install -r requirements.txt
if %errorlevel% neq 0 (
    echo %ERROR% Failed to install dependencies.
    pause
    exit /b 1
)

echo %SUCCESS% Python dependencies installed

REM Configure environment
echo %INFO% Configuring environment...

if not exist ".env" (
    echo %INFO% Creating .env file from template...
    if exist ".env.example" (
        copy ".env.example" ".env" >nul
    ) else (
        REM Create basic .env file
        (
            echo # Beast Mode AI Development Framework Configuration
            echo # Copy this file to your user directory for global configuration
            echo.
            echo # Redis Configuration
            echo REDIS_HOST=localhost
            echo REDIS_PORT=6379
            echo REDIS_PASSWORD=
            echo.
            echo # API Keys ^(set your actual keys^)
            echo OPENAI_API_KEY=
            echo ANTHROPIC_API_KEY=
            echo.
            echo # Environment
            echo ENVIRONMENT=development
            echo DEBUG=true
            echo.
            echo # Monitoring
            echo PROMETHEUS_PORT=9090
            echo GRAFANA_PORT=3000
            echo.
            echo # Observatory
            echo OBSERVATORY_PORT=8080
            echo OBSERVATORY_HOST=localhost
        ) > .env
    )
    
    echo %WARNING% Please edit .env file and set your API keys and configuration
)

REM Copy .env to user directory for global access
if exist ".env" if not exist "%USERPROFILE%\.env" (
    echo %INFO% Copying .env to user directory for global access...
    copy ".env" "%USERPROFILE%\.env" >nul
)

REM Check for Redis (optional on Windows)
echo %INFO% Checking Redis availability...
redis-server --version >nul 2>&1
if %errorlevel% neq 0 (
    echo %WARNING% Redis is not installed or not in PATH.
    echo For full functionality, please install Redis:
    echo 1. Download Redis for Windows from: https://github.com/microsoftarchive/redis/releases
    echo 2. Or use Docker: docker run -d -p 6379:6379 redis:alpine
    echo 3. Or use WSL2 with Linux Redis installation
) else (
    echo %SUCCESS% Redis is available
)

REM Validate installation
echo %INFO% Validating installation...

%PYTHON_CMD% -c "
import sys
try:
    import pydantic
    import fastapi
    import requests
    import cryptography
    print('✅ All core imports successful')
    print(f'Python version: {sys.version}')
    print(f'Virtual environment: {sys.prefix}')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)
"

if %errorlevel% neq 0 (
    echo %ERROR% Installation validation failed.
    pause
    exit /b 1
)

REM Test Redis connection (optional)
echo %INFO% Testing Redis connection...
%PYTHON_CMD% -c "
import os
try:
    import redis
    r = redis.Redis(
        host=os.getenv('REDIS_HOST', 'localhost'),
        port=int(os.getenv('REDIS_PORT', '6379')),
        password=os.getenv('REDIS_PASSWORD', '') or None,
        decode_responses=True
    )
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'⚠️  Redis connection failed: {e}')
    print('Redis is optional for basic functionality')
"

echo %SUCCESS% Installation validation complete

REM Run quick start example (if requested)
if "%1"=="--with-demo" (
    echo %INFO% Running quick start example...
    if exist "examples\quick_start.py" (
        %PYTHON_CMD% examples\quick_start.py
    ) else if exist "examples\demos\quick_start_demo.py" (
        %PYTHON_CMD% examples\demos\quick_start_demo.py
    ) else (
        echo %WARNING% Quick start example not found. Skipping...
    )
)

REM Print installation summary
echo.
echo %SUCCESS% 🎉 %PROJECT_NAME% installation complete!
echo.
echo 📋 Installation Summary:
echo   ✅ Python %PYTHON_VERSION%
echo   ✅ Virtual environment: .venv
echo   ✅ Dependencies installed
echo   ✅ Environment configured
echo.
echo 🚀 Next Steps:
echo   1. Activate virtual environment: .venv\Scripts\activate.bat
echo   2. Edit .env file with your API keys
echo   3. Run quick start: python examples\demos\quick_start_demo.py
echo   4. View documentation: docs\README.md
echo.
echo 🔧 Development Setup:
echo   • Install dev dependencies: pip install -r requirements-dev.txt
echo   • Run tests: pytest
echo   • Format code: black src\
echo   • Lint code: ruff check src\
echo.
echo 📚 Documentation:
echo   • Installation guide: docs\installation\INSTALLATION_GUIDE.md
echo   • API reference: docs\api\README.md
echo   • Examples: examples\README.md
echo.

REM Handle command line arguments
if "%1"=="--help" goto :help
if "%1"=="-h" goto :help
if "%1"=="--dev" goto :dev
goto :end

:help
echo Beast Mode AI Development Framework - Windows Installation Script
echo.
echo Usage: %0 [OPTIONS]
echo.
echo Options:
echo   --help, -h        Show this help message
echo   --with-demo       Run quick start demo after installation
echo   --dev             Install development dependencies
echo.
echo Examples:
echo   %0                Install core framework
echo   %0 --with-demo    Install and run demo
echo   %0 --dev          Install with development tools
echo.
goto :end

:dev
echo %INFO% Installing development dependencies...
pip install -r requirements-dev.txt
if %errorlevel% neq 0 (
    echo %ERROR% Failed to install development dependencies.
    pause
    exit /b 1
)
echo %SUCCESS% Development dependencies installed
goto :end

:end
pause
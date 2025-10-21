@echo off
REM 32bit Windows環境でのテスト実行スクリプト

echo "=== AOI Data Manager 32bit環境テスト ==="
echo "Python版本: %PYTHON_VERSION%"
echo "アーキテクチャ: %PROCESSOR_ARCHITECTURE%"

REM Python環境確認
python --version
python -c "import platform; print('Architecture:', platform.architecture()[0])"

echo.
echo "=== 依存関係の確認 ==="
python -c "import sys; print('Python version:', sys.version)"
python -c "import platform; print('Platform:', platform.platform())"

echo.
echo "=== 基本テストの実行 ==="
REM 32bit環境では軽量なテストのみ実行
uv run pytest tests/test_models.py -v
if %ERRORLEVEL% neq 0 (
    echo "モデルテストが失敗しました"
    exit /b 1
)

echo.
echo "=== ファイル操作テストの実行 ==="
uv run pytest tests/test_file_operations.py -v
if %ERRORLEVEL% neq 0 (
    echo "ファイル操作テストが失敗しました"
    exit /b 1
)

echo.
echo "=== 32bit専用SQLiteテストの実行 ==="
uv run pytest tests/test_sql_operations_32bit_fixed.py -v
if %ERRORLEVEL% neq 0 (
    echo "32bit専用SQL操作テストが失敗しました"
    exit /b 1
)

echo.
echo "=== API クライアントテストの実行（軽量） ==="
uv run pytest tests/test_api_client.py -m "not integration" -v
if %ERRORLEVEL% neq 0 (
    echo "API クライアントテストが失敗しました"
    exit /b 1
)

echo.
echo "=== メモリ効率テストの実行 ==="
uv run pytest tests/test_sql_operations_32bit_fixed.py -m "bit32 and not memory_intensive" -v
if %ERRORLEVEL% neq 0 (
    echo "メモリ効率テストが失敗しました"
    exit /b 1
)

echo.
echo "=== 全テスト完了 ==="
echo "32bit環境でのテストが正常に完了しました。"
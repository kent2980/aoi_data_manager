# AOI Data Manager

AOI defect data management library for handling file operations and API interactions.

## Features

- File operations for defect and repair data
- Kintone API client for data synchronization
- Data models for defect and repair information

## Installation

### Using pip

```bash
pip install aoi-data-manager
```

### For development (using uv)

```bash
# Clone the repository
git clone https://github.com/kent2980/aoi_data_manager.git
cd aoi_data_manager

# Install dependencies and create virtual environment
uv sync

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate
```

### Development commands

```bash
# Run tests
uv run pytest

# Run only unit tests (skip integration tests)
uv run pytest -m "not integration"

# Run integration tests (requires environment variables)
uv run pytest -m integration

# Format code
uv run black .

# Lint code
uv run flake8

# Type checking
uv run mypy src/

# Build package
uv build
```

## Integration Testing

統合テストを実行するには、実際のKintone APIの設定が必要です。

### 環境変数の設定

```bash
# Windows PowerShell
$env:KINTONE_SUBDOMAIN="your-subdomain"
$env:KINTONE_APP_ID="123"
$env:KINTONE_API_TOKEN="your-api-token"

# Linux/macOS
export KINTONE_SUBDOMAIN="your-subdomain"
export KINTONE_APP_ID="123"
export KINTONE_API_TOKEN="your-api-token"
```

### 統合テストの実行

```bash
# 統合テストのみ実行
uv run pytest -m integration

# 全テスト実行（単体テスト + 統合テスト）
uv run pytest
```

**注意**: 統合テストは実際のKintone APIにレコードを作成・削除します。テスト用のアプリを使用することを推奨します。

## Usage

```python
from aoi_data_manager import FileManager, KintoneClient, DefectInfo, RepairdInfo

# File operations
defect_list = FileManager.read_defect_csv("path/to/defect.csv")

# API operations
client = KintoneClient(subdomain="your-subdomain", app_id=123, api_token="your-token")
client.post_defect_records(defect_list)
```

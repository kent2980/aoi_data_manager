# AOI Data Manager

AOI defect data management library for handling file operations and API interactions.

## Features

- File operations for defect and repair data
- Kintone API client for data synchronization
- Data models for defect and repair information

## Installation

```bash
pip install aoi-data-manager
```

## Usage

```python
from aoi_data_manager import FileManager, KintoneClient, DefectInfo, RepairdInfo

# File operations
defect_list = FileManager.read_defect_csv("path/to/defect.csv")

# API operations
client = KintoneClient(subdomain="your-subdomain", app_id=123, api_token="your-token")
client.post_defect_records(defect_list)
```

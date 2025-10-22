import pytest
import tempfile
import os
from pathlib import Path


@pytest.fixture
def temp_dir():
    """一時ディレクトリのフィクスチャ"""
    with tempfile.TemporaryDirectory() as tmp_dir:
        yield tmp_dir


@pytest.fixture
def sample_defect_csv_data():
    """サンプル不良CSVデータのフィクスチャ"""
    return """id,model_code,lot_number,current_board_index,defect_number,serial,reference,defect_name,x,y,aoi_user,insert_datetime,model_label,board_label,kintone_record_id
test-id-1,Y001,LOT001,1,1,SER001,R001,短絡,100,200,user001,2023-01-01 12:00:00,Model001,Board001,100
test-id-2,Y002,LOT002,2,1,SER002,R002,断線,150,250,user002,2023-01-02 12:00:00,Model002,Board002,101"""


@pytest.fixture
def sample_repaird_csv_data():
    """サンプル修理CSVデータのフィクスチャ"""
    return """id,is_repaird,parts_type,insert_datetime,kintone_record_id
test-id-1,修理済み,抵抗,2023-01-01 13:00:00,200
test-id-2,未修理,,2023-01-02 13:00:00,201"""


@pytest.fixture
def create_test_csv_file(temp_dir):
    """テスト用CSVファイル作成のヘルパーフィクスチャ"""

    def _create_csv(filename, content):
        filepath = Path(temp_dir) / filename
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(content)
        return str(filepath)

    return _create_csv

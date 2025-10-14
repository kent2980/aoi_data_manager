import pytest
import pandas as pd
import json
import os
from pathlib import Path
from unittest.mock import patch, mock_open, MagicMock
from aoi_data_manager.file_operations import FileManager
from aoi_data_manager.models import DefectInfo, RepairdInfo


class TestFileManager:
    """FileManagerクラスのテスト"""

    def test_create_repaird_csv_path(self):
        """修理データCSVパス生成のテスト"""
        data_dir = "/test/data"
        lot_number = "LOT001"
        expected = os.path.join("/test/data", "LOT001_repaird_list.csv")

        result = FileManager.create_repaird_csv_path(data_dir, lot_number)
        assert result == expected

    def test_create_repaird_csv_path_empty_lot_number(self):
        """指図が空の場合のテスト"""
        with pytest.raises(ValueError, match="Current lot number is not set."):
            FileManager.create_repaird_csv_path("/test/data", "")

    def test_create_repaird_csv_path_empty_data_directory(self):
        """データディレクトリが空の場合のテスト"""
        with pytest.raises(ValueError, match="Not Setting Data Directory"):
            FileManager.create_repaird_csv_path("", "LOT001")

    def test_create_defect_csv_path(self):
        """不良データCSVパス生成のテスト"""
        data_dir = "/test/data"
        lot_number = "LOT001"
        image_filename = "image001"
        expected = os.path.join("/test/data", "LOT001_image001.csv")

        result = FileManager.create_defect_csv_path(
            data_dir, lot_number, image_filename
        )
        assert result == expected

    def test_create_defect_csv_path_empty_parameters(self):
        """パラメータが空の場合のテスト"""
        with pytest.raises(ValueError, match="Lot number is not set."):
            FileManager.create_defect_csv_path("/test/data", "", "image001")

        with pytest.raises(ValueError, match="Image filename is not set."):
            FileManager.create_defect_csv_path("/test/data", "LOT001", "")

        with pytest.raises(ValueError, match="Data directory is not set."):
            FileManager.create_defect_csv_path("", "LOT001", "image001")

    def test_get_image_path(self):
        """画像ディレクトリパス生成のテスト"""
        data_dir = "C:\\Users\\kentaroyoshida\\Pictures\\image_coords_app"
        lot_number = "1234567-20"
        item_code = "Y8470722R"

        result = FileManager.get_image_path(data_dir, lot_number, item_code)
        assert isinstance(result, str)
        assert result.startswith("Y8470722R_20_")

    def test_get_model_data_from_image_filename(self):
        """画像ファイル名からモデルデータ抽出のテスト"""
        image_filename = "Y8470722R_20_CN-SNDDJ0CJ_411CA_S面.jpg"
        model_name, board_name, borad_side = (
            FileManager.get_model_data_from_image_filename(image_filename)
        )
        assert model_name == "CN-SNDDJ0CJ"
        assert board_name == "411CA"
        assert borad_side == "S面"

    @patch("aoi_data_manager.file_operations.Path.exists")
    @patch("aoi_data_manager.file_operations.pd.read_csv")
    def test_read_defect_csv_success(self, mock_read_csv, mock_exists):
        """不良CSV読み込み成功のテスト"""
        mock_exists.return_value = True
        mock_df = pd.DataFrame(
            [
                {
                    "id": "test-id",
                    "model_code": "Y001",
                    "lot_number": "LOT001",
                    "current_board_index": 1,
                    "defect_number": "D001",
                    "serial": "SER001",
                    "reference": "R001",
                    "defect_name": "短絡",
                    "x": 100,
                    "y": 200,
                    "aoi_user": "user001",
                    "insert_datetime": "2023-01-01 12:00:00",
                    "model_label": "Model001",
                    "board_label": "Board001",
                    "kintone_record_id": "100",
                }
            ]
        )
        mock_read_csv.return_value = mock_df

        result = FileManager.read_defect_csv("test.csv")
        assert len(result) == 1
        assert isinstance(result[0], DefectInfo)
        assert result[0].model_code == "Y001"

    @patch("aoi_data_manager.file_operations.Path.exists")
    def test_read_defect_csv_file_not_exists(self, mock_exists):
        """不良CSVファイルが存在しない場合のテスト"""
        mock_exists.return_value = False

        result = FileManager.read_defect_csv("nonexistent.csv")
        assert result == []

    @patch("aoi_data_manager.file_operations.Path.exists")
    @patch("aoi_data_manager.file_operations.pd.read_csv")
    def test_read_defect_csv_exception(self, mock_read_csv, mock_exists):
        """不良CSV読み込み例外のテスト"""
        mock_exists.return_value = True
        mock_read_csv.side_effect = Exception("Read error")

        with pytest.raises(Exception, match="Failed to read defect CSV"):
            FileManager.read_defect_csv("test.csv")

    @patch("aoi_data_manager.file_operations.pd.DataFrame.to_csv")
    def test_save_defect_csv_success(self, mock_to_csv):
        """不良CSV保存成功のテスト"""
        defect_list = [DefectInfo(model_code="Y001", lot_number="LOT001")]

        FileManager.save_defect_csv(defect_list, "test.csv")
        mock_to_csv.assert_called_once_with(
            "test.csv", index=False, encoding="utf-8-sig"
        )

    @patch("aoi_data_manager.file_operations.pd.DataFrame.to_csv")
    def test_save_defect_csv_exception(self, mock_to_csv):
        """不良CSV保存例外のテスト"""
        mock_to_csv.side_effect = Exception("Write error")
        defect_list = [DefectInfo()]

        with pytest.raises(Exception, match="Failed to save defect CSV"):
            FileManager.save_defect_csv(defect_list, "test.csv")

    @patch("aoi_data_manager.file_operations.Path.exists")
    def test_read_defect_mapping_file_not_exists(self, mock_exists):
        """不良名マッピングファイルが存在しない場合のテスト"""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            FileManager.read_defect_mapping("mapping.csv")

    @patch("builtins.open", new_callable=mock_open)
    def test_create_kintone_settings_file_success(self, mock_file):
        """Kintone設定ファイル作成成功のテスト"""
        result = FileManager.create_kintone_settings_file(
            "settings.json", "subdomain", "app_id", "api_token"
        )
        assert result is True
        mock_file.assert_called_once()

    @patch("builtins.open", new_callable=mock_open)
    def test_create_kintone_settings_file_exception(self, mock_file):
        """Kintone設定ファイル作成例外のテスト"""
        mock_file.side_effect = Exception("Write error")

        result = FileManager.create_kintone_settings_file(
            "settings.json", "subdomain", "app_id", "api_token"
        )
        assert result is False

    @patch("aoi_data_manager.file_operations.Path.exists")
    def test_load_kintone_settings_file_not_exists(self, mock_exists):
        """Kintone設定ファイルが存在しない場合のテスト"""
        mock_exists.return_value = False

        with pytest.raises(FileNotFoundError):
            FileManager.load_kintone_settings_file("settings.json")

    @patch("aoi_data_manager.file_operations.Path.exists")
    @patch("builtins.open", new_callable=mock_open, read_data='{"subdomain": "test"}')
    def test_load_kintone_settings_file_success(self, mock_file, mock_exists):
        """Kintone設定ファイル読み込み成功のテスト"""
        mock_exists.return_value = True

        result = FileManager.load_kintone_settings_file("settings.json")
        assert result == {"subdomain": "test"}

import os
import pandas as pd
from pathlib import Path
from typing import List, Dict, Any
from .models import DefectInfo, RepairdInfo


class FileManager:
    """ファイル操作を管理するクラス"""

    @staticmethod
    def create_repaird_csv_path(data_directory: str, current_lot_number: str) -> str:
        """指図に対応する修理データCSVファイル名を生成"""
        if not current_lot_number:
            raise ValueError("Current lot number is not set.")
        if not data_directory:
            raise ValueError("Not Setting Data Directory")
        filename = f"{current_lot_number}_repaird_list.csv"
        return os.path.join(data_directory, filename)

    @staticmethod
    def create_defect_csv_path(
        data_directory: str, lot_number: str, image_filename: str
    ) -> str:
        """不良データCSVファイルのパスを生成"""
        if not lot_number:
            raise ValueError("Lot number is not set.")
        if not image_filename:
            raise ValueError("Image filename is not set.")
        if not data_directory:
            raise ValueError("Data directory is not set.")

        filename = f"{lot_number}_{image_filename}.csv"
        return os.path.join(data_directory, filename)

    @staticmethod
    def read_defect_csv(filepath: str) -> List[DefectInfo]:
        """CSVファイルから不良リストを読み込み"""
        try:
            if not Path(filepath).exists():
                return []

            df = pd.read_csv(filepath)
            return [DefectInfo(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise Exception(f"Failed to read defect CSV: {e}")

    @staticmethod
    def read_repaird_csv(filepath: str) -> List[RepairdInfo]:
        """CSVファイルから修理データを読み込み"""
        try:
            if not Path(filepath).exists():
                return []

            df = pd.read_csv(filepath)
            return [RepairdInfo(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise Exception(f"Failed to read repaird CSV: {e}")

    @staticmethod
    def save_defect_csv(defect_list: List[DefectInfo], filepath: str) -> None:
        """不良リストをCSVファイルに保存"""
        try:
            df = pd.DataFrame([defect.__dict__ for defect in defect_list])
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise Exception(f"Failed to save defect CSV: {e}")

    @staticmethod
    def save_repaird_csv(repaird_list: List[RepairdInfo], filepath: str) -> None:
        """修理データをCSVファイルに保存"""
        try:
            df = pd.DataFrame([repaird.__dict__ for repaird in repaird_list])
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise Exception(f"Failed to save repaird CSV: {e}")

    @staticmethod
    def read_defect_mapping(mapping_path: str) -> pd.DataFrame:
        """不良名マッピングファイルを読み込み"""
        if not Path(mapping_path).exists():
            raise FileNotFoundError(f"defect_mapping.csv not found at {mapping_path}")

        df = pd.read_csv(mapping_path)
        return df.dropna()

    @staticmethod
    def read_user_csv(user_csv_path: str) -> pd.DataFrame:
        """ユーザーCSVファイルを読み込み"""
        if not Path(user_csv_path).exists():
            raise FileNotFoundError(f"user.csv not found at {user_csv_path}")

        return pd.read_csv(user_csv_path)

import os
import pandas as pd
from pathlib import Path
from typing import List
from .models import DefectInfo, RepairdInfo


class FileManager:
    """ファイル操作を管理するクラス"""

    @staticmethod
    def create_repaird_csv_path(data_directory: str, current_lot_number: str) -> str:
        """
        指図に対応する修理データCSVファイル名を生成
        ### Args:
            data_directory (str): データディレクトリ
            current_lot_number (str): 現在の指図
        ### Raises:
            ValueError: current_lot_numberまたはdata_directoryが設定されていない場合
        ### Returns:
            str: 修理データCSVファイルのパス
        """

        # current_lot_numberが設定されているか確認
        if not current_lot_number:
            raise ValueError("Current lot number is not set.")
        # データディレクトリが設定されているか確認
        if not data_directory:
            raise ValueError("Not Setting Data Directory")
        # ファイル名を生成
        filename = f"{current_lot_number}_repaird_list.csv"
        # フルパスを返す
        return os.path.join(data_directory, filename)

    @staticmethod
    def create_defect_csv_path(
        data_directory: str, lot_number: str, image_filename: str
    ) -> str:
        """
        不良データCSVファイルのパスを生成
        ### Args:
            data_directory (str): データディレクトリ
            lot_number (str): 指図
            image_filename (str): 画像ファイル名（拡張子なし）
        ### Raises:
            ValueError: lot_number, image_filename, data_directoryが設定されていない場合
        ### Returns:
            str: 不良データCSVファイルのパス
        """
        # 指図が設定されているか確認
        if not lot_number:
            raise ValueError("Lot number is not set.")
        # 画像ファイル名が設定されているか確認
        if not image_filename:
            raise ValueError("Image filename is not set.")
        # データディレクトリが設定されているか確認
        if not data_directory:
            raise ValueError("Data directory is not set.")

        # ファイル名を生成
        filename = f"{lot_number}_{image_filename}.csv"
        # フルパスを返す
        return os.path.join(data_directory, filename)

    @staticmethod
    def read_defect_csv(filepath: str) -> List[DefectInfo]:
        """
        CSVファイルから不良リストを読み込み
        ### Args:
            filepath (str): CSVファイルのパス
        ### Raises:
            Exception: ファイル読み込みエラー
        ### Returns:
            List[DefectInfo]: 不良情報リスト
        """
        try:
            # ファイルの存在を確認
            if not Path(filepath).exists():
                return []
            # CSVを読み込み
            df = pd.read_csv(filepath)
            # DefectInfoのリストに変換して返す
            return [DefectInfo(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise Exception(f"Failed to read defect CSV: {e}")

    @staticmethod
    def read_repaird_csv(filepath: str) -> List[RepairdInfo]:
        """
        CSVファイルから修理データを読み込み
        ### Args:
            filepath (str): CSVファイルのパス
        ### Raises:
            Exception: ファイル読み込みエラー
        ### Returns:
            List[RepairdInfo]: 修理済み情報リスト
        """
        try:
            # ファイルの存在を確認
            if not Path(filepath).exists():
                return []
            # CSVを読み込み
            df = pd.read_csv(filepath)
            # RepairdInfoのリストに変換して返す
            return [RepairdInfo(**row) for row in df.to_dict(orient="records")]
        except Exception as e:
            raise Exception(f"Failed to read repaird CSV: {e}")

    @staticmethod
    def save_defect_csv(defect_list: List[DefectInfo], filepath: str) -> None:
        """
        不良リストをCSVファイルに保存
        ### Args:
            defect_list (List[DefectInfo]): 不良情報リスト
            filepath (str): 保存先CSVファイルのパス
        ### Raises:
            Exception: ファイル保存エラー
        """
        try:
            # DataFrameに変換して保存
            df = pd.DataFrame([defect.__dict__ for defect in defect_list])
            # インデックスを振らずにCSVに保存
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise Exception(f"Failed to save defect CSV: {e}")

    @staticmethod
    def save_repaird_csv(repaird_list: List[RepairdInfo], filepath: str) -> None:
        """
        修理データをCSVファイルに保存
        ### Args:
            repaird_list (List[RepairdInfo]): 修理済み情報リスト
            filepath (str): 保存先CSVファイルのパス
        ### Raises:
            Exception: ファイル保存エラー
        """
        try:
            # DataFrameに変換して保存
            df = pd.DataFrame([repaird.__dict__ for repaird in repaird_list])
            # インデックスを振らずにCSVに保存
            df.to_csv(filepath, index=False, encoding="utf-8-sig")
        except Exception as e:
            raise Exception(f"Failed to save repaird CSV: {e}")

    @staticmethod
    def read_defect_mapping(mapping_path: str) -> pd.DataFrame:
        """
        不良名マッピングファイルを読み込み
        ### Args:
            mapping_path (str): 不良名マッピングCSVファイルのパス
        ### Raises:
            FileNotFoundError: defect_mapping.csvが存在しない場合
        ### Returns:
            pd.DataFrame: 不良名マッピングデータフレーム
        """
        # ファイルの存在を確認
        if not Path(mapping_path).exists():
            raise FileNotFoundError(f"defect_mapping.csv not found at {mapping_path}")
        # CSVを読み込み、欠損値を削除して返す
        df = pd.read_csv(mapping_path)
        # 不良名マッピングの列を指定
        return df.dropna()

    @staticmethod
    def read_user_csv(user_csv_path: str) -> pd.DataFrame:
        """
        ユーザーCSVファイルを読み込み
        ### Args:
            user_csv_path (str): ユーザーCSVファイルのパス
        ### Raises:
            FileNotFoundError: user.csvが存在しない場合
        ### Returns:
            pd.DataFrame: ユーザーデータフレーム
        """
        # ファイルの存在を確認
        if not Path(user_csv_path).exists():
            raise FileNotFoundError(f"user.csv not found at {user_csv_path}")
        # CSVを読み込みして返す
        return pd.read_csv(user_csv_path)

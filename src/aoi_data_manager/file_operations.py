import os
import pandas as pd
from pathlib import Path
from typing import List, Tuple
from .models import DefectInfo, RepairdInfo
import re


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

    @staticmethod
    def create_kintone_settings_file(
        settings_path: str, subdomain: str, app_id: str, api_token: str
    ) -> bool:
        """
        kintone設定ファイルを作成
        ### Args:
            settings_path (str): kintone_settings.jsonのパス
            subdomain (str): kintoneのサブドメイン
            app_id (str): kintoneアプリID
            api_token (str): kintone APIトークン
        ### Returns:
            bool: ファイル作成に成功したかどうか
        """
        try:
            import json

            settings = {
                "subdomain": subdomain,
                "app_id": app_id,
                "api_token": api_token,
            }
            with open(settings_path, "w", encoding="utf-8") as f:
                json.dump(settings, f, ensure_ascii=False, indent=4)
            return True
        except Exception as e:
            print(f"Failed to create kintone settings file: {e}")
            return False

    @staticmethod
    def load_kintone_settings_file(settings_path: str) -> dict:
        """
        kintone設定ファイルを読み込み
        ### Args:
            settings_path (str): kintone_settings.jsonのパス
        ### Raises:
            FileNotFoundError: kintone_settings.jsonが存在しない場合
            Exception: ファイル読み込みエラー
        ### Returns:
            dict: kintone設定辞書
        """
        try:
            import json

            # ファイルの存在を確認
            if not Path(settings_path).exists():
                raise FileNotFoundError(
                    f"kintone_settings.json not found at {settings_path}"
                )
            with open(settings_path, "r", encoding="utf-8") as f:
                settings = json.load(f)
            return settings
        except FileNotFoundError as fnf_error:
            raise fnf_error
        except Exception as e:
            raise Exception(f"Failed to load kintone settings file: {e}")

    @staticmethod
    def get_image_path(image_directory: str, lot_number: str, item_code: str) -> str:
        """
        指図に対応する画像ディレクトリのパスを生成
        ### Args:
            data_directory (str): データディレクトリ
            lot_number (str): 指図
            item_code (str): 品目コード
        ### Raises:
            ValueError: lot_numberの形式が不正な場合
            FileNotFoundError: 画像ファイルが存在しない場合
        ### Returns:
            str: 画像ディレクトリのパス
        """
        # lotnumberの形式が正しいか確認
        if not re.match(r"^[0-9]{7}-[0-9]{2}", lot_number):
            raise ValueError("Invalid lot number format.")

        # lotnumberの末尾の2桁を取得
        lot_suffix = lot_number[-2:]

        # ファイル名の正規表現パターン
        pattern = rf"^{re.escape(item_code)}_{lot_suffix}_.*$"

        # image_directory以下のディレクトリを走査
        image_path = Path(image_directory)
        for dir_entry in image_path.iterdir():
            if re.match(pattern, dir_entry.name):
                return str(dir_entry.name)
        raise FileNotFoundError("Image directory not found.")

    @staticmethod
    def parse_image_filename(image_filename: str) -> Tuple[str, str, str]:
        """
        画像ファイル名から品目コードと指図を抽出
        ### Args:
            image_filename (str): 画像ファイル名（拡張子あり/なし両対応）
        ### Raises:
            ValueError: 画像ファイル名の形式が不正な場合
        ### Returns:
            (str, str, str): モデル名、基板名、基板面のタプル
        """

        # 拡張子を除去
        filename_without_ext = image_filename
        if "." in image_filename:
            filename_without_ext = image_filename.rsplit(".", 1)[0]

        # 修正された正規表現パターン（5フィールド）
        # パターン: 品目コード_2桁数字_モデル名_基板名_基板面
        match = re.match(r"^.*_[0-9]{2}_.*_.*_.*$", filename_without_ext)
        if not match:
            raise ValueError(f"Invalid image filename format: {image_filename}")

        # アンダースコアで分割
        parts = filename_without_ext.split("_")

        # 最低5つのパートが必要
        if len(parts) < 5:
            raise ValueError(
                f"Invalid filename format. Expected at least 5 parts: {image_filename}"
            )

        # 2番目のパートが2桁の数字であることを再確認
        if not re.match(r"^\d{2}$", parts[1]):
            raise ValueError(f"Second part should be 2-digit number: {parts[1]}")

        model_name = parts[2]
        board_name = parts[3]
        board_side = parts[4]

        return model_name, board_name, board_side

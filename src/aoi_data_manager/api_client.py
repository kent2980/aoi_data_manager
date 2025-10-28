import requests
import json
from typing import List, Dict, Any
from pathlib import Path
from .schema import DefectInfo, RepairdInfo


class KintoneClient:
    """Kintone API クライアント"""

    def __init__(self, subdomain: str, app_id: int, api_token: str):
        """
        コンストラクタ
        ### Args:
            subdomain (str): サブドメイン
            app_id (int): アプリID
            api_token (str): APIトークン
        """
        self.subdomain = subdomain
        """サブドメイン"""
        self.app_id = app_id
        """アプリID"""
        self.api_token = api_token
        """APIトークン"""
        self.base_url = f"https://{subdomain}.cybozu.com/k/v1"
        """APIベースURL"""
        self.headers = {
            "X-Cybozu-API-Token": api_token,
            "Content-Type": "application/json",
        }
        """HTTPヘッダー"""

    def post_defect_records(self, defect_list: List[DefectInfo]) -> List[DefectInfo]:
        """
        不良レコードをKintoneに送信
        ### Args:
            defect_list (List[DefectInfo]): 不良情報リスト
        ### Raises:
            ValueError: API送信エラー
        ### Returns:
            List[DefectInfo]: kintoneレコードIDが更新された不良情報リスト
        """

        # APIエンドポイントURL
        url = f"{self.base_url}/records.json"

        # DefectInfoリストを辞書リストに変換
        defect_list_dicts = []
        for item in defect_list:
            board_number_label = f"{item.lot_number}_{item.current_board_index}"
            # Noneや空の値をチェック
            defect_dict = {
                "updateKey": {"field": "unique_id", "value": str(item.id or "")},
                "revision": -1,
                "record": {
                    "line_name": {"value": str(item.line_name or "")},
                    "model_code": {"value": str(item.model_code or "")},
                    "lot_number": {"value": str(item.lot_number or "")},
                    "current_board_index": {
                        "value": int(item.current_board_index or 0)
                    },
                    "defect_number": {"value": int(item.defect_number or "")},
                    "serial": {"value": str(item.serial or "")},
                    "reference": {"value": str(item.reference or "")},
                    "defect_name": {"value": str(item.defect_name or "")},
                    "x": {"value": float(item.x or 0)},
                    "y": {"value": float(item.y or 0)},
                    "aoi_user": {"value": str(item.aoi_user or "")},
                    "insert_datetime": {
                        "value": str(item.insert_datetime or "")
                    },  # 修正
                    "model_label": {"value": str(item.model_label or "")},
                    "board_label": {"value": str(item.board_label or "")},
                    "board_number_label": {"value": board_number_label},
                },
            }
            # 画像パスが指定されている場合、画像をアップロードしてfileKeyを設定
            if item.image_path != "":
                file_key = self.upload_image_file(item.image_path)
                defect_dict["record"]["defect_image"] = {
                    "value": [{"fileKey": file_key}]
                }
            defect_list_dicts.append(defect_dict)

        # 一括登録リクエスト
        data = {"app": self.app_id, "records": defect_list_dicts, "upsert": True}

        # レスポンスを受け取る
        response = requests.put(url, headers=self.headers, data=json.dumps(data))

        # レスポンスkintoneレコードIDを取得してdefect_listを更新
        if response.status_code == 200:
            if "records" in response.json():
                records = response.json()["records"]
                for i, record in enumerate(records):
                    if i < len(defect_list):
                        defect_list[i].kintone_record_id = record["id"]
        else:
            raise ValueError(f"API送信エラー: {response.json()}")

        return defect_list

    def post_repaird_records(
        self, repaird_list: List[RepairdInfo]
    ) -> List[RepairdInfo]:
        """
        修理レコードをKintoneに送信
        ### Args:
            repaird_list (List[RepairdInfo]): 修理情報リスト
        ### Raises:
            ValueError: API送信エラー
        ### Returns:
            List[RepairdInfo]: kintoneレコードIDが更新された修理情報リスト
        """

        # APIエンドポイントURL
        url = f"{self.base_url}/records.json"

        # RepairdInfoリストを辞書リストに変換
        repaird_list_dicts = [
            {
                "updateKey": {"field": "unique_id", "value": str(item.id or "")},
                "revision": -1,
                "record": {
                    "is_repaird": {"value": str(item.is_repaird or "")},
                    "parts_type": {"value": str(item.parts_type or "")},
                    "insert_date": {"value": str(item.insert_datetime or "")},
                },
            }
            for item in repaird_list
        ]

        # 一括登録リクエスト
        data = {"app": self.app_id, "records": repaird_list_dicts, "upsert": True}

        # レスポンスを受け取る
        response = requests.put(url, headers=self.headers, data=json.dumps(data))

        # レスポンスkintoneレコードIDを取得してrepaird_listを更新
        if response.status_code == 200:
            if "records" in response.json():
                records = response.json()["records"]
                for i, record in enumerate(records):
                    if i < len(repaird_list):
                        repaird_list[i].kintone_record_id = record["id"]
        else:
            raise ValueError(f"API送信エラー: {response.json()}")

        return repaird_list

    def delete_record(self, record_id: str) -> None:
        """
        レコードを削除
        ### Args:
            record_id (str): レコードID
        ### Raises:
            ValueError: API削除エラー
        """

        # APIエンドポイントURL
        url = f"{self.base_url}/records.json"

        # 削除リクエスト
        data = {
            "app": self.app_id,
            "ids": [record_id],
        }

        # レスポンスを受け取る
        response = requests.delete(url, headers=self.headers, data=json.dumps(data))

        # エラーチェック
        if response.status_code != 200:
            raise ValueError(f"API削除エラー: {response.json()}")

    def is_connected(self) -> bool:
        """
        Kintoneへの接続確認
        ### Returns:
            bool: 接続成功ならTrue、失敗ならFalse
        """
        try:
            url = f"{self.base_url}/app.json"
            data = {"id": self.app_id}
            response = requests.get(url, headers=self.headers, data=json.dumps(data))
            return response.status_code == 200
        except Exception:
            return False

    def upload_image_file(self, file_path: str) -> str:
        """
        画像ファイルをKintoneにアップロードしてfileKeyを返す
        ### Args:
            file_path (str): アップロードするファイルのパス
        ### Raises:
            ValueError: ファイルが存在しない場合
            ValueError: サポートされていないファイル形式
            ValueError: APIアップロードエラー
        ### Returns:
            str: アップロードされたファイルのfileKey
        """
        # ファイルの存在確認
        path = Path(file_path)
        if not path.exists():
            raise ValueError(f"ファイルが存在しません: {file_path}")

        # ファイル拡張子からMIMEタイプを判定
        mime_types = {
            ".jpg": "image/jpeg",
            ".jpeg": "image/jpeg",
            ".png": "image/png",
            ".gif": "image/gif",
            ".bmp": "image/bmp",
        }
        file_ext = path.suffix.lower()
        mime_type = mime_types.get(file_ext)

        if mime_type is None:
            raise ValueError(f"サポートされていないファイル形式: {file_ext}")

        # APIエンドポイントURL
        url = f"{self.base_url}/file.json"

        # ヘッダー(Content-Typeは指定しない)
        headers = {
            "X-Cybozu-API-Token": self.api_token,
        }

        # ファイルを開いてアップロード
        with open(file_path, "rb") as f:
            files = {"file": (path.name, f, mime_type)}
            response = requests.post(url, headers=headers, files=files)

        # エラーチェック
        if response.status_code != 200:
            raise ValueError(f"APIアップロードエラー: {response.json()}")

        # fileKeyを返す
        file_key = response.json()["fileKey"]
        return file_key

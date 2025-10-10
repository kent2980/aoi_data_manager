import requests
import json
from typing import List, Dict, Any
from .models import DefectInfo, RepairdInfo


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
        defect_list_dicts = [
            {
                "updateKey": {"field": "unique_id", "value": item.id},
                "revision": -1,
                "record": {
                    "model_code": {"value": item.model_code},
                    "lot_number": {"value": item.lot_number},
                    "current_board_index": {"value": item.current_board_index},
                    "defect_number": {"value": item.defect_number},
                    "serial": {"value": item.serial},
                    "reference": {"value": item.reference},
                    "defect_name": {"value": item.defect_name},
                    "x": {"value": item.x},
                    "y": {"value": item.y},
                    "aoi_user": {"value": item.aoi_user},
                    "insert_date": {"value": item.insert_datetime},
                    "model_label": {"value": item.model_label},
                    "board_label": {"value": item.board_label},
                    "unique_id": {"value": item.id},
                },
            }
            for item in defect_list
        ]

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
                "updateKey": {"field": "unique_id", "value": item.id},
                "revision": -1,
                "record": {
                    "unique_id": {"value": item.id},
                    "is_repaird": {"value": item.is_repaird},
                    "parts_type": {"value": item.parts_type},
                    "insert_date": {"value": item.insert_datetime},
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

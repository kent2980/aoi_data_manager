"""
データスキーマモジュール
データベーステーブルに対応するスキーマクラスを定義
"""

from uuid import uuid5, NAMESPACE_DNS
from sqlmodel import SQLModel, Field
from datetime import datetime
from pydantic import model_validator
from typing import Any, Optional


class DefectInfo(SQLModel):
    """
    不良情報のスキーマクラス
    idはlot_number, current_board_index, defect_numberの組み合わせで生成する
    ### Attributes:
        id (str): 不良情報の一意なID
        line_name (str): 生産ライン
        model_code (str): Y番
        lot_number (str): 指図
        current_board_index (int): 基板番号
        defect_number (int): 不良番号
        serial (str): QRシリアル
        reference (str): リファレンス
        defect_name (str): 不良名
        x (float): X座標
        y (float): Y座標
        aoi_user (str): AOI検査員
        insert_datetime (str): 更新日時
        model_label (str): モデルラベル
        board_label (str): 基板ラベル
        kintone_record_id (str): kintoneレコードID
    """

    id: str = Field(default="")
    """不良情報の一意なID"""
    line_name: str = Field(default="")
    """生産ライン"""
    model_code: str = Field(default="")
    """Y番"""
    lot_number: str = Field(default="")
    """指図"""
    current_board_index: int = Field(default=0)
    """基板番号"""
    defect_number: int = Field(default=0)
    """不良番号"""
    serial: str = Field(default="")
    """QRシリアル"""
    reference: str = Field(default="")
    """リファレンス"""
    defect_name: str = Field(default="")
    """不良名"""
    x: float = Field(default=0.0)
    """X座標"""
    y: float = Field(default=0.0)
    """Y座標"""
    aoi_user: str = Field(default="")
    """AOI検査員"""
    insert_datetime: str = Field(default="")
    """更新日時"""
    model_label: str = Field(default="")
    """モデルラベル"""
    board_label: str = Field(default="")
    """基板ラベル"""
    board_number_label: str = Field(default="")
    """基板番号ラベル"""
    image_url: Optional[str] = Field(default=None)
    """画像URL"""
    kintone_record_id: str = Field(default="")
    """kintoneレコードID"""

    @model_validator(mode="before")
    @classmethod
    def generate_id_and_datetime(cls, values: Any) -> Any:
        """IDと日時の自動生成"""
        if isinstance(values, dict):
            if not values.get("id"):
                lot_number = values.get("lot_number", "")
                current_board_index = values.get("current_board_index", 0)
                defect_number = values.get("defect_number", 0)
                namespace = f"{lot_number}_{current_board_index}_{defect_number}"
                values["id"] = str(uuid5(NAMESPACE_DNS, namespace))

            if not values.get("insert_datetime"):
                values["insert_datetime"] = str(datetime.now())
        return values

    @classmethod
    def create(
        cls,
        line_name: str,
        model_code: str,
        lot_number: str,
        current_board_index: int,
        defect_number: int,
        defect_name: str,
        x: float = 0.0,
        y: float = 0.0,
        serial: str = "",
        reference: str = "",
        aoi_user: str = "",
        model_label: str = "",
        board_label: str = "",
        kintone_record_id: str = "",
    ) -> "DefectInfo":
        """
        DefectInfoインスタンスを作成するファクトリメソッド

        Args:
            line_name: 生産ライン
            model_code: Y番
            lot_number: 指図
            current_board_index: 基板番号
            defect_number: 不良番号
            defect_name: 不良名
            x: X座標
            y: Y座標
            serial: QRシリアル
            reference: リファレンス
            aoi_user: AOI検査員
            model_label: モデルラベル
            board_label: 基板ラベル
            kintone_record_id: kintoneレコードID

        Returns:
            DefectInfoSchemaインスタンス
        """
        instance = cls(
            line_name=line_name,
            model_code=model_code,
            lot_number=lot_number,
            current_board_index=current_board_index,
            defect_number=defect_number,
            serial=serial,
            reference=reference,
            defect_name=defect_name,
            x=x,
            y=y,
            aoi_user=aoi_user,
            model_label=model_label,
            board_label=board_label,
            kintone_record_id=kintone_record_id,
        )
        return instance


class RepairdInfo(SQLModel):
    """
    修理済み情報のスキーマクラス
    idはDefectInfoのidと同じものを使用する

    ### Attributes:
        id (str): DefectInfoのid
        is_repaird (bool): 修理済みかどうか
        parts_type (str): 部品種別
        insert_datetime (str): 更新日時
        kintone_record_id (str): kintoneレコードID
    """

    id: str = Field(default="")
    """DefectInfoのid"""
    is_repaird: bool = Field(default=False)
    """修理済みかどうか"""
    parts_type: str = Field(default="")
    """部品種別"""
    insert_datetime: str = Field(default="")
    """更新日時"""
    kintone_record_id: str = Field(default="")
    """kintoneレコードID"""

    @model_validator(mode="before")
    @classmethod
    def generate_datetime(cls, values: Any) -> Any:
        """日時の自動生成"""
        if isinstance(values, dict):
            if not values.get("insert_datetime"):
                values["insert_datetime"] = str(datetime.now())
        return values

    @classmethod
    def create(
        cls,
        defect_id: str,
        is_repaird: bool = False,
        parts_type: str = "",
        kintone_record_id: str = "",
    ) -> "RepairdInfo":
        """
        RepairdInfoSchemaインスタンスを作成するファクトリメソッド

        Args:
            defect_id: DefectInfoのid
            is_repaird: 修理済みかどうか
            parts_type: 部品種別
            kintone_record_id: kintoneレコードID

        Returns:
            RepairdInfoSchemaインスタンス
        """
        instance = cls(
            id=defect_id,
            is_repaird=is_repaird,
            parts_type=parts_type,
            kintone_record_id=kintone_record_id,
        )
        return instance

"""
データスキーマモジュール
データベーステーブルに対応するスキーマクラスを定義
"""

from uuid import uuid5, NAMESPACE_DNS
from sqlmodel import SQLModel
from datetime import datetime


class DefectInfoSchema(SQLModel):
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

    id: str = ""
    """不良情報の一意なID"""
    line_name: str = ""
    """生産ライン"""
    model_code: str = ""
    """Y番"""
    lot_number: str = ""
    """指図"""
    current_board_index: int = 0
    """基板番号"""
    defect_number: int = 0
    """不良番号"""
    serial: str = ""
    """QRシリアル"""
    reference: str = ""
    """リファレンス"""
    defect_name: str = ""
    """不良名"""
    x: float = 0.0
    """X座標"""
    y: float = 0.0
    """Y座標"""
    aoi_user: str = ""
    """AOI検査員"""
    insert_datetime: str = ""
    """更新日時"""
    model_label: str = ""
    """モデルラベル"""
    board_label: str = ""
    """基板ラベル"""
    kintone_record_id: str = ""
    """kintoneレコードID"""

    def __post_init__(self):
        """初期化後処理 - IDの自動生成と日時設定"""
        if not self.id:
            namespace = (
                f"{self.lot_number}_{self.current_board_index}_{self.defect_number}"
            )
            self.id = str(uuid5(NAMESPACE_DNS, namespace))

        if not self.insert_datetime:
            self.insert_datetime = str(datetime.now())

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
    ) -> "DefectInfoSchema":
        """
        DefectInfoSchemaインスタンスを作成するファクトリメソッド

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
        instance.__post_init__()
        return instance


class RepairdInfoSchema(SQLModel):
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

    id: str = ""
    """DefectInfoのid"""
    is_repaird: bool = False
    """修理済みかどうか"""
    parts_type: str = ""
    """部品種別"""
    insert_datetime: str = ""
    """更新日時"""
    kintone_record_id: str = ""
    """kintoneレコードID"""

    def __post_init__(self):
        """初期化後処理 - 日時設定"""
        if not self.insert_datetime:
            self.insert_datetime = str(datetime.now())

    @classmethod
    def create(
        cls,
        defect_id: str,
        is_repaird: bool = False,
        parts_type: str = "",
        kintone_record_id: str = "",
    ) -> "RepairdInfoSchema":
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
        instance.__post_init__()
        return instance

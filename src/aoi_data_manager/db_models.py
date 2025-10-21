from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_DNS
from sqlmodel import SQLModel, Field
from datetime import datetime


class DefectInfo(SQLModel, table=True):
    """
    不良情報を保持するデータクラス
    idはlot_number, current_board_index, defect_numberの組み合わせで生成する
    ### Attributes:
        id (str): 不良情報の一意なID
        line_name (str): 生産ライン
        model_code (str): Y番
        lot_number (str): 指図
        current_board_index (int): 基板番号
        defect_number (str): 不良番号
        serial (str): QRシリアル
        reference (str): リファレンス
        defect_name (str): 不良名
        x (int): X座標
        y (int): Y座標
        aoi_user (str): AOI検査員
        insert_datetime (str): 更新日時
        model_label (str): モデルラベル
        board_label (str): 基板ラベル
        kintone_record_id (str): kintoneレコードID
    """

    id: str = Field(default="", description="不良情報の一意なID", primary_key=True)
    """id"""
    line_name: str = Field(default="", description="生産ライン")
    """生産ライン"""
    model_code: str = Field(default="", description="Y番")
    """Y番"""
    lot_number: str = Field(default="", description="指図")
    """指図"""
    current_board_index: int = Field(default=0, description="基板番号")
    """基板番号"""
    defect_number: int = Field(default=0, description="不良番号")
    """不良番号"""
    serial: str = Field(default="", description="QRシリアル")
    """QRシリアル"""
    reference: str = Field(default="", description="リファレンス")
    """リファレンス"""
    defect_name: str = Field(default="", description="不良名")
    """不良名"""
    x: float = Field(default=0.0, description="X座標")
    """X座標"""
    y: float = Field(default=0.0, description="Y座標")
    """Y座標"""
    aoi_user: str = Field(default="", description="AOI検査員")
    """AOI検査員"""
    insert_datetime: datetime = Field(
        default_factory=datetime.now, description="更新日時"
    )
    """更新日時"""
    model_label: str = Field(default="", description="モデルラベル")
    """モデルラベル"""
    board_label: str = Field(default="", description="基板ラベル")
    """基板ラベル"""
    kintone_record_id: str = Field(default="", description="kintoneレコードID")
    """kintoneレコードID"""

    def __post_init__(self):
        if not self.id:
            namespace = (
                f"{self.lot_number}_{self.current_board_index}_{self.defect_number}"
            )
            self.id = str(uuid5(NAMESPACE_DNS, namespace))


class RepairdInfo(SQLModel, table=True):
    """
    修理済み情報を保持するデータクラス
    idはDefectInfoのidと同じものを使用する

    ### Attributes:
        id (str): DefectInfoのid
        is_repaird (str): 修理済みかどうか
        parts_type (str): 部品種別
        insert_datetime (str): 更新日時
        kintone_record_id (str): kintoneレコードID
    """

    id: str = Field(default="", description="DefectInfoのid", primary_key=True)
    """id"""
    is_repaird: bool = Field(default=False, description="修理済みかどうか")
    """修理済みかどうか"""
    parts_type: str = Field(default="", description="部品種別")
    """部品種別"""
    insert_datetime: datetime = Field(
        default_factory=datetime.now, description="更新日時"
    )
    """更新日時"""
    kintone_record_id: str = Field(default="", description="kintoneレコードID")
    """kintoneレコードID"""

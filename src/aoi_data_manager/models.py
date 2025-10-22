from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_DNS
from sqlmodel import SQLModel


class DefectInfo(SQLModel):
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
        x (float): X座標
        y (float): Y座標
        aoi_user (str): AOI検査員
        insert_datetime (str): 更新日時
        model_label (str): モデルラベル
        board_label (str): 基板ラベル
        kintone_record_id (str): kintoneレコードID
    """

    id: str = ""
    """id"""
    line_name: str = ""
    """生産ライン"""
    model_code: str = ""
    """Y番"""
    lot_number: str = ""
    """指図"""
    current_board_index: int = 0
    """基板番号"""
    defect_number: str = ""
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
        if not self.id:
            namespace = (
                f"{self.lot_number}_{self.current_board_index}_{self.defect_number}"
            )
            self.id = str(uuid5(NAMESPACE_DNS, namespace))


class RepairdInfo(SQLModel):
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

    id: str
    """id"""
    is_repaird: str = "未修理"
    """修理済みかどうか"""
    parts_type: str = ""
    """部品種別"""
    insert_datetime: str = ""
    """更新日時"""
    kintone_record_id: str = ""
    """kintoneレコードID"""

from dataclasses import dataclass
from uuid import uuid5, NAMESPACE_DNS


@dataclass
class DefectInfo:
    """不良情報を保持するデータクラス"""

    id: str = ""
    model_code: str = ""
    lot_number: str = ""
    current_board_index: int = 0
    defect_number: str = ""
    serial: str = ""
    reference: str = ""
    defect_name: str = ""
    x: int = 0
    y: int = 0
    aoi_user: str = ""
    insert_date: str = ""
    model_label: str = ""
    board_label: str = ""
    kintone_record_id: str = ""

    def __post_init__(self):
        if not self.id:
            namespace = (
                f"{self.lot_number}_{self.current_board_index}_{self.defect_number}"
            )
            self.id = str(uuid5(NAMESPACE_DNS, namespace))


@dataclass
class RepairdInfo:
    """修理済み情報を保持するデータクラス"""

    id: str
    is_repaird: str = "未修理"
    parts_type: str = ""
    insert_date: str = ""
    kintone_record_id: str = ""

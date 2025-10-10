import pytest
from aoi_data_manager.models import DefectInfo, RepairdInfo


class TestDefectInfo:
    """DefectInfoクラスのテスト"""

    def test_defect_info_default_values(self):
        """デフォルト値のテスト"""
        defect = DefectInfo()
        assert defect.model_code == ""
        assert defect.lot_number == ""
        assert defect.current_board_index == 0
        assert defect.defect_number == ""
        assert defect.serial == ""
        assert defect.reference == ""
        assert defect.defect_name == ""
        assert defect.x == 0
        assert defect.y == 0
        assert defect.aoi_user == ""
        assert defect.insert_datetime == ""
        assert defect.model_label == ""
        assert defect.board_label == ""
        assert defect.kintone_record_id == ""

    def test_defect_info_id_generation(self):
        """ID自動生成のテスト"""
        defect = DefectInfo(
            lot_number="LOT001", current_board_index=1, defect_number="D001"
        )
        assert defect.id != ""
        assert len(defect.id) == 36  # UUID形式

    def test_defect_info_same_values_same_id(self):
        """同じ値から同じIDが生成されることのテスト"""
        defect1 = DefectInfo(
            lot_number="LOT001", current_board_index=1, defect_number="D001"
        )
        defect2 = DefectInfo(
            lot_number="LOT001", current_board_index=1, defect_number="D001"
        )
        assert defect1.id == defect2.id

    def test_defect_info_different_values_different_id(self):
        """異なる値から異なるIDが生成されることのテスト"""
        defect1 = DefectInfo(
            lot_number="LOT001", current_board_index=1, defect_number="D001"
        )
        defect2 = DefectInfo(
            lot_number="LOT002", current_board_index=1, defect_number="D001"
        )
        assert defect1.id != defect2.id

    def test_defect_info_custom_id(self):
        """カスタムIDが設定されている場合のテスト"""
        custom_id = "custom-id-123"
        defect = DefectInfo(
            id=custom_id,
            lot_number="LOT001",
            current_board_index=1,
            defect_number="D001",
        )
        assert defect.id == custom_id


class TestRepairdInfo:
    """RepairdInfoクラスのテスト"""

    def test_repaird_info_required_id(self):
        """必須IDパラメータのテスト"""
        repaird_id = "test-id-123"
        repaird = RepairdInfo(id=repaird_id)
        assert repaird.id == repaird_id
        assert repaird.is_repaird == "未修理"
        assert repaird.parts_type == ""
        assert repaird.insert_datetime == ""
        assert repaird.kintone_record_id == ""

    def test_repaird_info_with_values(self):
        """値が設定された場合のテスト"""
        repaird = RepairdInfo(
            id="test-id-123",
            is_repaird="修理済み",
            parts_type="抵抗",
            insert_datetime="2023-01-01 12:00:00",
            kintone_record_id="100",
        )
        assert repaird.id == "test-id-123"
        assert repaird.is_repaird == "修理済み"
        assert repaird.parts_type == "抵抗"
        assert repaird.insert_datetime == "2023-01-01 12:00:00"
        assert repaird.kintone_record_id == "100"

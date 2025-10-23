"""
delete_defect_info および delete_repaird_info 関数の詳細テスト
"""

import pytest
import tempfile

from aoi_data_manager.sql_operations import SqlOperations
from aoi_data_manager.schema import DefectInfo, RepairdInfo


class TestDeleteDefectInfo:
    """delete_defect_info関数の詳細テスト"""

    def test_delete_existing_defect(self):
        """存在するDefectInfoの削除"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # データ挿入
                defect = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch",
                    x=100.0,
                    y=200.0,
                )
                sql_ops.insert_defect_info(defect)
                defect_id = defect.id

                # 削除前の確認
                assert sql_ops.get_defect_info_by_id(defect_id) is not None
                assert len(sql_ops.get_all_defect_info()) == 1

                # 削除実行
                result = sql_ops.delete_defect_info(defect_id)

                # 削除後の確認
                assert result is True
                assert sql_ops.get_defect_info_by_id(defect_id) is None
                assert len(sql_ops.get_all_defect_info()) == 0

    def test_delete_nonexistent_defect(self):
        """存在しないDefectInfoの削除"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # 存在しないIDで削除を試みる
                result = sql_ops.delete_defect_info("nonexistent_id_12345")

                # 削除失敗を確認
                assert result is False

    def test_delete_multiple_defects(self):
        """複数のDefectInfoを順番に削除"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # 3件のデータを挿入
                defects = []
                for i in range(3):
                    defect = DefectInfo(
                        line_name=f"LINE_{i:02d}",
                        model_code=f"Y{i:03d}",
                        lot_number=f"LOT{i:03d}",
                        current_board_index=1,
                        defect_number=1,
                        defect_name=f"defect_{i}",
                        x=float(i * 100),
                        y=float(i * 200),
                    )
                    sql_ops.insert_defect_info(defect)
                    defects.append(defect)

                # 全件確認
                assert len(sql_ops.get_all_defect_info()) == 3

                # 1件ずつ削除
                for i, defect in enumerate(defects):
                    result = sql_ops.delete_defect_info(defect.id)
                    assert result is True
                    assert len(sql_ops.get_all_defect_info()) == 2 - i

                # 全件削除確認
                assert len(sql_ops.get_all_defect_info()) == 0

    def test_delete_defect_with_lot_number_query(self):
        """削除後にlot_number検索で取得できないことを確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # 同じlot_numberで複数のデータを挿入
                defect1 = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch",
                    x=100.0,
                    y=200.0,
                )
                defect2 = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=2,  # 異なるdefect_number
                    defect_name="chip",
                    x=150.0,
                    y=250.0,
                )
                sql_ops.insert_defect_info(defect1)
                sql_ops.insert_defect_info(defect2)

                # lot_numberで検索
                lot_defects = sql_ops.get_defect_info_by_lot("LOT001")
                assert len(lot_defects) == 2

                # 1件削除
                result = sql_ops.delete_defect_info(defect1.id)
                assert result is True

                # lot_numberで検索して1件のみ残っていることを確認
                lot_defects = sql_ops.get_defect_info_by_lot("LOT001")
                assert len(lot_defects) == 1
                assert lot_defects[0].defect_number == 2

    def test_delete_and_reinsert_same_defect(self):
        """削除後に新しいデータを再挿入（IDは異なる）"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # データ挿入
                defect = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch",
                    x=100.0,
                    y=200.0,
                )
                sql_ops.insert_defect_info(defect)
                original_id = defect.id

                # 削除
                result = sql_ops.delete_defect_info(original_id)
                assert result is True
                assert sql_ops.get_defect_info_by_id(original_id) is None
                assert len(sql_ops.get_all_defect_info()) == 0

                # 同じlot_number/board/defect_numberで再挿入
                # （IDにdatetimeが含まれるため、異なるIDになる）
                defect_new = DefectInfo(
                    line_name="LINE_01_UPDATED",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch_updated",
                    x=150.0,
                    y=250.0,
                )
                sql_ops.insert_defect_info(defect_new)

                # 新しいデータが挿入されていることを確認
                assert len(sql_ops.get_all_defect_info()) == 1
                retrieved = sql_ops.get_defect_info_by_id(defect_new.id)
                assert retrieved is not None
                assert retrieved.line_name == "LINE_01_UPDATED"
                assert retrieved.defect_name == "scratch_updated"

                # 元のIDでは取得できないことを確認
                assert sql_ops.get_defect_info_by_id(original_id) is None


class TestDeleteRepairdInfo:
    """delete_repaird_info関数の詳細テスト"""

    def test_delete_existing_repaird(self):
        """存在するRepairdInfoの削除"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # DefectInfoを先に挿入（RepairdInfoのIDとして使用）
                defect = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch",
                    x=100.0,
                    y=200.0,
                )
                sql_ops.insert_defect_info(defect)

                # RepairdInfo挿入
                repaird = RepairdInfo(
                    id=defect.id,
                    is_repaird=True,
                    parts_type="CHIP",
                    kintone_record_id="kr001",
                )
                sql_ops.insert_repaird_info(repaird)

                # 削除前の確認
                assert sql_ops.get_repaird_info_by_id(defect.id) is not None
                assert len(sql_ops.get_all_repaird_info()) == 1

                # 削除実行
                result = sql_ops.delete_repaird_info(defect.id)

                # 削除後の確認
                assert result is True
                assert sql_ops.get_repaird_info_by_id(defect.id) is None
                assert len(sql_ops.get_all_repaird_info()) == 0

                # DefectInfoは削除されていないことを確認
                assert sql_ops.get_defect_info_by_id(defect.id) is not None

    def test_delete_nonexistent_repaird(self):
        """存在しないRepairdInfoの削除"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # 存在しないIDで削除を試みる
                result = sql_ops.delete_repaird_info("nonexistent_id_67890")

                # 削除失敗を確認
                assert result is False

    def test_delete_repaird_keeps_defect(self):
        """RepairdInfoを削除してもDefectInfoは残ることを確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # DefectInfoを挿入
                defect = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch",
                    x=100.0,
                    y=200.0,
                )
                sql_ops.insert_defect_info(defect)

                # RepairdInfo挿入
                repaird = RepairdInfo(
                    id=defect.id,
                    is_repaird=True,
                    parts_type="CHIP",
                    kintone_record_id="kr001",
                )
                sql_ops.insert_repaird_info(repaird)

                # RepairdInfoを削除
                result = sql_ops.delete_repaird_info(defect.id)
                assert result is True

                # DefectInfoは残っていることを確認
                remaining_defect = sql_ops.get_defect_info_by_id(defect.id)
                assert remaining_defect is not None
                assert remaining_defect.line_name == defect.line_name
                assert remaining_defect.defect_name == defect.defect_name


class TestDeleteOperationsEdgeCases:
    """削除操作のエッジケーステスト"""

    def test_delete_twice(self):
        """同じIDを2回削除"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # データ挿入
                defect = DefectInfo(
                    line_name="LINE_01",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch",
                    x=100.0,
                    y=200.0,
                )
                sql_ops.insert_defect_info(defect)
                defect_id = defect.id

                # 1回目の削除
                result1 = sql_ops.delete_defect_info(defect_id)
                assert result1 is True

                # 2回目の削除（既に存在しない）
                result2 = sql_ops.delete_defect_info(defect_id)
                assert result2 is False

    def test_delete_empty_string_id(self):
        """空文字列のIDで削除を試みる"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                # 空文字列で削除を試みる
                result = sql_ops.delete_defect_info("")
                assert result is False

    def test_delete_after_close(self):
        """close後の削除は例外を発生させる"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_ops = SqlOperations(db_url=temp_dir)
            sql_ops.create_tables()

            # データ挿入
            defect = DefectInfo(
                line_name="LINE_01",
                model_code="Y001",
                lot_number="LOT001",
                current_board_index=1,
                defect_number=1,
                defect_name="scratch",
                x=100.0,
                y=200.0,
            )
            sql_ops.insert_defect_info(defect)
            defect_id = defect.id

            # 接続を閉じる
            sql_ops.close()

            # close後の削除は例外を発生させる
            with pytest.raises(RuntimeError):
                sql_ops.delete_defect_info(defect_id)

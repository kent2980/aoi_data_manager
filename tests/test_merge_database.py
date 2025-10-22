"""
merge_target_database関数のテストモジュール
"""

import pytest
import tempfile
import os
from pathlib import Path

from aoi_data_manager.sql_operations import SqlOperations
from aoi_data_manager.schema import DefectInfo, RepairdInfo


class TestMergeDatabaseFunction:
    """merge_target_database関数のテストクラス"""

    def test_merge_empty_databases(self):
        """空のデータベース同士のマージ"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # データベース作成
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()

            # マージ実行
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                assert len(target_ops.get_all_defect_info()) == 0
                assert len(target_ops.get_all_repaird_info()) == 0

    def test_merge_with_new_data(self):
        """新規データのマージ"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ソースデータベースにデータ追加
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
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
                    line_name="LINE_02",
                    model_code="Y002",
                    lot_number="LOT002",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="chip",
                    x=150.0,
                    y=250.0,
                )
                source_ops.insert_defect_info(defect1)
                source_ops.insert_defect_info(defect2)

            # ターゲットデータベース作成
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()

            # マージ実行
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert len(defects) == 2
                assert any(d.line_name == "LINE_01" for d in defects)
                assert any(d.line_name == "LINE_02" for d in defects)

    def test_merge_with_duplicate_data(self):
        """重複データのマージ（更新）"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # 同じIDのデータを両方に追加
            defect_base = DefectInfo(
                line_name="LINE_01",
                model_code="Y001",
                lot_number="LOT001",
                current_board_index=1,
                defect_number=1,
                defect_name="scratch",
                x=100.0,
                y=200.0,
            )

            # ターゲットに古いデータ
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect_base)

            # ソースに更新データ（同じIDで異なる内容）
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                defect_updated = DefectInfo(
                    line_name="LINE_01_UPDATED",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch_updated",
                    x=150.0,
                    y=250.0,
                )
                source_ops.insert_defect_info(defect_updated)

            # マージ実行
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認 - データは1件のまま、内容が更新されている
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert len(defects) == 1
                assert defects[0].line_name == "LINE_01_UPDATED"
                assert defects[0].defect_name == "scratch_updated"
                assert defects[0].x == 150.0
                assert defects[0].y == 250.0

    def test_merge_with_mixed_data(self):
        """新規と既存が混在したデータのマージ"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ターゲットにデータ1追加
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
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
                target_ops.insert_defect_info(defect1)

            # ソースにデータ1（更新）とデータ2（新規）を追加
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                # 既存データの更新版
                defect1_updated = DefectInfo(
                    line_name="LINE_01_UPDATED",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch_updated",
                    x=150.0,
                    y=250.0,
                )
                # 新規データ
                defect2 = DefectInfo(
                    line_name="LINE_02",
                    model_code="Y002",
                    lot_number="LOT002",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="chip",
                    x=300.0,
                    y=400.0,
                )
                source_ops.insert_defect_info(defect1_updated)
                source_ops.insert_defect_info(defect2)

            # マージ実行
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert len(defects) == 2

                # 更新されたデータを確認
                defect1_result = next(d for d in defects if d.lot_number == "LOT001")
                assert defect1_result.line_name == "LINE_01_UPDATED"
                assert defect1_result.defect_name == "scratch_updated"

                # 新規データを確認
                defect2_result = next(d for d in defects if d.lot_number == "LOT002")
                assert defect2_result.line_name == "LINE_02"
                assert defect2_result.defect_name == "chip"

    def test_merge_repaird_info(self):
        """RepairdInfoのマージテスト"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ソースにRepairdInfoを追加
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                # まずDefectInfoを追加（RepairdInfoのIDとして使用）
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
                source_ops.insert_defect_info(defect1)

                repair1 = RepairdInfo(
                    id=defect1.id,
                    is_repaird=True,
                    parts_type="CHIP",
                    kintone_record_id="kr001",
                )
                source_ops.insert_repaird_info(repair1)

            # ターゲット作成
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()

            # マージ実行
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                repairs = target_ops.get_all_repaird_info()
                assert len(defects) == 1
                assert len(repairs) == 1
                assert repairs[0].is_repaird is True
                assert repairs[0].parts_type == "CHIP"

    def test_merge_large_dataset(self):
        """大量データのマージテスト"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ソースに100件のデータを追加
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                defects = []
                for i in range(100):
                    defect = DefectInfo(
                        line_name=f"LINE_{i:03d}",
                        model_code=f"Y{i:03d}",
                        lot_number=f"LOT{i:03d}",
                        current_board_index=1,
                        defect_number=1,
                        defect_name=f"defect_{i}",
                        x=float(i * 10),
                        y=float(i * 20),
                    )
                    defects.append(defect)
                source_ops.insert_defect_info_batch(defects)

            # ターゲット作成
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()

            # マージ実行
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects_result = target_ops.get_all_defect_info()
                assert len(defects_result) == 100

    def test_merge_error_handling(self):
        """エラーハンドリングのテスト"""
        with tempfile.TemporaryDirectory() as valid_dir:
            # 無効なパスでマージを試みる
            with pytest.raises(Exception):
                SqlOperations.merge_target_database(
                    source_db_url="/invalid/path/source", target_db_url=valid_dir
                )

    def test_merge_idempotency(self):
        """マージの冪等性テスト（同じマージを2回実行しても結果が同じ）"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ソースにデータ追加
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
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
                source_ops.insert_defect_info(defect)

            # ターゲット作成
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()

            # 1回目のマージ
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects_first = target_ops.get_all_defect_info()
                assert len(defects_first) == 1

            # 2回目のマージ（同じ操作）
            SqlOperations.merge_target_database(source_dir, target_dir)

            # 結果確認（データは1件のまま）
            with SqlOperations(db_url=target_dir) as target_ops:
                defects_second = target_ops.get_all_defect_info()
                assert len(defects_second) == 1
                assert defects_second[0].id == defects_first[0].id
                assert defects_second[0].line_name == defects_first[0].line_name

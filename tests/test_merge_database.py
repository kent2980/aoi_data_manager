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
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

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
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert len(defects) == 2
                assert any(d.line_name == "LINE_01" for d in defects)
                assert any(d.line_name == "LINE_02" for d in defects)

    def test_merge_with_duplicate_data(self):
        """重複データのマージ（更新）"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # 同じIDのデータを両方に追加するため、同じオブジェクトを使用
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

            # 一度IDを生成
            original_id = defect_base.id
            original_datetime = defect_base.insert_datetime

            # ターゲットに元のデータを挿入
            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect_base)

            # ソースに同じIDで更新されたデータを挿入（手動でIDとdatetimeを設定）
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                defect_updated = DefectInfo(
                    id=original_id,  # 同じIDを使用
                    line_name="LINE_01_UPDATED",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch_updated",
                    x=150.0,
                    y=250.0,
                    insert_datetime=original_datetime,  # 同じdatetimeを使用
                )
                source_ops.insert_defect_info(defect_updated)

            # マージ実行
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

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

            # IDとdatetimeを保存
            original_id = defect1.id
            original_datetime = defect1.insert_datetime

            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect1)

            # ソースにデータ1（更新）とデータ2（新規）を追加
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                # 既存データの更新版（同じIDを使用）
                defect1_updated = DefectInfo(
                    id=original_id,  # 同じIDを使用
                    line_name="LINE_01_UPDATED",
                    model_code="Y001",
                    lot_number="LOT001",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="scratch_updated",
                    x=150.0,
                    y=250.0,
                    insert_datetime=original_datetime,  # 同じdatetimeを使用
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
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

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
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

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
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

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
                    source_db_url="/invalid/path/source",
                    target_db_url=valid_dir,
                    db_name="aoi_data.db",
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
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects_first = target_ops.get_all_defect_info()
                assert len(defects_first) == 1

            # 2回目のマージ（同じ操作）
            SqlOperations.merge_target_database(
                source_dir, target_dir, db_name="aoi_data.db"
            )

            # 結果確認（データは1件のまま）
            with SqlOperations(db_url=target_dir) as target_ops:
                defects_second = target_ops.get_all_defect_info()
                assert len(defects_second) == 1
                assert defects_second[0].id == defects_first[0].id
                assert defects_second[0].line_name == defects_first[0].line_name

    def test_merge_with_delete_sync(self):
        """削除を使ったデータ同期のテスト"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ターゲットに3件のデータを追加
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
            defect3 = DefectInfo(
                line_name="LINE_03",
                model_code="Y003",
                lot_number="LOT003",
                current_board_index=1,
                defect_number=1,
                defect_name="crack",
                x=200.0,
                y=300.0,
            )

            # IDを保存
            id1 = defect1.id
            id2 = defect2.id
            id3 = defect3.id

            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect1)
                target_ops.insert_defect_info(defect2)
                target_ops.insert_defect_info(defect3)

            # ソースには新しいデータ1件のみ（他は削除対象）
            defect_new = DefectInfo(
                line_name="LINE_NEW",
                model_code="Y999",
                lot_number="LOT999",
                current_board_index=1,
                defect_number=1,
                defect_name="new_defect",
                x=999.0,
                y=999.0,
            )

            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()
                source_ops.insert_defect_info(defect_new)

            # マージ実行：新規データを追加し、指定したIDを削除
            SqlOperations.merge_target_database(
                source_dir,
                target_dir,
                db_name="aoi_data.db",
                delete_defect_ids=[id2, id3],  # defect2とdefect3を削除
            )

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                # defect1（残存）とdefect_new（新規）の2件のみ
                assert len(defects) == 2

                lot_numbers = [d.lot_number for d in defects]
                assert "LOT001" in lot_numbers  # defect1は残る
                assert "LOT999" in lot_numbers  # defect_newは追加
                assert "LOT002" not in lot_numbers  # defect2は削除
                assert "LOT003" not in lot_numbers  # defect3は削除

    def test_merge_with_repaird_delete_sync(self):
        """RepairdInfo削除を使ったデータ同期のテスト"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ターゲットにDefectInfoとRepairdInfoを追加
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

            id1 = defect1.id
            id2 = defect2.id

            repair1 = RepairdInfo(
                id=id1,
                is_repaird=True,
                parts_type="CHIP",
                kintone_record_id="kr001",
            )
            repair2 = RepairdInfo(
                id=id2,
                is_repaird=False,
                parts_type="RESISTOR",
                kintone_record_id="kr002",
            )

            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect1)
                target_ops.insert_defect_info(defect2)
                target_ops.insert_repaird_info(repair1)
                target_ops.insert_repaird_info(repair2)

            # ソースは空
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()

            # マージ実行：repair2のみ削除
            SqlOperations.merge_target_database(
                source_dir,
                target_dir,
                db_name="aoi_data.db",
                delete_repaird_ids=[id2],
            )

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                repairs = target_ops.get_all_repaird_info()

                # DefectInfoは2件とも残る
                assert len(defects) == 2

                # RepairdInfoはrepair1のみ残る
                assert len(repairs) == 1
                assert repairs[0].id == id1
                assert repairs[0].parts_type == "CHIP"

    def test_merge_full_sync(self):
        """完全同期テスト：追加・更新・削除の組み合わせ"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ターゲットに初期データ
            target_defect1 = DefectInfo(
                line_name="TARGET_01",
                model_code="Y001",
                lot_number="LOT001",
                current_board_index=1,
                defect_number=1,
                defect_name="old_defect",
                x=100.0,
                y=200.0,
            )
            target_defect2 = DefectInfo(
                line_name="TARGET_02",
                model_code="Y002",
                lot_number="LOT002",
                current_board_index=1,
                defect_number=1,
                defect_name="to_delete",
                x=150.0,
                y=250.0,
            )
            target_defect3 = DefectInfo(
                line_name="TARGET_03",
                model_code="Y003",
                lot_number="LOT003",
                current_board_index=1,
                defect_number=1,
                defect_name="to_update",
                x=200.0,
                y=300.0,
            )

            id1 = target_defect1.id
            id2 = target_defect2.id
            id3 = target_defect3.id
            dt3 = target_defect3.insert_datetime

            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(target_defect1)
                target_ops.insert_defect_info(target_defect2)
                target_ops.insert_defect_info(target_defect3)

            # ソースデータ
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()

                # 更新データ（defect3の内容を変更、同じIDを使用）
                updated_defect3 = DefectInfo(
                    id=id3,
                    line_name="SOURCE_03_UPDATED",
                    model_code="Y003",
                    lot_number="LOT003",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="updated_defect",
                    x=999.0,
                    y=999.0,
                    insert_datetime=dt3,
                )

                # 新規データ
                new_defect = DefectInfo(
                    line_name="SOURCE_NEW",
                    model_code="Y999",
                    lot_number="LOT999",
                    current_board_index=1,
                    defect_number=1,
                    defect_name="new_defect",
                    x=500.0,
                    y=600.0,
                )

                source_ops.insert_defect_info(updated_defect3)
                source_ops.insert_defect_info(new_defect)

            # マージ実行：defect2を削除
            SqlOperations.merge_target_database(
                source_dir,
                target_dir,
                db_name="aoi_data.db",
                delete_defect_ids=[id2],
            )

            # 結果確認
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert (
                    len(defects) == 3
                )  # defect1（保持）、defect3（更新）、new_defect（新規）

                lot_numbers = {d.lot_number: d for d in defects}

                # defect1は変更なし
                assert "LOT001" in lot_numbers
                assert lot_numbers["LOT001"].line_name == "TARGET_01"

                # defect2は削除
                assert "LOT002" not in lot_numbers

                # defect3は更新
                assert "LOT003" in lot_numbers
                assert lot_numbers["LOT003"].line_name == "SOURCE_03_UPDATED"
                assert lot_numbers["LOT003"].defect_name == "updated_defect"
                assert lot_numbers["LOT003"].x == 999.0

                # new_defectは新規追加
                assert "LOT999" in lot_numbers
                assert lot_numbers["LOT999"].line_name == "SOURCE_NEW"

    def test_merge_delete_nonexistent_ids(self):
        """存在しないIDを削除指定した場合のテスト"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ターゲットにデータ追加
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

            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect)

            # ソース作成
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()

            # 存在しないIDを削除指定
            SqlOperations.merge_target_database(
                source_dir,
                target_dir,
                db_name="aoi_data.db",
                delete_defect_ids=["nonexistent_id_1", "nonexistent_id_2"],
            )

            # 結果確認：既存データは影響を受けない
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert len(defects) == 1
                assert defects[0].lot_number == "LOT001"

    def test_merge_delete_all_data(self):
        """全データ削除の同期テスト"""
        with tempfile.TemporaryDirectory() as source_dir, tempfile.TemporaryDirectory() as target_dir:
            # ターゲットにデータ追加
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

            id1 = defect1.id
            id2 = defect2.id

            with SqlOperations(db_url=target_dir) as target_ops:
                target_ops.create_tables()
                target_ops.insert_defect_info(defect1)
                target_ops.insert_defect_info(defect2)

            # ソースは空
            with SqlOperations(db_url=source_dir) as source_ops:
                source_ops.create_tables()

            # 全データを削除
            SqlOperations.merge_target_database(
                source_dir,
                target_dir,
                db_name="aoi_data.db",
                delete_defect_ids=[id1, id2],
            )

            # 結果確認：全データが削除される
            with SqlOperations(db_url=target_dir) as target_ops:
                defects = target_ops.get_all_defect_info()
                assert len(defects) == 0

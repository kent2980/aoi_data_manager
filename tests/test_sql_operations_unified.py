"""
SqlOperations統合テストスイート
SqlOperationsクラスの全機能を網羅したテスト
- 基本機能テスト
- 32bit環境対応テスト
- 自動切断機能テスト
- パフォーマンステスト
- エラーハンドリングテスト
"""

import pytest
import tempfile
import time
import uuid
import gc
import weakref
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

try:
    import psutil

    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

from aoi_data_manager.sql_operations import SqlOperations
from aoi_data_manager.db_models import DefectInfo, RepairdInfo


# ===== フィクスチャ =====


@pytest.fixture
def temp_db():
    """テスト用の一時データベースを作成するfixture（自動切断対応）"""
    with tempfile.TemporaryDirectory() as temp_dir:
        with SqlOperations(db_url=temp_dir) as sql_ops:
            sql_ops.create_tables()
            yield sql_ops


@pytest.fixture
def sample_defect_data():
    """テスト用のサンプル不良データ"""
    return DefectInfo(
        id=str(uuid.uuid4()),
        line_name="LINE_01",
        model_code="Y001",
        lot_number="LOT001",
        current_board_index=1,
        defect_number=1,
        serial="QR001",
        reference="R001",
        defect_name="scratch",
        x=100,
        y=200,
        aoi_user="test_user",
        model_label="model_test",
        board_label="board_test",
        kintone_record_id="k001",
    )


@pytest.fixture
def sample_repair_data():
    """テスト用のサンプル修理データ"""
    return RepairdInfo(
        id=str(uuid.uuid4()),
        is_repaird=True,
        parts_type="CHIP",
        kintone_record_id="kr001",
    )


# ===== 基本機能テスト =====


class TestSqlOperationsBasicFunctionality:
    """SqlOperationsクラスの基本機能テスト"""

    def test_initialization(self):
        """初期化テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                assert sql_ops.db_url == temp_dir
                assert sql_ops.engine is not None
                assert not sql_ops._closed

    def test_table_creation(self):
        """テーブル作成テスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            with SqlOperations(db_url=temp_dir) as sql_ops:
                result = sql_ops.create_tables()
                assert result is None  # create_tablesは戻り値なし
                assert sql_ops.engine is not None

    def test_defect_info_insertion(self, temp_db, sample_defect_data):
        """DefectInfo挿入テスト"""
        result = temp_db.insert_defect_info(sample_defect_data)
        assert result is None  # insert_defect_infoは戻り値なし

    def test_defect_info_insertion_success_verification(
        self, temp_db, sample_defect_data
    ):
        """DefectInfo挿入成功の詳細確認テスト"""
        # 挿入前の状態確認
        initial_count = len(temp_db.get_all_defect_info())

        # データ挿入（ID事前取得でDetachedInstanceError回避）
        defect_id = sample_defect_data.id
        line_name = sample_defect_data.line_name
        model_code = sample_defect_data.model_code
        lot_number = sample_defect_data.lot_number
        current_board_index = sample_defect_data.current_board_index
        defect_number = sample_defect_data.defect_number
        defect_name = sample_defect_data.defect_name
        x = sample_defect_data.x
        y = sample_defect_data.y

        temp_db.insert_defect_info(sample_defect_data)

        # 挿入後の確認
        # 1. 総件数が1件増加していることを確認
        after_count = len(temp_db.get_all_defect_info())
        assert after_count == initial_count + 1

        # 2. 挿入したデータがIDで取得できることを確認
        retrieved_data = temp_db.get_defect_info_by_id(defect_id)
        assert retrieved_data is not None

        # 3. 挿入したデータの内容が正確に保存されていることを確認
        assert retrieved_data.id == defect_id
        assert retrieved_data.line_name == line_name
        assert retrieved_data.model_code == model_code
        assert retrieved_data.lot_number == lot_number
        assert retrieved_data.current_board_index == current_board_index
        assert retrieved_data.defect_number == defect_number
        assert retrieved_data.defect_name == defect_name
        assert retrieved_data.x == x
        assert retrieved_data.y == y

        # 4. 指図番号での検索でも取得できることを確認
        lot_results = temp_db.get_defect_info_by_lot(lot_number)
        assert len(lot_results) >= 1
        found = any(defect.id == defect_id for defect in lot_results)
        assert found, "挿入したデータが指図番号検索で見つからない"

        # 5. 全件取得でも含まれていることを確認
        all_results = temp_db.get_all_defect_info()
        found_in_all = any(defect.id == defect_id for defect in all_results)
        assert found_in_all, "挿入したデータが全件取得で見つからない"

    def test_repair_info_insertion(self, temp_db, sample_repair_data):
        """RepairdInfo挿入テスト"""
        result = temp_db.insert_repaird_info(sample_repair_data)
        assert result is None  # insert_repaird_infoは戻り値なし

    def test_multiple_defect_info_insertion_success(self, temp_db):
        """複数のDefectInfo挿入成功テスト"""
        # テスト用の複数データを作成
        defect_data_list = []
        expected_data = []  # 検証用データを別途保存

        for i in range(3):
            defect_id = str(uuid.uuid4())
            line_name = f"LINE_{i+1:02d}"
            model_code = f"Y{i+1:03d}"
            lot_number = f"LOT{i+1:03d}"

            defect_data = DefectInfo(
                id=defect_id,
                line_name=line_name,
                model_code=model_code,
                lot_number=lot_number,
                current_board_index=i + 1,
                defect_number=i + 1,
                defect_name=f"defect_type_{i+1}",
                x=100 + i * 10,
                y=200 + i * 10,
            )
            defect_data_list.append(defect_data)
            # 検証用データを保存（DetachedInstanceError回避）
            expected_data.append(
                {
                    "id": defect_id,
                    "line_name": line_name,
                    "model_code": model_code,
                    "lot_number": lot_number,
                    "current_board_index": i + 1,
                    "defect_number": i + 1,
                }
            )

        # 挿入前の件数確認
        initial_count = len(temp_db.get_all_defect_info())

        # 各データを挿入
        for defect_data in defect_data_list:
            temp_db.insert_defect_info(defect_data)

        # 挿入後の確認
        final_count = len(temp_db.get_all_defect_info())
        assert final_count == initial_count + 3

        # 各データが正しく挿入されていることを確認
        for expected in expected_data:
            retrieved = temp_db.get_defect_info_by_id(expected["id"])
            assert retrieved is not None
            assert retrieved.line_name == expected["line_name"]
            assert retrieved.lot_number == expected["lot_number"]
            assert retrieved.current_board_index == expected["current_board_index"]

    def test_defect_info_insertion_with_special_characters(self, temp_db):
        """特殊文字を含むDefectInfo挿入テスト"""
        # 検証用データを事前に変数として保存
        defect_id = str(uuid.uuid4())
        line_name = "LINE_特殊文字テスト"
        model_code = "Y001-αβγ"
        lot_number = "LOT001_検査済み"
        defect_name = "不良タイプ_漢字混合123"
        serial = "SN_αβγδε_12345"
        reference = "REF_参照番号_ABC"
        aoi_user = "ユーザー名_日本語"

        defect_data = DefectInfo(
            id=defect_id,
            line_name=line_name,
            model_code=model_code,
            lot_number=lot_number,
            current_board_index=1,
            defect_number=999,
            defect_name=defect_name,
            x=12345,
            y=67890,
            serial=serial,
            reference=reference,
            aoi_user=aoi_user,
        )

        # 挿入
        temp_db.insert_defect_info(defect_data)

        # 取得して確認
        retrieved = temp_db.get_defect_info_by_id(defect_id)
        assert retrieved is not None
        assert retrieved.line_name == line_name
        assert retrieved.model_code == model_code
        assert retrieved.lot_number == lot_number
        assert retrieved.defect_name == defect_name
        assert retrieved.serial == serial
        assert retrieved.reference == reference
        assert retrieved.aoi_user == aoi_user

    def test_get_defect_info_by_id_exists(self, temp_db, sample_defect_data):
        """存在するIDでのDefectInfo取得テスト"""
        defect_id = sample_defect_data.id  # IDを事前に取得
        temp_db.insert_defect_info(sample_defect_data)

        result = temp_db.get_defect_info_by_id(defect_id)
        assert result is not None
        assert result.id == defect_id
        assert result.line_name == "LINE_01"
        assert result.defect_name == "scratch"

    def test_get_defect_info_by_id_not_exists(self, temp_db):
        """存在しないIDでのDefectInfo取得テスト"""
        result = temp_db.get_defect_info_by_id("nonexistent_id")
        assert result is None

    def test_get_all_defect_info(self, temp_db, sample_defect_data):
        """全DefectInfo取得テスト"""
        temp_db.insert_defect_info(sample_defect_data)

        result = temp_db.get_all_defect_info()
        assert len(result) >= 1
        assert result[0].line_name == "LINE_01"

    def test_get_defect_info_by_lot(self, temp_db):
        """指図番号でのDefectInfo取得テスト"""
        lot_number = "LOT_TEST_001"
        defect_data = DefectInfo(
            id=str(uuid.uuid4()),
            line_name="LINE_01",
            model_code="Y001",
            lot_number=lot_number,
            current_board_index=1,
            defect_number=1,
            defect_name="scratch",
        )
        temp_db.insert_defect_info(defect_data)

        result = temp_db.get_defect_info_by_lot(lot_number)
        assert len(result) >= 1
        assert result[0].lot_number == lot_number

    def test_get_repair_info_by_id(self, temp_db, sample_repair_data):
        """RepairdInfo取得テスト"""
        repair_id = sample_repair_data.id  # IDを事前に取得
        temp_db.insert_repaird_info(sample_repair_data)

        result = temp_db.get_repaird_info_by_id(repair_id)
        assert result is not None
        assert result.id == repair_id
        assert result.is_repaird is True

    def test_get_all_repair_info(self, temp_db, sample_repair_data):
        """全RepairdInfo取得テスト"""
        temp_db.insert_repaird_info(sample_repair_data)

        result = temp_db.get_all_repaird_info()
        assert len(result) >= 1


# ===== バッチ操作テスト =====


class TestSqlOperationsBatchOperations:
    """バッチ操作テスト"""

    def test_defect_info_batch_insert(self, temp_db):
        """DefectInfoバッチ挿入テスト"""
        defect_list = []
        for i in range(5):
            defect_data = DefectInfo(
                id=str(uuid.uuid4()),
                line_name="LINE_01",
                model_code="Y001",
                lot_number=f"LOT_{i:03d}",
                current_board_index=i,
                defect_number=i,
                serial=f"QR_{i:03d}",
                reference=f"R_{i:03d}",
                defect_name="scratch",
                x=100 + i,
                y=200 + i,
            )
            defect_list.append(defect_data)

        result = temp_db.insert_defect_info_batch(defect_list)
        assert result is None  # insert_defect_info_batchは戻り値なし

        # 挿入されたデータを確認
        all_data = temp_db.get_all_defect_info()
        assert len(all_data) >= 5

    def test_repair_info_batch_insert(self, temp_db):
        """RepairdInfoバッチ挿入テスト"""
        repair_list = []
        for i in range(3):
            repair_data = RepairdInfo(
                id=str(uuid.uuid4()),
                is_repaird=i % 2 == 0,
                parts_type=f"CHIP_{i}",
                kintone_record_id=f"kr_{i:03d}",
            )
            repair_list.append(repair_data)

        result = temp_db.insert_repaird_info_batch(repair_list)
        assert result is None  # insert_repaird_info_batchは戻り値なし

        # 挿入されたデータを確認
        all_data = temp_db.get_all_repaird_info()
        assert len(all_data) >= 3


# ===== 削除操作テスト =====


class TestSqlOperationsDeleteOperations:
    """削除操作テスト"""

    def test_delete_defect_info_success(self, temp_db, sample_defect_data):
        """DefectInfo削除成功テスト"""
        defect_id = sample_defect_data.id  # IDを事前に取得
        temp_db.insert_defect_info(sample_defect_data)

        result = temp_db.delete_defect_info(defect_id)
        assert result is True

        # 削除確認
        deleted_data = temp_db.get_defect_info_by_id(defect_id)
        assert deleted_data is None

    def test_delete_defect_info_not_exists(self, temp_db):
        """存在しないDefectInfo削除テスト"""
        result = temp_db.delete_defect_info("nonexistent_id")
        assert result is False

    def test_delete_repair_info_success(self, temp_db, sample_repair_data):
        """RepairdInfo削除成功テスト"""
        repair_id = sample_repair_data.id  # IDを事前に取得
        temp_db.insert_repaird_info(sample_repair_data)

        result = temp_db.delete_repaird_info(repair_id)
        assert result is True

        # 削除確認
        deleted_data = temp_db.get_repaird_info_by_id(repair_id)
        assert deleted_data is None

    def test_delete_repair_info_not_exists(self, temp_db):
        """存在しないRepairdInfo削除テスト"""
        result = temp_db.delete_repaird_info("nonexistent_id")
        assert result is False


# ===== 自動切断機能テスト =====


class TestSqlOperationsAutoDisconnect:
    """自動切断機能テスト"""

    def test_context_manager_usage(self):
        """with文を使用した自動切断のテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            defect_id = str(uuid.uuid4())

            with SqlOperations(db_url=temp_dir) as sql_ops:
                sql_ops.create_tables()

                defect_data = DefectInfo(
                    id=defect_id, line_name="LINE_01", defect_name="scratch"
                )
                sql_ops.insert_defect_info(defect_data)

                result = sql_ops.get_defect_info_by_id(defect_id)
                assert result is not None
                assert result.line_name == "LINE_01"

                # この時点ではまだ接続は有効
                assert not sql_ops._closed

            # with文を抜けた後は自動的に切断されている
            assert sql_ops._closed

    def test_manual_close(self):
        """手動でclose()を呼ぶテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_ops = SqlOperations(db_url=temp_dir)

            try:
                sql_ops.create_tables()
                assert not sql_ops._closed

                sql_ops.close()
                assert sql_ops._closed

            except Exception:
                sql_ops.close()
                raise

    def test_operations_after_close_raise_error(self):
        """close()後の操作がエラーを発生させることのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_ops = SqlOperations(db_url=temp_dir)
            sql_ops.create_tables()
            sql_ops.close()

            with pytest.raises(
                RuntimeError, match="SqlOperations instance has been closed"
            ):
                sql_ops.create_tables()

    def test_multiple_close_calls_safe(self):
        """複数回close()を呼んでも安全であることのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_ops = SqlOperations(db_url=temp_dir)
            sql_ops.create_tables()

            sql_ops.close()
            sql_ops.close()
            sql_ops.close()

            assert sql_ops._closed

    def test_context_manager_with_exception(self):
        """with文内で例外が発生した場合でも適切に切断されることのテスト"""
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                with SqlOperations(db_url=temp_dir) as sql_ops:
                    sql_ops.create_tables()
                    raise ValueError("Test exception")
            except ValueError:
                assert sql_ops._closed


# ===== 32bit環境対応テスト =====


@pytest.mark.bit32
class TestSqlOperations32BitCompatibility:
    """32bit環境対応テスト"""

    def test_platform_detection(self):
        """プラットフォーム検出テスト"""
        import platform

        arch = platform.architecture()[0]
        machine = platform.machine()

        print(f"Architecture: {arch}")
        print(f"Machine: {machine}")
        print(f"Platform: {platform.platform()}")

        assert arch in ["32bit", "64bit"]

    @pytest.mark.memory_intensive
    def test_small_batch_processing(self, temp_db):
        """32bit環境での小規模バッチ処理テスト"""
        defect_list = []
        for i in range(10):  # 32bit環境を考慮した小さなサイズ
            defect_data = DefectInfo(
                id=str(uuid.uuid4()),
                line_name="LINE_01",
                lot_number=f"BATCH_{i:03d}",
                current_board_index=i,
                defect_number=i,
                defect_name="scratch",
                x=i * 10,
                y=i * 20,
            )
            defect_list.append(defect_data)

        temp_db.insert_defect_info_batch(defect_list)

        all_data = temp_db.get_all_defect_info()
        assert len(all_data) >= 10

    @pytest.mark.skipif(not PSUTIL_AVAILABLE, reason="psutil not available")
    def test_memory_usage_monitoring(self, temp_db):
        """メモリ使用量監視テスト"""
        import psutil

        process = psutil.Process()
        start_memory = process.memory_info().rss

        # 少量のデータ操作
        defect_data = DefectInfo(
            id=str(uuid.uuid4()), line_name="LINE_01", defect_name="scratch"
        )
        temp_db.insert_defect_info(defect_data)

        end_memory = process.memory_info().rss
        memory_increase = end_memory - start_memory

        print(f"Memory increase: {memory_increase / (1024*1024):.2f} MB")

        # 32bit環境では大幅なメモリ増加は避けるべき
        assert memory_increase < 100 * 1024 * 1024  # 100MB未満

    def test_unicode_handling(self, temp_db):
        """Unicode文字列処理テスト"""
        defect_id = str(uuid.uuid4())
        defect_data = DefectInfo(
            id=defect_id,
            line_name="ライン_01",
            model_code="モデル_Y001",
            defect_name="スクラッチ",
            serial="シリアル_001",
        )

        temp_db.insert_defect_info(defect_data)

        result = temp_db.get_defect_info_by_id(defect_id)
        assert result is not None
        assert result.line_name == "ライン_01"
        assert result.defect_name == "スクラッチ"


# ===== パフォーマンステスト =====


@pytest.mark.slow
class TestSqlOperationsPerformance:
    """パフォーマンステスト"""

    def test_batch_vs_individual_insertion_performance(self, temp_db):
        """バッチ挿入と個別挿入のパフォーマンス比較"""
        # バッチ挿入用データ
        batch_data = []
        for i in range(20):  # 32bit環境を考慮した適度なサイズ
            defect_data = DefectInfo(
                id=str(uuid.uuid4()),
                line_name="LINE_01",
                lot_number=f"PERF_BATCH_{i:03d}",
                current_board_index=i,
                defect_number=i,
                defect_name="scratch",
            )
            batch_data.append(defect_data)

        # バッチ挿入実行
        start_time = time.time()
        temp_db.insert_defect_info_batch(batch_data)
        batch_time = time.time() - start_time

        print(f"Batch insertion time: {batch_time:.4f} seconds")

        # データが正しく挿入されたか確認
        all_data = temp_db.get_all_defect_info()
        assert len(all_data) >= 20

        # 32bit環境でも合理的な時間内で完了することを確認
        assert batch_time < 5.0  # 5秒未満

    def test_query_performance(self, temp_db):
        """クエリパフォーマンステスト"""
        # テストデータ準備
        defect_list = []
        first_defect_id = str(uuid.uuid4())
        for i in range(50):
            defect_id = first_defect_id if i == 0 else str(uuid.uuid4())
            defect_data = DefectInfo(
                id=defect_id,
                line_name=f"LINE_{i//10 + 1:02d}",
                lot_number=f"QUERY_PERF_{i:03d}",
                current_board_index=i,
                defect_number=i,
                defect_name="scratch",
            )
            defect_list.append(defect_data)

        temp_db.insert_defect_info_batch(defect_list)

        # クエリパフォーマンステスト
        start_time = time.time()

        # 複数の異なるクエリを実行
        all_data = temp_db.get_all_defect_info()
        lot_data = temp_db.get_defect_info_by_lot("QUERY_PERF_010")
        individual_data = temp_db.get_defect_info_by_id(first_defect_id)

        query_time = time.time() - start_time

        print(f"Query performance time: {query_time:.4f} seconds")

        # 結果確認
        assert len(all_data) >= 50
        assert len(lot_data) >= 1
        assert individual_data is not None

        # パフォーマンス要件
        assert query_time < 2.0  # 2秒未満


# ===== エラーハンドリングテスト =====


class TestSqlOperationsErrorHandling:
    """エラーハンドリングテスト"""

    def test_invalid_path_initialization(self):
        """無効パスでの初期化テスト"""
        # SQLiteは無効なパスでも初期化は成功する
        sql_ops = SqlOperations(db_url="/invalid/path")
        assert sql_ops.db_url == "/invalid/path"
        assert sql_ops.engine is not None
        sql_ops.close()

    def test_error_recovery(self, temp_db):
        """エラー回復テスト"""
        # 無効なデータでの挿入試行
        invalid_defect = DefectInfo(
            id="", line_name="", defect_name="", x=-1, y=-1  # 空のID
        )

        # エラーが適切に処理されることを確認
        # SQLModelの実装に依存するが、例外が発生するかFalseが返される
        try:
            temp_db.insert_defect_info(invalid_defect)
        except Exception:
            pass  # 例外が発生することを許容


# ===== 統合テスト =====


class TestSqlOperationsIntegration:
    """統合テスト"""

    def test_complete_workflow(self, temp_db):
        """完全なワークフローテスト"""
        # 1. DefectInfo挿入
        defect_id = str(uuid.uuid4())
        defect_data = DefectInfo(
            id=defect_id,
            line_name="LINE_01",
            model_code="Y001",
            lot_number="INTEGRATION_001",
            current_board_index=1,
            defect_number=1,
            defect_name="scratch",
            x=100,
            y=200,
        )
        temp_db.insert_defect_info(defect_data)

        # 2. データ取得
        retrieved_data = temp_db.get_defect_info_by_id(defect_id)
        assert retrieved_data is not None
        assert retrieved_data.line_name == "LINE_01"

        # 3. RepairdInfo挿入
        repair_data = RepairdInfo(
            id=str(uuid.uuid4()), is_repaird=True, parts_type="CHIP"
        )
        temp_db.insert_repaird_info(repair_data)

        # 4. 全データ取得
        all_defects = temp_db.get_all_defect_info()
        all_repairs = temp_db.get_all_repaird_info()
        assert len(all_defects) >= 1
        assert len(all_repairs) >= 1

        # 5. データ削除
        delete_result = temp_db.delete_defect_info(defect_id)
        assert delete_result is True

    def test_concurrent_operations_simulation(self, temp_db):
        """同時操作シミュレーションテスト"""
        # 複数の操作を連続して実行
        operations_count = 10

        for i in range(operations_count):
            # 挿入
            defect_id = str(uuid.uuid4())
            defect_data = DefectInfo(
                id=defect_id,
                line_name=f"LINE_{i % 3 + 1:02d}",
                lot_number=f"CONCURRENT_{i:03d}",
                current_board_index=i,
                defect_number=i,
                defect_name="scratch",
            )
            temp_db.insert_defect_info(defect_data)

            # 取得
            result = temp_db.get_defect_info_by_id(defect_id)
            assert result is not None

            # 削除（半分のデータ）
            if i % 2 == 0:
                delete_result = temp_db.delete_defect_info(defect_id)
                assert delete_result is True

        # 最終確認
        final_data = temp_db.get_all_defect_info()
        assert len(final_data) >= operations_count // 2


# ===== 後方互換性テスト =====


class TestSqlOperationsBackwardCompatibility:
    """後方互換性テスト"""

    def test_existing_usage_pattern(self):
        """既存の使用パターンがまだ動作することの確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            sql_ops = SqlOperations(db_url=temp_dir)
            try:
                sql_ops.create_tables()

                defect_id = str(uuid.uuid4())
                defect_data = DefectInfo(
                    id=defect_id, line_name="LINE_01", defect_name="scratch"
                )
                sql_ops.insert_defect_info(defect_data)

                result = sql_ops.get_defect_info_by_id(defect_id)
                assert result is not None
            finally:
                sql_ops.close()

    def test_migration_path(self):
        """新旧の使用方法の移行パス確認"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # 古い方法
            sql_ops_old = SqlOperations(db_url=temp_dir)
            try:
                sql_ops_old.create_tables()
            finally:
                sql_ops_old.close()

            # 新しい方法（推奨）
            with SqlOperations(db_url=temp_dir) as sql_ops_new:
                defect_id = str(uuid.uuid4())
                defect_data = DefectInfo(
                    id=defect_id, line_name="LINE_01", defect_name="scratch"
                )
                sql_ops_new.insert_defect_info(defect_data)

                result = sql_ops_new.get_defect_info_by_id(defect_id)
                assert result is not None

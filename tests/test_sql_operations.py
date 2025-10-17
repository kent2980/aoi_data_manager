import pytest
from unittest.mock import Mock, patch, MagicMock
from pathlib import Path
import time
import uuid
from sqlalchemy import create_engine, inspect
from sqlmodel import Session

from aoi_data_manager.sql_operations import SqlOperations
from aoi_data_manager.db_models import DefectInfo, RepairdInfo


def get_unique_test_name(base_name: str) -> str:
    """テスト用の一意な名前を生成"""
    timestamp = str(int(time.time() * 1000))
    return f"{base_name}_{timestamp}"


class TestSqlOperationsInitialization:
    """SqlOperationsクラスの初期化テスト"""

    def test_sqlite_initialization(self):
        """SQLiteでの初期化をテスト"""
        sql_ops = SqlOperations("sqlite", "test_db")
        assert sql_ops.db_engine == "sqlite"
        assert "test_db" in sql_ops.db_url

    def test_postgres_initialization(self):
        """PostgreSQLでの初期化をテスト"""
        db_url = "user:pass@localhost:5432/testdb"
        sql_ops = SqlOperations("postgresql", db_url)
        assert sql_ops.db_engine == "postgresql"
        assert db_url in sql_ops.db_url

    def test_invalid_database_type(self):
        """無効なデータベースタイプでのエラーテスト"""
        with pytest.raises(ValueError, match="Unsupported database engine"):
            SqlOperations("mysql", "test.db")


class TestSqlOperationsEngine:
    """エンジン作成とセッション管理のテスト"""

    def test_sqlite_engine_creation(self):
        """SQLiteエンジンの作成をテスト"""
        sql_ops = SqlOperations("sqlite", "test_db")
        engine = sql_ops.engine
        assert engine is not None
        assert hasattr(engine, "dialect")

    @patch("aoi_data_manager.sql_operations.create_engine")
    def test_postgres_engine_creation(self, mock_create_engine):
        """PostgreSQLエンジンの作成をテスト（モック使用）"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        sql_ops = SqlOperations("postgresql", "user:pass@localhost:5432/testdb")

        engine = sql_ops.engine
        assert engine == mock_engine
        mock_create_engine.assert_called_once()


class TestSqlOperationsTableCreation:
    """テーブル作成のテスト"""

    def test_create_tables(self):
        """テーブル作成をテスト"""
        # テスト用のディレクトリを作成
        test_dir = Path("test_tables")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_tables")
        sql_ops.create_tables()

        # テーブルが作成されたか確認
        inspector = inspect(sql_ops.engine)
        tables = inspector.get_table_names()

        # DefectInfoとRepairdInfoのテーブルが作成されることを確認
        assert "defectinfo" in tables
        assert "repairdinfo" in tables

        # クリーンアップ
        try:
            Path("test_tables/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


class TestSqlOperationsErrorHandling:
    """エラーハンドリングのテスト"""

    def test_invalid_database_engine(self):
        """無効なデータベースエンジンでのエラーテスト"""
        with pytest.raises(ValueError, match="Unsupported database engine"):
            SqlOperations("mysql", "test.db")

    @patch("aoi_data_manager.sql_operations.create_engine")
    def test_engine_creation_error(self, mock_create_engine):
        """エンジン作成エラーのテスト"""
        mock_create_engine.side_effect = Exception("Database connection failed")

        with pytest.raises(Exception, match="Database connection failed"):
            SqlOperations("sqlite", "invalid_path")


class TestSqlOperationsBasicFunctionality:
    """基本機能のテスト"""

    def test_sqlite_basic_operations(self):
        """SQLiteでの基本操作をテスト"""
        # テスト用のディレクトリを作成
        test_dir = Path("test_basic")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_basic")
        sql_ops.create_tables()

        # エンジンが正常に作成されていることを確認
        assert sql_ops.engine is not None
        assert "sqlite" in str(sql_ops.engine.url)

        # クリーンアップ
        try:
            Path("test_basic/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    @patch("aoi_data_manager.sql_operations.create_engine")
    def test_postgres_basic_operations(self, mock_create_engine):
        """PostgreSQLでの基本操作をテスト（モック使用）"""
        mock_engine = Mock()
        mock_create_engine.return_value = mock_engine

        sql_ops = SqlOperations("postgresql", "user:pass@localhost:5432/testdb")

        # エンジンが正常に作成されていることを確認
        assert sql_ops.engine == mock_engine
        mock_create_engine.assert_called_once_with(
            "postgresql://user:pass@localhost:5432/testdb"
        )


class TestSqlOperationsDataInsertion:
    """データ挿入操作のテスト"""

    def test_insert_defect_info_success(self):
        """DefectInfo挿入の成功テスト"""
        # 一意なテスト名を生成
        test_name = get_unique_test_name("test_insert_defect")
        test_dir = Path(test_name)
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", test_name)
        sql_ops.create_tables()

        # テストデータ作成
        defect_info = DefectInfo(
            id=f"{test_name}-defect-001",
            lot_number="LOT123",
            current_board_index=1,
            defect_number=1,
            line_name="LINE01",
            model_code="MODEL01",
            serial="SN123",
            reference="REF01",
            defect_name="欠品",
            x=100,
            y=200,
            aoi_user="test_user",
        )

        # データ挿入
        sql_ops.insert_defect_info(defect_info)

        # データが挿入されたことを確認
        with Session(sql_ops.engine) as session:
            inserted_defect = session.get(DefectInfo, f"{test_name}-defect-001")
            assert inserted_defect is not None
            assert inserted_defect.lot_number == "LOT123"
            assert inserted_defect.defect_number == 1

        # クリーンアップ
        try:
            Path(f"{test_name}/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_insert_repaird_info_success(self):
        """RepairdInfo挿入の成功テスト"""
        # 一意なテスト名を生成
        test_name = get_unique_test_name("test_insert_repair")
        test_dir = Path(test_name)
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", test_name)
        sql_ops.create_tables()

        # テストデータ作成
        repaird_info = RepairdInfo(
            id=f"{test_name}-repair-001", is_repaird=True, parts_type="抵抗"
        )

        # データ挿入
        sql_ops.insert_repaird_info(repaird_info)

        # データが挿入されたことを確認
        with Session(sql_ops.engine) as session:
            inserted_repair = session.get(RepairdInfo, f"{test_name}-repair-001")
            assert inserted_repair is not None
            assert inserted_repair.is_repaird is True
            assert inserted_repair.parts_type == "抵抗"

        # クリーンアップ
        try:
            Path(f"{test_name}/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    @patch("aoi_data_manager.sql_operations.Session")
    def test_insert_defect_info_session_error(self, mock_session):
        """DefectInfo挿入時のセッションエラーテスト"""
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.add.side_effect = Exception("Database error")

        sql_ops = SqlOperations("sqlite", "test_db")
        defect_info = DefectInfo(id="test-001")

        with pytest.raises(Exception, match="Database error"):
            sql_ops.insert_defect_info(defect_info)

    @patch("aoi_data_manager.sql_operations.Session")
    def test_insert_repaird_info_session_error(self, mock_session):
        """RepairdInfo挿入時のセッションエラーテスト"""
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.add.side_effect = Exception("Database error")

        sql_ops = SqlOperations("sqlite", "test_db")
        repaird_info = RepairdInfo(id="test-001")

        with pytest.raises(Exception, match="Database error"):
            sql_ops.insert_repaird_info(repaird_info)


class TestSqlOperationsQueryMethods:
    """データ検索メソッドのテスト"""

    def test_get_defect_info_by_id_exists(self):
        """存在するIDでDefectInfoを取得するテスト"""
        test_dir = Path("test_get_defect_by_id")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_get_defect_by_id")
        sql_ops.create_tables()

        # テストデータ挿入
        defect_info = DefectInfo(
            id="query-test-001", lot_number="QUERY_LOT", defect_name="テスト不良"
        )
        sql_ops.insert_defect_info(defect_info)

        # ID検索テスト
        result = sql_ops.get_defect_info_by_id("query-test-001")
        assert result is not None
        assert result.lot_number == "QUERY_LOT"
        assert result.defect_name == "テスト不良"

        # クリーンアップ
        try:
            Path("test_get_defect_by_id/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_get_defect_info_by_id_not_exists(self):
        """存在しないIDでDefectInfoを取得するテスト"""
        test_dir = Path("test_get_defect_not_exist")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_get_defect_not_exist")
        sql_ops.create_tables()

        # 存在しないID検索テスト
        result = sql_ops.get_defect_info_by_id("non-existent-id")
        assert result is None

        # クリーンアップ
        try:
            Path("test_get_defect_not_exist/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_get_all_defect_info(self):
        """全DefectInfo取得テスト"""
        test_dir = Path("test_get_all_defects")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_get_all_defects")
        sql_ops.create_tables()

        # 複数データ挿入
        defects = [
            DefectInfo(id=f"all-test-{i:03d}", lot_number=f"LOT{i}")
            for i in range(1, 4)
        ]
        for defect in defects:
            sql_ops.insert_defect_info(defect)

        # 全件取得テスト
        results = sql_ops.get_all_defect_info()
        assert len(results) == 3
        lot_numbers = [r.lot_number for r in results]
        assert "LOT1" in lot_numbers
        assert "LOT2" in lot_numbers
        assert "LOT3" in lot_numbers

        # クリーンアップ
        try:
            Path("test_get_all_defects/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_get_defect_info_by_lot(self):
        """指図番号でDefectInfo検索テスト"""
        test_dir = Path("test_get_by_lot")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_get_by_lot")
        sql_ops.create_tables()

        # 同じ指図番号のデータを複数挿入
        defects = [
            DefectInfo(id="lot-test-001", lot_number="SEARCH_LOT", defect_number=1),
            DefectInfo(id="lot-test-002", lot_number="SEARCH_LOT", defect_number=2),
            DefectInfo(id="lot-test-003", lot_number="OTHER_LOT", defect_number=1),
        ]
        for defect in defects:
            sql_ops.insert_defect_info(defect)

        # 指図番号検索テスト
        results = sql_ops.get_defect_info_by_lot("SEARCH_LOT")
        assert len(results) == 2
        for result in results:
            assert result.lot_number == "SEARCH_LOT"

        # クリーンアップ
        try:
            Path("test_get_by_lot/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


class TestSqlOperationsBatchMethods:
    """バッチ処理メソッドのテスト"""

    def test_insert_defect_info_batch(self):
        """DefectInfo一括挿入テスト"""
        test_dir = Path("test_batch_defect")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_batch_defect")
        sql_ops.create_tables()

        # バッチデータ作成
        batch_defects = [
            DefectInfo(
                id=f"batch-defect-{i:03d}", lot_number=f"BATCH_LOT_{i}", defect_number=i
            )
            for i in range(1, 6)
        ]

        # バッチ挿入
        sql_ops.insert_defect_info_batch(batch_defects)

        # 挿入確認
        all_defects = sql_ops.get_all_defect_info()
        assert len(all_defects) == 5

        # 特定データ確認
        defect_003 = sql_ops.get_defect_info_by_id("batch-defect-003")
        assert defect_003 is not None
        assert defect_003.lot_number == "BATCH_LOT_3"

        # クリーンアップ
        try:
            Path("test_batch_defect/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_insert_repaird_info_batch(self):
        """RepairdInfo一括挿入テスト"""
        test_dir = Path("test_batch_repair")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_batch_repair")
        sql_ops.create_tables()

        # バッチデータ作成
        batch_repairs = [
            RepairdInfo(
                id=f"batch-repair-{i:03d}",
                is_repaird=(i % 2 == 0),
                parts_type=f"部品{i}",
            )
            for i in range(1, 4)
        ]

        # バッチ挿入
        sql_ops.insert_repaird_info_batch(batch_repairs)

        # 挿入確認
        all_repairs = sql_ops.get_all_repaird_info()
        assert len(all_repairs) == 3

        # 特定データ確認
        repair_002 = sql_ops.get_repaird_info_by_id("batch-repair-002")
        assert repair_002 is not None
        assert repair_002.is_repaird is True
        assert repair_002.parts_type == "部品2"

        # クリーンアップ
        try:
            Path("test_batch_repair/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


class TestSqlOperationsDeleteMethods:
    """削除メソッドのテスト"""

    def test_delete_defect_info_exists(self):
        """存在するDefectInfo削除テスト"""
        test_dir = Path("test_delete_defect")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_delete_defect")
        sql_ops.create_tables()

        # データ挿入
        defect_info = DefectInfo(id="delete-test-001", lot_number="DELETE_LOT")
        sql_ops.insert_defect_info(defect_info)

        # 削除実行
        result = sql_ops.delete_defect_info("delete-test-001")
        assert result is True

        # 削除確認
        deleted_defect = sql_ops.get_defect_info_by_id("delete-test-001")
        assert deleted_defect is None

        # クリーンアップ
        try:
            Path("test_delete_defect/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_delete_defect_info_not_exists(self):
        """存在しないDefectInfo削除テスト"""
        test_dir = Path("test_delete_defect_not_exist")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_delete_defect_not_exist")
        sql_ops.create_tables()

        # 存在しないデータの削除
        result = sql_ops.delete_defect_info("non-existent-id")
        assert result is False

        # クリーンアップ
        try:
            Path("test_delete_defect_not_exist/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_delete_repaird_info_exists(self):
        """存在するRepairdInfo削除テスト"""
        test_dir = Path("test_delete_repair")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_delete_repair")
        sql_ops.create_tables()

        # データ挿入
        repaird_info = RepairdInfo(id="delete-repair-001", parts_type="削除テスト部品")
        sql_ops.insert_repaird_info(repaird_info)

        # 削除実行
        result = sql_ops.delete_repaird_info("delete-repair-001")
        assert result is True

        # 削除確認
        deleted_repair = sql_ops.get_repaird_info_by_id("delete-repair-001")
        assert deleted_repair is None

        # クリーンアップ
        try:
            Path("test_delete_repair/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


class TestSqlOperationsCRUD:
    """CRUD操作の包括的テスト"""

    def test_full_defect_lifecycle(self):
        """DefectInfoの完全なライフサイクルテスト"""
        # テスト用のディレクトリを作成
        test_dir = Path("test_defect_lifecycle")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_defect_lifecycle")
        sql_ops.create_tables()

        # 1. データ作成と挿入
        defect_info = DefectInfo(
            id="lifecycle-test-001",
            lot_number="LOT456",
            current_board_index=2,
            defect_number=5,
            line_name="LINE02",
            model_code="MODEL02",
            serial="SN456",
            reference="REF02",
            defect_name="ブリッジ",
            x=150,
            y=250,
            aoi_user="test_user2",
        )
        sql_ops.insert_defect_info(defect_info)

        # 2. データ読み取り確認
        with Session(sql_ops.engine) as session:
            retrieved_defect = session.get(DefectInfo, "lifecycle-test-001")
            assert retrieved_defect is not None
            assert retrieved_defect.lot_number == "LOT456"
            assert retrieved_defect.defect_name == "ブリッジ"

        # クリーンアップ
        try:
            Path("test_defect_lifecycle/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_multiple_records_insertion(self):
        """複数レコード挿入テスト"""
        # テスト用のディレクトリを作成
        test_dir = Path("test_multiple_records")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_multiple_records")
        sql_ops.create_tables()

        # 複数のDefectInfoを挿入
        defects = [
            DefectInfo(
                id=f"multi-test-{i:03d}",
                lot_number=f"LOT{i:03d}",
                current_board_index=i,
                defect_number=i,
                line_name=f"LINE{i:02d}",
            )
            for i in range(1, 6)
        ]

        for defect in defects:
            sql_ops.insert_defect_info(defect)

        # 挿入されたレコード数を確認
        with Session(sql_ops.engine) as session:
            from sqlmodel import select

            statement = select(DefectInfo)
            results = session.exec(statement).all()
            assert len(results) == 5

            # 特定のレコードの内容確認
            test_defect = session.get(DefectInfo, "multi-test-003")
            assert test_defect.lot_number == "LOT003"
            assert test_defect.current_board_index == 3

        # クリーンアップ
        try:
            Path("test_multiple_records/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


class TestSqlOperationsPerformance:
    """パフォーマンステスト"""

    def test_large_batch_insertion(self):
        """大量データ一括挿入のパフォーマンステスト"""
        test_dir = Path("test_performance")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_performance")
        sql_ops.create_tables()

        # 100件のテストデータ作成
        large_batch = [
            DefectInfo(
                id=f"perf-test-{i:04d}",
                lot_number=f"PERF_LOT_{i // 10}",
                current_board_index=i % 10,
                defect_number=i,
                line_name=f"LINE{i % 5:02d}",
                model_code=f"MODEL{i % 3:02d}",
            )
            for i in range(100)
        ]

        # バッチ挿入実行
        import time

        start_time = time.time()
        sql_ops.insert_defect_info_batch(large_batch)
        end_time = time.time()

        # パフォーマンス確認（100件の挿入が5秒以内に完了することを確認）
        assert (end_time - start_time) < 5.0

        # データ確認
        all_defects = sql_ops.get_all_defect_info()
        assert len(all_defects) == 100

        # クリーンアップ
        try:
            Path("test_performance/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass

    def test_query_performance(self):
        """検索パフォーマンステスト"""
        test_dir = Path("test_query_performance")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_query_performance")
        sql_ops.create_tables()

        # 50件のテストデータ挿入
        test_data = [
            DefectInfo(
                id=f"query-perf-{i:03d}",
                lot_number=f"QUERY_LOT_{i % 5}",
                defect_number=i,
            )
            for i in range(50)
        ]
        sql_ops.insert_defect_info_batch(test_data)

        # 検索パフォーマンステスト
        import time

        start_time = time.time()

        # 複数の検索操作を実行
        for i in range(10):
            sql_ops.get_defect_info_by_lot(f"QUERY_LOT_{i % 5}")
            sql_ops.get_defect_info_by_id(f"query-perf-{i:03d}")

        end_time = time.time()

        # パフォーマンス確認（検索操作が1秒以内に完了することを確認）
        assert (end_time - start_time) < 1.0

        # クリーンアップ
        try:
            Path("test_query_performance/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


class TestSqlOperationsErrorScenarios:
    """エラーシナリオテスト"""

    @patch("aoi_data_manager.sql_operations.Session")
    def test_get_defect_info_by_id_session_error(self, mock_session):
        """get_defect_info_by_id実行時のセッションエラーテスト"""
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.get.side_effect = Exception("Database connection error")

        sql_ops = SqlOperations("sqlite", "test_db")

        with pytest.raises(Exception, match="Database connection error"):
            sql_ops.get_defect_info_by_id("test-id")

    @patch("aoi_data_manager.sql_operations.Session")
    def test_get_all_defect_info_session_error(self, mock_session):
        """get_all_defect_info実行時のセッションエラーテスト"""
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.exec.side_effect = Exception("Query execution error")

        sql_ops = SqlOperations("sqlite", "test_db")

        with pytest.raises(Exception, match="Query execution error"):
            sql_ops.get_all_defect_info()

    @patch("aoi_data_manager.sql_operations.Session")
    def test_delete_defect_info_session_error(self, mock_session):
        """delete_defect_info実行時のセッションエラーテスト"""
        mock_session_instance = Mock()
        mock_session.return_value.__enter__.return_value = mock_session_instance
        mock_session_instance.get.side_effect = Exception("Delete operation error")

        sql_ops = SqlOperations("sqlite", "test_db")

        with pytest.raises(Exception, match="Delete operation error"):
            sql_ops.delete_defect_info("test-id")

    def test_batch_insertion_with_duplicate_ids(self):
        """重複IDでの一括挿入エラーテスト"""
        test_dir = Path("test_duplicate_ids")
        test_dir.mkdir(exist_ok=True)

        sql_ops = SqlOperations("sqlite", "test_duplicate_ids")
        sql_ops.create_tables()

        # 最初のデータ挿入
        first_defect = DefectInfo(id="duplicate-test-001", lot_number="FIRST_LOT")
        sql_ops.insert_defect_info(first_defect)

        # 同じIDでの一括挿入（エラーが発生することを確認）
        duplicate_batch = [
            DefectInfo(id="duplicate-test-001", lot_number="DUPLICATE_LOT")
        ]

        with pytest.raises(Exception):  # IntegrityError や類似のエラーが発生
            sql_ops.insert_defect_info_batch(duplicate_batch)

        # クリーンアップ
        try:
            Path("test_duplicate_ids/aoi_data.db").unlink(missing_ok=True)
            test_dir.rmdir()
        except (PermissionError, FileNotFoundError):
            pass


@pytest.mark.skipif(True, reason="実際のPostgreSQL環境が必要")
class TestSqlOperationsIntegration:
    """統合テスト（実際のデータベース環境が必要）"""

    def test_postgres_real_connection(self):
        """実際のPostgreSQL接続テスト"""
        # 実際のPostgreSQL環境でのテスト
        pass

    def test_sqlite_file_operations(self):
        """SQLiteファイル操作の統合テスト"""
        # 実際のファイルシステムでのテスト
        pass

"""
SqlOperations自動切断機能の使用例

このファイルはSqlOperationsクラスの新しい自動切断機能の使用方法を示します。
"""

from aoi_data_manager.sql_operations import SqlOperations
from aoi_data_manager.db_models import DefectInfo, RepairdInfo
import uuid


def example_context_manager_usage():
    """推奨: with文を使用した自動切断"""

    # with文を使用することで、ブロックを抜ける時に自動的にデータベース接続が切断されます
    with SqlOperations(db_url="./database") as sql_ops:
        # テーブル作成
        sql_ops.create_tables()

        # データ挿入
        defect_data = DefectInfo(
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
            aoi_user="operator_1",
            model_label="model_A",
            board_label="board_1",
            kintone_record_id="record_001",
        )
        sql_ops.insert_defect_info(defect_data)

        # データ取得
        result = sql_ops.get_defect_info_by_id(defect_data.id)
        print(f"取得したデータ: {result.line_name}")

    # ここで自動的にsql_ops.close()が呼ばれます
    print("データベース接続が自動的に切断されました")


def example_manual_close():
    """手動でclose()を呼ぶ方法"""

    sql_ops = SqlOperations(db_url="./database")

    try:
        sql_ops.create_tables()

        # データ操作...
        defect_data = DefectInfo(
            id=str(uuid.uuid4()), line_name="LINE_02", defect_name="bubble"
        )
        sql_ops.insert_defect_info(defect_data)

    except Exception as e:
        print(f"エラーが発生しました: {e}")

    finally:
        # 必ずclose()を呼んでリソースを解放
        sql_ops.close()
        print("データベース接続を手動で切断しました")


def example_batch_processing():
    """バッチ処理と自動切断の組み合わせ"""

    with SqlOperations(db_url="./database") as sql_ops:
        sql_ops.create_tables()

        # 大量データのバッチ処理
        defect_list = []
        for i in range(100):
            defect_data = DefectInfo(
                id=str(uuid.uuid4()),
                line_name=f"LINE_{i//10 + 1:02d}",
                model_code="Y001",
                lot_number=f"LOT_{i:03d}",
                current_board_index=i % 10,
                defect_number=i,
                serial=f"QR_{i:06d}",
                reference=f"R_{i:06d}",
                defect_name="scratch",
                x=i % 1000,
                y=i % 500,
                aoi_user="batch_operator",
                model_label="batch_model",
                board_label=f"board_{i}",
                kintone_record_id=f"batch_record_{i:06d}",
            )
            defect_list.append(defect_data)

        # バッチ挿入
        sql_ops.insert_defect_info_batch(defect_list)

        # 結果確認
        all_data = sql_ops.get_all_defect_info()
        print(f"バッチ処理完了: {len(all_data)}件のデータを挿入しました")

    # with文を抜ける時に自動的に接続が切断されます


def example_error_handling():
    """エラーハンドリングと自動切断"""

    try:
        with SqlOperations(db_url="./database") as sql_ops:
            sql_ops.create_tables()

            # 何らかの処理でエラーが発生
            raise RuntimeError("処理中にエラーが発生しました")

    except RuntimeError as e:
        print(f"エラーをキャッチしました: {e}")
        # エラーが発生してもwith文を抜ける時に自動的に切断されます

    print("エラーが発生してもデータベース接続は適切に切断されました")


def example_migration_from_old_code():
    """既存コードからの移行例"""

    # 【古いコード】
    # sql_ops = SqlOperations(db_url="./database")
    # sql_ops.create_tables()
    # # ... 処理 ...
    # sql_ops.close()  # 手動でclose()を呼ぶ必要があった

    # 【新しいコード（推奨）】
    with SqlOperations(db_url="./database") as sql_ops:
        sql_ops.create_tables()
        # ... 同じ処理 ...
    # close()は自動的に呼ばれる


def example_connection_check():
    """接続状態のチェック"""

    sql_ops = SqlOperations(db_url="./database")
    sql_ops.create_tables()

    # 手動でclose()
    sql_ops.close()

    # close()後の操作はエラーになります
    try:
        sql_ops.create_tables()
    except RuntimeError as e:
        print(f"期待通りのエラー: {e}")
        print("close()後の操作は適切にブロックされました")


if __name__ == "__main__":
    print("=== SqlOperations自動切断機能の使用例 ===\n")

    print("1. Context manager使用例（推奨）")
    example_context_manager_usage()
    print()

    print("2. 手動close使用例")
    example_manual_close()
    print()

    print("3. バッチ処理例")
    example_batch_processing()
    print()

    print("4. エラーハンドリング例")
    example_error_handling()
    print()

    print("5. 接続状態チェック例")
    example_connection_check()
    print()

    print("=== 全ての例が完了しました ===")

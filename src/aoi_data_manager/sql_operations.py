from sqlmodel import SQLModel, create_engine, Session, select
from typing import List, Optional
import weakref
from .schema import DefectInfo, RepairdInfo
from .db_models import (
    DefectInfoTable,
    RepairdInfoTable,
)  # テーブル定義用


class SqlOperations:
    """
    複数のSQLデータベースエンジンに対応したSQL操作クラス
    コンストラクタで使用するデータベースエンジンを指定してください。

    ### 対応データベースエンジン
    - SQLite3

    Args:
        db_url (str): データベース接続URL

    ### 使用方法
    # with文を使用することで自動的にデータベース接続が切断されます
    with SqlOperations(db_url="path/to/db") as sql_ops:
        sql_ops.create_tables()
        sql_ops.insert_defect_info(data)
    # ここで自動的にclose()が呼ばれます

    # 手動でcloseする場合
    sql_ops = SqlOperations(db_url="path/to/db")
    try:
        sql_ops.create_tables()
    finally:
        sql_ops.close()
    """

    def __init__(self, db_url: str, db_name: str = "aoi_data.db"):
        """
        コンストラクタ
        Args:
            db_url (str): データベース接続URL
            db_name (str): データベース名
        """
        self.db_name = db_name
        self.db_url = db_url
        self.engine = self._create_engine()
        self._closed = False

        # ガベージコレクション時の自動クリーンアップを設定
        self._finalizer = weakref.finalize(self, self._cleanup_engine, self.engine)

    def __enter__(self):
        """Context managerのenter"""
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context managerのexit - 自動的にデータベース接続を切断"""
        self.close()

    def _create_engine(self):
        """指定されたデータベースエンジンに基づいてSQLAlchemyエンジンを作成"""
        return create_engine(f"sqlite:///{self.db_url}/{self.db_name}")

    @staticmethod
    def _cleanup_engine(engine):
        """エンジンのクリーンアップ（ガベージコレクション時用）"""
        try:
            if engine:
                engine.dispose()
        except Exception:
            # ガベージコレクション時のエラーは無視
            pass

    def close(self):
        """データベース接続を明示的に切断"""
        if not self._closed and self.engine:
            try:
                self.engine.dispose()
            finally:
                self._closed = True
                # finalizerを無効化（既にクリーンアップ済み）
                if hasattr(self, "_finalizer"):
                    self._finalizer.detach()

    def _check_connection(self):
        """接続状態をチェック"""
        if self._closed:
            raise RuntimeError(
                "SqlOperations instance has been closed. Create a new instance or use within a 'with' statement."
            )

    def _schema_to_db_model(self, schema_obj):
        """スキーマオブジェクトをデータベースモデルに変換"""
        if isinstance(schema_obj, DefectInfo):
            return DefectInfoTable(
                id=schema_obj.id,
                line_name=schema_obj.line_name,
                model_code=schema_obj.model_code,
                lot_number=schema_obj.lot_number,
                current_board_index=schema_obj.current_board_index,
                defect_number=schema_obj.defect_number,
                serial=schema_obj.serial,
                reference=schema_obj.reference,
                defect_name=schema_obj.defect_name,
                x=schema_obj.x,
                y=schema_obj.y,
                aoi_user=schema_obj.aoi_user,
                insert_datetime=schema_obj.insert_datetime,
                model_label=schema_obj.model_label,
                board_label=schema_obj.board_label,
                kintone_record_id=schema_obj.kintone_record_id,
            )
        elif isinstance(schema_obj, RepairdInfo):
            return RepairdInfoTable(
                id=schema_obj.id,
                is_repaird=schema_obj.is_repaird,
                parts_type=schema_obj.parts_type,
                insert_datetime=schema_obj.insert_datetime,
                kintone_record_id=schema_obj.kintone_record_id,
            )
        else:
            raise ValueError(f"Unsupported schema type: {type(schema_obj)}")

    def _db_model_to_schema(self, db_obj):
        """データベースモデルをスキーマオブジェクトに変換"""
        if isinstance(db_obj, DefectInfoTable):
            return DefectInfo(
                id=db_obj.id,
                line_name=db_obj.line_name,
                model_code=db_obj.model_code,
                lot_number=db_obj.lot_number,
                current_board_index=db_obj.current_board_index,
                defect_number=db_obj.defect_number,
                serial=db_obj.serial,
                reference=db_obj.reference,
                defect_name=db_obj.defect_name,
                x=db_obj.x,
                y=db_obj.y,
                aoi_user=db_obj.aoi_user,
                insert_datetime=db_obj.insert_datetime,
                model_label=db_obj.model_label,
                board_label=db_obj.board_label,
                kintone_record_id=db_obj.kintone_record_id,
            )
        elif isinstance(db_obj, RepairdInfoTable):
            return RepairdInfo(
                id=db_obj.id,
                is_repaird=db_obj.is_repaird,
                parts_type=db_obj.parts_type,
                insert_datetime=db_obj.insert_datetime,
                kintone_record_id=db_obj.kintone_record_id,
            )
        else:
            raise ValueError(f"Unsupported database model type: {type(db_obj)}")

    def create_tables(self):
        """データベース内にDefectInfoおよびRepairdInfoのテーブルを作成"""
        self._check_connection()
        SQLModel.metadata.create_all(self.engine)

    def insert_defect_info(self, defect_info: DefectInfo):
        """DefectInfoデータをデータベースに挿入"""
        self._check_connection()
        # スキーマをデータベースモデルに変換
        db_model = self._schema_to_db_model(defect_info)
        with Session(self.engine) as session:
            try:
                session.add(db_model)
                session.commit()
            except Exception as e:
                session.rollback()
                raise

    def insert_defect_infos(self, defect_infos: List[DefectInfo]):
        """DefectInfoデータを一括挿入"""
        self._check_connection()
        # スキーマをデータベースモデルに変換
        db_models = [self._schema_to_db_model(info) for info in defect_infos]
        with Session(self.engine) as session:
            try:
                session.add_all(db_models)
                session.commit()
            except Exception as e:
                session.rollback()
                raise

    def merge_insert_defect_info(self, defect_info: DefectInfo):
        """DefectInfoデータをマージ挿入（存在すれば更新、なければ挿入）"""
        self._check_connection()
        # スキーマをデータベースモデルに変換
        db_model = self._schema_to_db_model(defect_info)
        with Session(self.engine) as session:
            try:
                session.merge(db_model)
                session.commit()
            except Exception as e:
                session.rollback()
                raise

    def merge_insert_defect_infos(self, defect_infos: List[DefectInfo]):
        """DefectInfoデータを一括マージ挿入（存在すれば更新、なければ挿入）"""
        self._check_connection()
        # スキーマをデータベースモデルに変換
        db_models = [self._schema_to_db_model(info) for info in defect_infos]
        with Session(self.engine) as session:
            try:
                for db_model in db_models:
                    session.merge(db_model)
                session.commit()
            except Exception as e:
                session.rollback()
                raise

    def insert_repaird_info(self, repaird_info: RepairdInfo):
        """RepairdInfoデータをデータベースに挿入"""
        self._check_connection()
        # スキーマをデータベースモデルに変換
        db_model = self._schema_to_db_model(repaird_info)
        with Session(self.engine) as session:
            session.add(db_model)
            session.commit()

    def get_defect_info_by_id(self, defect_id: str) -> Optional[DefectInfo]:
        """IDでDefectInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            db_obj = session.get(DefectInfoTable, defect_id)
            return self._db_model_to_schema(db_obj) if db_obj else None

    def get_all_defect_info(self) -> List[DefectInfo]:
        """全てのDefectInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            statement = select(DefectInfoTable)
            db_objects = session.exec(statement).all()
            return [self._db_model_to_schema(db_obj) for db_obj in db_objects]

    def get_defect_info_by_lot(self, lot_number: str) -> List[DefectInfo]:
        """指図番号でDefectInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            statement = select(DefectInfoTable).where(
                DefectInfoTable.lot_number == lot_number
            )
            db_objects = session.exec(statement).all()
            return [self._db_model_to_schema(db_obj) for db_obj in db_objects]

    def get_repaird_info_by_id(self, repair_id: str) -> Optional[RepairdInfo]:
        """IDでRepairdInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            db_obj = session.get(RepairdInfoTable, repair_id)
            return self._db_model_to_schema(db_obj) if db_obj else None

    def get_all_repaird_info(self) -> List[RepairdInfo]:
        """全てのRepairdInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            statement = select(RepairdInfoTable)
            db_objects = session.exec(statement).all()
            return [self._db_model_to_schema(db_obj) for db_obj in db_objects]

    def insert_defect_info_batch(self, defect_infos: List[DefectInfo]):
        """DefectInfoデータを一括挿入"""
        self._check_connection()
        with Session(self.engine) as session:
            for defect_info in defect_infos:
                db_model = self._schema_to_db_model(defect_info)
                session.add(db_model)
            session.commit()

    def insert_repaird_info_batch(self, repaird_infos: List[RepairdInfo]):
        """RepairdInfoデータを一括挿入"""
        self._check_connection()
        with Session(self.engine) as session:
            for repaird_info in repaird_infos:
                db_model = self._schema_to_db_model(repaird_info)
                session.add(db_model)
            session.commit()

    def merge_repaird_info_batch(self, repaird_infos: List[RepairdInfo]):
        """RepairdInfoデータを一括マージ挿入（存在すれば更新、なければ挿入）"""
        self._check_connection()
        with Session(self.engine) as session:
            for repaird_info in repaird_infos:
                db_model = self._schema_to_db_model(repaird_info)
                session.merge(db_model)
            session.commit()

    def delete_defect_info(self, defect_id: str) -> bool:
        """
        DefectInfoを削除

        Args:
            defect_id (str): 削除するDefectInfoのID
        Returns:
            bool: 削除が成功したかどうか
        Examples:
            sql_ops = SqlOperations(db_url="path/to/db")
            result = sql_ops.delete_defect_info("defect_id_12345")
        """
        self._check_connection()
        with Session(self.engine) as session:
            defect_info = session.get(DefectInfoTable, defect_id)
            if defect_info:
                session.delete(defect_info)
                session.commit()
                return True
            return False

    def delete_defect_infos(self, defect_ids: List[str]) -> int:
        """
        複数のDefectInfoを削除

        Args:
            defect_ids (List[str]): 削除するDefectInfoのIDリスト
        Returns:
            int: 削除したDefectInfoの数
        Examples:
            sql_ops = SqlOperations(db_url="path/to/db")
            deleted_count = sql_ops.delete_defect_infos(["defect_id_12345", "defect_id_67890"])
        """
        self._check_connection()
        deleted_count = 0
        with Session(self.engine) as session:
            for defect_id in defect_ids:
                defect_info = session.get(DefectInfoTable, defect_id)
                if defect_info:
                    session.delete(defect_info)
                    deleted_count += 1
            session.commit()
        return deleted_count

    def delete_repaird_info(self, repair_id: str) -> bool:
        """RepairdInfoを削除"""
        self._check_connection()
        with Session(self.engine) as session:
            repaird_info = session.get(RepairdInfoTable, repair_id)
            if repaird_info:
                session.delete(repaird_info)
                session.commit()
                return True
            return False

    def delete_repaird_infos(self, repair_ids: List[str]) -> int:
        """複数のRepairdInfoを削除"""
        self._check_connection()
        deleted_count = 0
        with Session(self.engine) as session:
            for repair_id in repair_ids:
                repaird_info = session.get(RepairdInfoTable, repair_id)
                if repaird_info:
                    session.delete(repaird_info)
                    deleted_count += 1
            session.commit()
        return deleted_count

    @staticmethod
    def merge_target_database(
        source_db_url: str,
        target_db_url: str,
        db_name: str,
        delete_defect_ids: List[str] = None,
        delete_repaird_ids: List[str] = None,
    ) -> None:
        """
        2つのデータベースをマージ（sourceからtargetへ）
        新規データは挿入、既存データは更新されます。

        Args:
            source_db_url (str): ソースデータベースURL
            target_db_url (str): ターゲットデータベースURL
            db_name (str): データベース名
            delete_defect_ids (List[str], optional): ターゲットデータベースから削除するDefectInfoのIDリスト. Defaults to None.
            delete_repaird_ids (List[str], optional): ターゲットデータベースから削除するRepairdInfoのIDリスト. Defaults to None.
        """
        source_ops = SqlOperations(db_url=source_db_url, db_name=db_name)
        target_ops = SqlOperations(db_url=target_db_url, db_name=db_name)

        try:
            source_ops.create_tables()
            target_ops.create_tables()

            # DefectInfoのマージ
            source_defects = source_ops.get_all_defect_info()
            target_ops.merge_insert_defect_infos(source_defects)

            # DefectInfoの削除
            if delete_defect_ids:
                for defect_id in delete_defect_ids:
                    target_ops.delete_defect_info(defect_id)

            # RepairdInfoのマージ
            source_repairds = source_ops.get_all_repaird_info()
            target_ops.merge_repaird_info_batch(source_repairds)

            # RepairdInfoの削除
            if delete_repaird_ids:
                for repaird_id in delete_repaird_ids:
                    target_ops.delete_repaird_info(repaird_id)

        finally:
            source_ops.close()
            target_ops.close()

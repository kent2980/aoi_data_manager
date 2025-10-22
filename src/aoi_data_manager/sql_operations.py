from sqlmodel import SQLModel, create_engine, Session, select
from typing import List, Optional
import weakref
from .db_models import DefectInfo, RepairdInfo


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

    def __init__(self, db_url: str):
        """
        コンストラクタ
        Args:
            db_url (str): データベース接続URL
        """
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
        return create_engine(f"sqlite:///{self.db_url}/aoi_data.db")

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

    def create_tables(self):
        """データベース内にDefectInfoおよびRepairdInfoのテーブルを作成"""
        self._check_connection()
        SQLModel.metadata.create_all(self.engine)

    def insert_defect_info(self, defect_info: DefectInfo):
        """DefectInfoデータをデータベースに挿入"""
        print("DEBUG: Inserting defect_info")
        self._check_connection()
        with Session(self.engine) as session:
            try:
                session.add(defect_info)
                session.commit()
            except Exception as e:
                print(f"DEBUG: Error type: {type(e).__name__}")
                print(f"DEBUG: Error message: {str(e)}")
                session.rollback()
                raise

    def insert_repaird_info(self, repaird_info: RepairdInfo):
        """RepairdInfoデータをデータベースに挿入"""
        self._check_connection()
        with Session(self.engine) as session:
            session.add(repaird_info)
            session.commit()

    def get_defect_info_by_id(self, defect_id: str) -> Optional[DefectInfo]:
        """IDでDefectInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            return session.get(DefectInfo, defect_id)

    def get_all_defect_info(self) -> List[DefectInfo]:
        """全てのDefectInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            statement = select(DefectInfo)
            return list(session.exec(statement).all())

    def get_defect_info_by_lot(self, lot_number: str) -> List[DefectInfo]:
        """指図番号でDefectInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            statement = select(DefectInfo).where(DefectInfo.lot_number == lot_number)
            return list(session.exec(statement).all())

    def get_repaird_info_by_id(self, repair_id: str) -> Optional[RepairdInfo]:
        """IDでRepairdInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            return session.get(RepairdInfo, repair_id)

    def get_all_repaird_info(self) -> List[RepairdInfo]:
        """全てのRepairdInfoを取得"""
        self._check_connection()
        with Session(self.engine) as session:
            statement = select(RepairdInfo)
            return list(session.exec(statement).all())

    def insert_defect_info_batch(self, defect_infos: List[DefectInfo]):
        """DefectInfoデータを一括挿入"""
        self._check_connection()
        with Session(self.engine) as session:
            for defect_info in defect_infos:
                session.add(defect_info)
            session.commit()

    def insert_repaird_info_batch(self, repaird_infos: List[RepairdInfo]):
        """RepairdInfoデータを一括挿入"""
        self._check_connection()
        with Session(self.engine) as session:
            for repaird_info in repaird_infos:
                session.add(repaird_info)
            session.commit()

    def delete_defect_info(self, defect_id: str) -> bool:
        """DefectInfoを削除"""
        self._check_connection()
        with Session(self.engine) as session:
            defect_info = session.get(DefectInfo, defect_id)
            if defect_info:
                session.delete(defect_info)
                session.commit()
                return True
            return False

    def delete_repaird_info(self, repair_id: str) -> bool:
        """RepairdInfoを削除"""
        self._check_connection()
        with Session(self.engine) as session:
            repaird_info = session.get(RepairdInfo, repair_id)
            if repaird_info:
                session.delete(repaird_info)
                session.commit()
                return True
            return False

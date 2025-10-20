from sqlmodel import SQLModel, create_engine, Session, select
from typing import List, Optional
from .db_models import DefectInfo, RepairdInfo


class SqlOperations:
    """
    複数のSQLデータベースエンジンに対応したSQL操作クラス
    コンストラクタで使用するデータベースエンジンを指定してください。

    ### 対応データベースエンジン
    - SQLite3

    Args:
        db_url (str): データベース接続URL
    """

    def __init__(self, db_url: str):
        """
        コンストラクタ
        Args:
            db_url (str): データベース接続URL
        """
        self.db_url = db_url
        self.engine = self._create_engine()

    def _create_engine(self):
        """指定されたデータベースエンジンに基づいてSQLAlchemyエンジンを作成"""
        return create_engine(f"sqlite:///{self.db_url}/aoi_data.db")

    def create_tables(self):
        """データベース内にDefectInfoおよびRepairdInfoのテーブルを作成"""
        SQLModel.metadata.create_all(self.engine)

    def insert_defect_info(self, defect_info: DefectInfo):
        """DefectInfoデータをデータベースに挿入"""
        with Session(self.engine) as session:
            session.add(defect_info)
            session.commit()

    def insert_repaird_info(self, repaird_info: RepairdInfo):
        """RepairdInfoデータをデータベースに挿入"""
        with Session(self.engine) as session:
            session.add(repaird_info)
            session.commit()

    def get_defect_info_by_id(self, defect_id: str) -> Optional[DefectInfo]:
        """IDでDefectInfoを取得"""
        with Session(self.engine) as session:
            return session.get(DefectInfo, defect_id)

    def get_all_defect_info(self) -> List[DefectInfo]:
        """全てのDefectInfoを取得"""
        with Session(self.engine) as session:
            statement = select(DefectInfo)
            return list(session.exec(statement).all())

    def get_defect_info_by_lot(self, lot_number: str) -> List[DefectInfo]:
        """指図番号でDefectInfoを取得"""
        with Session(self.engine) as session:
            statement = select(DefectInfo).where(DefectInfo.lot_number == lot_number)
            return list(session.exec(statement).all())

    def get_repaird_info_by_id(self, repair_id: str) -> Optional[RepairdInfo]:
        """IDでRepairdInfoを取得"""
        with Session(self.engine) as session:
            return session.get(RepairdInfo, repair_id)

    def get_all_repaird_info(self) -> List[RepairdInfo]:
        """全てのRepairdInfoを取得"""
        with Session(self.engine) as session:
            statement = select(RepairdInfo)
            return list(session.exec(statement).all())

    def insert_defect_info_batch(self, defect_infos: List[DefectInfo]):
        """DefectInfoデータを一括挿入"""
        with Session(self.engine) as session:
            for defect_info in defect_infos:
                session.add(defect_info)
            session.commit()

    def insert_repaird_info_batch(self, repaird_infos: List[RepairdInfo]):
        """RepairdInfoデータを一括挿入"""
        with Session(self.engine) as session:
            for repaird_info in repaird_infos:
                session.add(repaird_info)
            session.commit()

    def delete_defect_info(self, defect_id: str) -> bool:
        """DefectInfoを削除"""
        with Session(self.engine) as session:
            defect_info = session.get(DefectInfo, defect_id)
            if defect_info:
                session.delete(defect_info)
                session.commit()
                return True
            return False

    def delete_repaird_info(self, repair_id: str) -> bool:
        """RepairdInfoを削除"""
        with Session(self.engine) as session:
            repaird_info = session.get(RepairdInfo, repair_id)
            if repaird_info:
                session.delete(repaird_info)
                session.commit()
                return True
            return False

from typing import Union

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, Integer, Float, String
from sqlalchemy.orm import sessionmaker
import os

base = declarative_base()
url = "postgresql://diegomatematicav1_user:OdLdU8jhROFMHVohKBpDaBCMBKZ7vypc@dpg-cmt9748l6cac73ask9vg-a.oregon-postgres.render.com/diegomatematicav1"

class BaseSiepe:
    __tablename__ = 'siepe'
    id = Column(Integer, primary_key=True, autoincrement=True)
    username = Column(String, nullable=False)
    autorizacao = Column(String, nullable=False)

class BancoDadosSiepe:
    def __init__(self):
        database_url = url
        self.engine = create_engine(database_url, echo=True)
        session = sessionmaker(bind=self.engine)
        self.db = session()
        self.metadata = MetaData()
        self.base = BaseSiepe
    
    def create_tables(self):
        BaseSiepe.metadata.create_all(self.engine)
    
    def consulta_username(self, username, tabela: Union[type, object]):
        consulta = self.db.query(tabela).filter(tabela.username == username).scalar()
        return consulta.autorizacao

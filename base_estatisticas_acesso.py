from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, Integer, Float, String, Boolean, JSON
from sqlalchemy.orm import sessionmaker
import os
import requests

base = declarative_base()
url = "postgresql://diego:rush1985@192.168.0.17:5432/matematica_local"


class Estatisticas(base):
    __tablename__ = "estatisticas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    data_acesso = Column(String, nullable=False)  # ou DateTime, se for usar datetime.datetime
    ip = Column(String, nullable=False)
    url_acessada = Column(String, nullable=True)
    tempo_permanencia = Column(Float, nullable=True)  # em segundos
    referenciador = Column(String, nullable=True)  # de onde veio o acesso (referer)
    resolucao_tela = Column(String, nullable=True)

class BancoDadosEstatisticas:
    def __init__(self):
        database_url = url
        self.engine = create_engine(database_url, echo=True)
        session = sessionmaker(bind=self.engine)
        self.db = session()
        self.metadata = MetaData()
        self.base = Estatisticas
    
    def create_tables(self):
        base.metadata.create_all(self.engine)
    

banco = BancoDadosEstatisticas()
banco.create_tables()
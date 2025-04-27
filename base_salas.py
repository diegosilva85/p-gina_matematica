from typing import Union
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import create_engine, MetaData, Column, Integer, Float, String, Boolean, JSON
from sqlalchemy.orm import sessionmaker
import os


base = declarative_base()
url = "postgresql://diego:rush1985@192.168.0.17:5432/matematica_local"

class Salas(base):
    __tablename__ = "salas"
    id = Column(Integer, primary_key=True, autoincrement=True)
    codigo = Column(String, nullable=False)
    sala = Column(String, nullable=False)
    dono = Column(String, nullable=False)
    senha = Column(String, nullable=False)
    jogadores = Column(JSON, nullable=False, default=list)
    pontos = Column(JSON, nullable=False, default=dict)
    partidas = Column(Integer, nullable=False, default=0)
    iniciar = Column(Integer, nullable=False, default=0)
    sid = Column(JSON, nullable=False, default=list)
    nivel = Column(JSON, nullable=False, default=dict)
    pares = Column(JSON, nullable=False, default=list)

    def dicionario(self):
        return {
            "id": self.id,
            "codigo": self.codigo,
            "sala": self.sala,
            "dono": self.dono,
            "senha": self.senha,
            "jogadores": self.jogadores,
            "pontos": self.pontos,
            "partidas": self.partidas,
            "iniciar": self.iniciar,
            "sid": self.sid,
            "nivel": self.nivel,
            # Se tiver outros atributos, adicione aqui.
        }

class BancoDadosSalas:
    def __init__(self):
        database_url = url
        self.engine = create_engine(database_url, echo=True)
        session = sessionmaker(bind=self.engine)
        self.db = session()
        self.metadata = MetaData()
        self.base = Salas
    
    def create_tables(self):
        base.metadata.create_all(self.engine)
    
    

banco = BancoDadosSalas()
banco.create_tables()
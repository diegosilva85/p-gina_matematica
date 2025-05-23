from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Integer


class Base(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    nome: Mapped[str] = mapped_column(unique=True, nullable=False)
    prova1: Mapped[float] = mapped_column(nullable=True)
    prova2: Mapped[float] = mapped_column(nullable=True)
    prova3: Mapped[float] = mapped_column(nullable=True)
    prova4: Mapped[float] = mapped_column(nullable=True)
    prova5: Mapped[float] = mapped_column(nullable=True)
    prova6: Mapped[float] = mapped_column(nullable=True)
    prova7: Mapped[float] = mapped_column(nullable=True)
    prova8: Mapped[float] = mapped_column(nullable=True)
    prova9: Mapped[float] = mapped_column(nullable=True)
    prova10: Mapped[float] = mapped_column(nullable=True)
    prova11: Mapped[float] = mapped_column(nullable=True)
    prova12: Mapped[float] = mapped_column(nullable=True)
    pm1: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm2: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm3: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm4: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm5: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm6: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm7: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm8: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm9: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm10: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm11: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm12: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    pm: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa1: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa2: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa3: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa4: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa5: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa6: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa7: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa8: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa9: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa10: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa11: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroa12: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios1: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios2: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios3: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios4: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios5: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios6: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios7: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios8: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios9: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios10: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios11: Mapped[str] = mapped_column(nullable=True, server_default="-")
    beneficios12: Mapped[str] = mapped_column(nullable=True, server_default="-")
    boss_vitoria: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    boss_total: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_ouro: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_prata: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    coroa_bronze: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    elite: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite1: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite2: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite3: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite4: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite5: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite6: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite7: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite8: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite9: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite10: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite11: Mapped[str] = mapped_column(nullable=True, server_default="-")
    elite12: Mapped[str] = mapped_column(nullable=True, server_default="-")
    coroas_elite: Mapped[int] = mapped_column(nullable=True, server_default=str(0))
    boss_elite: Mapped[int] = mapped_column(nullable=True, server_default=str(0))


class BaseProfessor(DeclarativeBase):
    __abstract__ = True
    id: Mapped[int] = mapped_column(primary_key=True)

class BaseMurais(DeclarativeBase):
    __abstract__ = True
    turma: Mapped[str] = mapped_column(primary_key=True, nullable=True)
    prova1: Mapped[str] = mapped_column(nullable=True)
    prova2: Mapped[str] = mapped_column(nullable=True)
    prova3: Mapped[str] = mapped_column(nullable=True)
    prova4: Mapped[str] = mapped_column(nullable=True)
    prova5: Mapped[str] = mapped_column(nullable=True)
    prova6: Mapped[str] = mapped_column(nullable=True)
    prova7: Mapped[str] = mapped_column(nullable=True)
    prova8: Mapped[str] = mapped_column(nullable=True)
    prova9: Mapped[str] = mapped_column(nullable=True)
    prova10: Mapped[str] = mapped_column(nullable=True)
    prova11: Mapped[str] = mapped_column(nullable=True)
    prova12: Mapped[str] = mapped_column(nullable=True)



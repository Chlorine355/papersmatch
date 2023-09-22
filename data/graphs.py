import sqlalchemy
import sqlalchemy.orm as orm
from .db_session import SqlAlchemyBase
from sqlalchemy.ext.hybrid import hybrid_property, hybrid_method


class Graph(SqlAlchemyBase):
    __tablename__ = 'graphs'

    paperId = sqlalchemy.Column(sqlalchemy.String, primary_key=True)
    articles = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    edges = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    origin = sqlalchemy.Column(sqlalchemy.Text, nullable=True)
    year1 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)
    year2 = sqlalchemy.Column(sqlalchemy.Integer, nullable=True)

    def __repr__(self):
        return f'''chat id: {self.paperId}'''

import sqlalchemy as sqla
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy_utils import database_exists, create_database

Base = declarative_base()


class Users(Base):
    __tablename__ = 'users'

    id = sqla.Column(sqla.Integer, primary_key=True)
    vk_id_user = sqla.Column(sqla.Integer, nullable=False, unique=True)
    couples = relationship('couple', backref='user1')
    favorites = relationship('favorites', backref='user2')
    blacklists = relationship('blacklist', backref='user3')


class MatchUsers(Base):
    __tablename__ = 'match_users'
    id = sqla.Column(sqla.Integer, primary_key=True)
    vk_id = sqla.Column(sqla.Integer, nullable=False, unique=True)
    first_name = sqla.Column(sqla.String(40))
    last_name = sqla.Column(sqla.String(40))
    profile_link = sqla.Column(sqla.String(80))
    user_photos = sqla.Column(sqla.String(150))
    city = sqla.Column(sqla.String(50))
    bdate = sqla.Column(sqla.String(30))
    couples1 = relationship('couple', backref='match_user1')
    favorites1 = relationship('favorites', backref='match_user2')
    blacklists1 = relationship('blacklist', backref='match_user3')


class Couple(Base):
    __tablename__ = 'couple'
    id_user = sqla.Column(sqla.Integer, sqla.ForeignKey('users.id',  ondelete='CASCADE'), nullable=False)
    id_match_user = sqla.Column(sqla.Integer, sqla.ForeignKey('match_users.id', ondelete='CASCADE'), nullable=False)
    sqla.PrimaryKeyConstraint(id_user, id_match_user, name='couple_id_check')


class Favotites(Base):
    __tablename__ = 'favorites'
    id_user = sqla.Column(sqla.Integer, sqla.ForeignKey('users.id',  ondelete='CASCADE'), nullable=False)
    id_match_user = sqla.Column(sqla.Integer, sqla.ForeignKey('match_users.id', ondelete='CASCADE'), nullable=False)
    sqla.PrimaryKeyConstraint(id_user, id_match_user, name='favorites_id_check')


class Blacklist(Base):
    __tablename__ = 'blacklist'
    id_user = sqla.Column(sqla.Integer, sqla.ForeignKey('users.id',  ondelete='CASCADE'), nullable=False)
    id_match_user = sqla.Column(sqla.Integer, sqla.ForeignKey('match_users.id', ondelete='CASCADE'), nullable=False)
    sqla.PrimaryKeyConstraint(id_user, id_match_user, name='blacklist_id_check')


def create_tables(engine_):
    Base.metadata.drop_all(engine_)
    Base.metadata.create_all(engine_)


def main():
    with open('../config/pwd.txt', encoding='utf-8') as f:
        password = f.readline()

    login = 'postgres'
    pwd = password
    db_name = 'appinder_db'

    dsn = f'postgresql://{login}:{pwd}@localhost:5432/{db_name}'
    engine = sqla.create_engine(dsn)

    # Создаём базу данных, если не существует
    if not database_exists(engine.url):
        create_database(engine.url)

    # Создаём таблицы; на данный момент при создании удаляет старые
    create_tables(engine)


if __name__ == '__main__':
    main()

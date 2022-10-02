import psycopg2
from psycopg2 import Error


class AppinderDb:
    """Класс для пользования базой данных"""

    def __init__(self, name_db_, login_, password, port='5432', host='localhost'):
        self.name_db = name_db_
        self.login = login_
        self.password = password
        self.port = port
        self.host = host
        self.conn = psycopg2.connect(database=self.name_db,
                                     user=self.login,
                                     password=self.password,
                                     host=self.host,
                                     port=self.port)
        self.cur = self.conn.cursor()

    def add_user(self, vk_id_user):
        """Метод добавляет нового пользователя"""
        try:
            self.cur.execute("""
                    INSERT INTO users(vk_id_user)
                    VALUES (%s);
                    """, (vk_id_user,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            self.conn.commit()
            print(f'+ Пользователь {vk_id_user} добавлен в базу')

    def add_match_user(self, vk_id, first_name, last_name, profile_link, city, bdate, user_photos):
        """Метод добавляет нового совпавшего пользователя"""
        try:
            self.cur.execute("""
                            INSERT INTO match_users(vk_id, first_name, last_name,
                                                    profile_link, city, bdate, user_photos
                                                    )
                            VALUES (%s, %s, %s, %s, %s, %s, %s);
                            """, (vk_id, first_name, last_name, profile_link, city, bdate, user_photos)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            self.conn.commit()
            print(f'+ Пользователь {vk_id} добавлен в базу')

    def add_couple(self, id_user, id_match_user):
        """Метод добавляет пару id.users и id.match_users"""
        try:
            self.cur.execute("""
                                   INSERT INTO couple(id_user, id_match_user)
                                   VALUES (%s, %s);
                                   """, (id_user, id_match_user)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            self.conn.commit()
            print(f'+ Пара {id_user} + {id_match_user} добавлена в базу')

    def find_db_id_user(self, vk_id):
        """Возвращает id.users для vk_id пользователя"""
        try:
            self.cur.execute("""
                            SELECT id
                            FROM users
                            WHERE (vk_id_user = %s);
                            """, (vk_id,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            id_ = self.cur.fetchone()
            if id_:
                return id_[0]
            return id_

    def find_db_id_match_user(self, vk_id):
        """Возвращает id.match_users для vk_id совпавшего пользователя"""
        try:
            self.cur.execute("""
                            SELECT id
                            FROM match_users
                            WHERE (vk_id = %s);
                            """, (vk_id,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            id_ = self.cur.fetchone()
            if id_:
                return id_[0]
            return id_

    def get_info(self, id_):
        """Возвращает first_name, last_name, profile_link, user_photos для id.match_users"""
        try:
            self.cur.execute("""
                            SELECT (first_name, last_name, profile_link, user_photos)
                            FROM match_users
                            WHERE (id = %s);
                            """, (id_,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            return self.cur.fetchone()[0].strip('()').replace(',', ';', 3).split(';')

    def get_match_ids(self, id_user):
        """Возвращает список id.match_users для данного пользователя"""
        try:
            self.cur.execute("""
                            SELECT (id_match_user)
                            FROM couple
                            WHERE (id_user = %s);
                            """, (id_user,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            return list(map(lambda x: x[0], self.cur.fetchall()))

    def add_to_favorite(self, id_user, id_match_user):
        """Метод добавляет в список избранных id.match_users для id.users"""
        try:
            self.cur.execute("""
                                    INSERT INTO favorites(id_user, id_match_user)
                                    VALUES (%s, %s);
                                    """, (id_user, id_match_user)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            self.conn.commit()
            print(f'+ Избранный {id_match_user} для {id_user} добавлен в базу')

    def add_to_black_list(self, id_user, id_match_user):
        """Метод добавляет в "черный" список id.match_users для id.users"""
        try:
            self.cur.execute("""
                                    INSERT INTO blacklist(id_user, id_match_user)
                                    VALUES (%s, %s);
                                    """, (id_user, id_match_user)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            self.conn.commit()
            print(f'+ {id_match_user} для {id_user} добавлен в "Черный Список"')

    def get_favorites(self, id_user):
        """Метод выводит список избранных для id.users"""
        try:
            self.cur.execute("""
                            SELECT (id_match_user)
                            FROM favorites
                            WHERE (id_user = %s);
                            """, (id_user,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            return list(map(lambda x: x[0], self.cur.fetchall()))

    def get_blacklist(self, id_user):
        """Метод выводит черный список найденных людей для id.users"""
        try:
            self.cur.execute("""
                            SELECT (id_match_user)
                            FROM blacklist
                            WHERE (id_user = %s);
                            """, (id_user,)
                             )
        except Error as err:
            print(f'--> {err}')
            self.conn.rollback()
        else:
            return list(map(lambda x: x[0], self.cur.fetchall()))

    def close(self):
        """Метод закрывает все соединения с базой данных"""
        self.cur.close()
        self.conn.close()


if __name__ == '__main__':
    # # для проверки
    # name_db = 'appinder_db'
    # login = 'postgres'
    # with open('../config/pwd.txt', encoding='utf-8') as f:
    #     pwd = f.readline()
    # me = AppinderDb(name_db, login, password=pwd)
    #
    # print(me.find_db_id_match_user(746536032))
    # print(me.find_db_id_match_user(1))
    # me.close()
    pass

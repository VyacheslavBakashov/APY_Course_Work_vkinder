from config.config import vk_group_token, token_, pwd
import random
from VK.vk_funcs import VkBot
from DB.db_class import AppinderDb

USER_TOKEN = token_
GROUP_TOKEN = vk_group_token
DB_PWD = pwd


def get_skip_lists(id_user, db_conn):
    """Формирует список исключений для показов по user_db_id"""
    fav_list = db_conn.get_favorites(id_user)
    black_list_ = db_conn.get_blacklist(id_user)
    return fav_list + black_list_


def get_available_ids(user_id, db_conn) -> list:
    """Выводит список match_user_id для user_vk_id,
    которых нет в favorite_list и black_list"""
    db_id = db_conn.find_db_id_user(user_id)
    match_ids = db_conn.get_match_ids(db_id)
    skip_list = get_skip_lists(db_id, db_conn)
    return list(set(match_ids).difference(set(skip_list)))


def get_random_user_db(db_conn, some_ids):
    """Выводит данные из базы данных произвольного совпадения для user_vk_id"""
    keys = ['first_name', 'last_name', 'profile_link', 'user_photos']
    values = db_conn.get_info(random.choice(some_ids))
    return dict(zip(keys, values))


def get_user_db(db_conn, some_id):
    """Выводит данные из базы данных совпадения match_user.id"""
    keys = ['first_name', 'last_name', 'profile_link', 'user_photos']
    values = db_conn.get_info(some_id)

    return dict(zip(keys, values))


def search_add_users(user_id, vk_conn, db_conn, count=100):
    """Ищет людей и добавляет их в базу данных (в match_users и couple) для user_vk_id"""
    params = vk_conn.get_params_for_search(user_id)
    search_resp = vk_conn.search(count=count, **params)
    found_list = iter(vk_conn.make_found_list(user_id, db_conn, search_resp))

    for person in found_list:
        db_conn.add_match_user(**person)
        db_conn.add_couple(
                            db_conn.find_db_id_user(user_id_),
                            db_conn.find_db_id_match_user(person['vk_id'])
                          )


def show_list(some_list, db_conn, vk_conn, user_id):
    """Используется при выводе списка избранных или черного списка"""
    if some_list:
        for match_id_db in some_list:
            info = db_conn.get_info(match_id_db)
            vk_conn.push_show_list(user_id, info)
    else:
        vk_conn.send_message(user_id_, 'Список пуст', vk_conn.key_review.get_keyboard())


def find_db_ids(user_id, person, db_conn):
    """ Выводит кортеж (id.users, id.match.users) из базы данных"""
    match_user_id = person['profile_link'].strip('https://vk.com/id')
    return db_conn.find_db_id_user(user_id), db_conn.find_db_id_match_user(match_user_id)


if __name__ == '__main__':

    name_db = 'appinder_db'
    login = 'postgres'
    password = DB_PWD

    my_db = AppinderDb(name_db_=name_db, login_=login, password=password)
    # my_db.close()
    my_bot = VkBot(gr_token=GROUP_TOKEN, user_token=token_)
    current_finding = ''
    try:
        while True:
            user_id_, msg = my_bot.bot_listen()
            if msg.lower() in ['привет', 'hello', 'hi', '/q', 'прив']:
                my_bot.say_hello(user_id_, my_db)

            elif msg.lower() in ['старт', '/s', '/ы']:
                my_db.add_user(user_id_)
                search_add_users(user_id_, db_conn=my_db, vk_conn=my_bot)
                current_finding = get_random_user_db(my_db, get_available_ids(user_id_, my_db))
                my_bot.push_start(user_id_, current_finding)

            elif msg.lower() in ['next', '/n']:
                avail_ids = get_available_ids(user_id_, my_db)
                if len(avail_ids) > 3:
                    current_finding = get_random_user_db(my_db, avail_ids)
                else:
                    my_bot.push_search_more(user_id_)
                    search_add_users(user_id_, db_conn=my_db, vk_conn=my_bot)
                    current_finding = get_random_user_db(my_db, get_available_ids(user_id_, my_db))
                my_bot.push_next(user_id_, current_finding)

            elif msg.lower() in ['to favorite list', '/af']:
                try:
                    id_db_user, id_db_match_user = find_db_ids(user_id_, current_finding, my_db)
                except Exception as err:
                    print(err)
                    my_bot.send_message(user_id_, 'Кликни Next', my_bot.key_review.get_keyboard())
                else:
                    my_db.add_to_favorite(id_db_user, id_db_match_user)
                    my_bot.push_add_favorite(user_id_, current_finding)

            elif msg.lower() in ['to black list', '/abl']:
                try:
                    id_db_user, id_db_match_user = find_db_ids(user_id_, current_finding, my_db)
                except Exception as err:
                    print(err)
                    my_bot.send_message(user_id_, 'Кликни Next', my_bot.key_review.get_keyboard())
                else:
                    my_db.add_to_black_list(id_db_user, id_db_match_user)
                    my_bot.push_add_blacklist(user_id_, current_finding)

            elif msg.lower() in ['show favorites', '/sf']:
                favorites_list = my_db.get_favorites(my_db.find_db_id_user(user_id_))
                show_list(favorites_list, my_db, my_bot, user_id_)

            elif msg.lower() in ['show black list', '/sbl']:
                black_list = my_db.get_blacklist(my_db.find_db_id_user(user_id_))
                show_list(black_list, my_db, my_bot, user_id_)

            elif msg.lower() in ['find more', '/fm']:
                my_bot.send_message(user_id_, 'Поиск займёт какое-то время',
                                    my_bot.key_review.get_keyboard())
                search_add_users(user_id_, db_conn=my_db, vk_conn=my_bot, count=100)
                my_bot.send_message(user_id_, 'Готово! Кликни Next',
                                    my_bot.key_review.get_keyboard())

            else:
                my_bot.wrong_message(user_id_)

    except Exception as err:
        print(err)
        my_db.close()

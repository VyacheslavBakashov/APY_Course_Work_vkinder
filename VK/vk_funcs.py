import random
import vk_api
from vk_api.exceptions import ApiError
from datetime import datetime as dt
from vk_api.longpoll import VkLongPoll, VkEventType
from vk_api.keyboard import VkKeyboard, VkKeyboardColor


class VkBot:

    def __init__(self, gr_token: str, user_token: str, api_version='5.131'):
        self.vk_session = vk_api.VkApi(token=gr_token)
        self.user_session = vk_api.VkApi(token=user_token)
        # self.serv_session = vk_api.VkApi(token=service_group_token_)
        self.api_version = api_version
        self.long_poll = VkLongPoll(self.vk_session)

        # кнопки
        self.key_begin = VkKeyboard(one_time=True)
        self.key_begin.add_button(label='Старт', color=VkKeyboardColor.PRIMARY)

        self.key_review = VkKeyboard(one_time=False)
        self.key_review.add_button(label='Next', color=VkKeyboardColor.PRIMARY)
        self.key_review.add_button(label='To Favorite List', color=VkKeyboardColor.POSITIVE)
        self.key_review.add_button(label='To Black List', color=VkKeyboardColor.NEGATIVE)
        self.key_review.add_line()
        self.key_review.add_button(label='Show Favorites', color=VkKeyboardColor.PRIMARY)
        self.key_review.add_button(label='Show Black List', color=VkKeyboardColor.PRIMARY)
        # self.key_review.add_button(label='Find More', color=VkKeyboardColor.PRIMARY)

    def bot_listen(self):
        """
        Прослушивание беседы с пользователем
        :return: (user_vk_id, user_text)
        """
        for event in self.long_poll.listen():
            if event.type == VkEventType.MESSAGE_NEW:
                if event.to_me:
                    msg_text = event.text
                    user_id = event.user_id
                    return user_id, msg_text

    def get_user_info(self, user_id) -> dict:
        """
        Возвращает словарь из параметров пользователя
        :param user_id: vk_user_id
        :return: {'first_name': имя, 'last_name': фамилия, 'city': город,
         'bdate': дата рождения, 'sex': пол, 'id': VK_id}
        """
        resp = self.vk_session.method('users.get', {'user_ids': user_id, 'fields': 'city, sex, bdate'})[0]
        resp.pop('can_access_closed')
        resp.pop('is_closed')
        return resp

    def _get_photos(self, owner_id):
        """Вспомогательный метод для получения трех фотографии для подстановки в attachment сообщения от бота"""
        params_ = {'owner_id': owner_id,
                   'album_id': -6,
                   'extended': 1,
                   'has_photo': 1,
                   'photo_sizes': 1,
                   'count': 15}

        def get_three_photos(response):
            return sorted(response['items'], key=lambda x: x['likes']['count'], reverse=True)[:3]

        try:
            resp = self.user_session.method('photos.get', params_)
        except ApiError:
            return
        else:
            return ','.join([f'photo{owner_id}_{photo["id"]}' for photo in get_three_photos(resp)])

    def search(self, sex: str, age_from=18, age_to=None, city=None, country=1, count=50) -> list:
        """
        Метод для поиска пользователей VK по параметрам
        :param count: количество для поиска
        :param sex: пол
        :param age_from: с какого возраста
        :param age_to: до какого возраста
        :param city: город номером ВК
        :param country: сирана по номеру ВК
        :return: список словарей с данными, найденных пользователей
        """
        if age_from < 18:
            age_from = 18
        fields = {
            'sort': random.randint(0, 1),
            'country': country,
            'city': city,
            'status': 1,
            'count': count,
            'sex': sex,
            'age_from': age_from,
            'age_to': age_to,
            'is_closed': False,
            'fields': 'bdate, city, sex'
        }
        try:
            response = self.user_session.method('users.search', fields)
        except ApiError as err:
            print(err, 'Поиск не удался')
            return []
        else:
            found_list = []
            keys = ['first_name', 'last_name', 'profile_link', 'vk_id', 'bdate', 'user_photos']
            for item in response['items']:
                photos = self._get_photos(item['id'])
                if photos and item.get('sex'):
                    values = [item[keys[0]],
                              item[keys[1]],
                              'https://vk.com/id' + str(item['id']),
                              item['id'],
                              item[keys[4]],
                              photos
                              ]
                    person_info = dict(zip(keys, values))
                    person_info['city'] = item.get('city', {'id': None})['id']
                    found_list.append(person_info)
            return found_list

    def get_params_for_search(self, user_id) -> dict:
        """
        Получает словарь с параметрами для поиска на основании данных пользователя
        :param user_id: vk_user_id
        :return: словарь с параметрами поиска
        """
        user_info = self.get_user_info(user_id)
        user_age = (dt.now() - dt.strptime(user_info['bdate'], '%d.%m.%Y')).days // 365  # приблизительно
        find_dict = {
            'sex': user_info['sex'] % 2 + 1,
            'city': user_info['city']['id'],
            'age_from': user_age - 10,
            'age_to': user_age
        }
        return find_dict

    # общение
    def send_message(self, user_id, message, keyboard=None, attachment=None):
        """
        Посылает сообщение пользователю
        :param user_id: vk_id
        :param message: текст сообщения
        :param keyboard: клавиатура, по умолчанию отсутствует
        :param attachment: приложенные фото, по умолчанию отсутствуют
        :return: сообщение в чат с пользователем
        """
        self.vk_session.method('messages.send', {'user_id': user_id,
                                                 'message': message,
                                                 'random_id': 0,
                                                 'keyboard': keyboard,
                                                 'attachment': attachment
                                                 }
                               )

    def say_hello(self, user_id, db_conn):
        """
        Метод для отправки сообщения с приветствием пользователю
        :param user_id: vk_id
        :param db_conn: экземпляр класса лоя работы с базой данных
        :return: сообщение в чат с пользователем
        """
        user_name = self.get_user_info(user_id)["first_name"]
        if db_conn.find_db_id_user(user_id):
            message = f"С возвращением, {user_name}! Рад тебя видеть! Продолжим!"
            self.send_message(user_id=user_id, message=message, keyboard=self.key_review.get_keyboard())
        else:
            message = f"""Приветствую, {user_name}!
                  Я могу помочь найти тебе вторую половинку. Нажми кнопку 'Старт'.
                  Первый поиск может занять некоторое время..."""
            self.send_message(user_id=user_id, message=message, keyboard=self.key_begin.get_keyboard())

    def push_start(self, user_id, found_user):
        """
        Действие при нажатии на кнопку 'Старт'
        :param user_id:
        :param found_user: словарь с данными, случайно найденного совпадения из базы данных для данного пользователя
        :return:
        """
        message = f'Вот кто первый нашёлся, для продолжения просмотра нажми "Next"\n' \
                  f'{found_user["first_name"]} {found_user["last_name"]}\n' \
                  f'{found_user["profile_link"]}'
        self.send_message(user_id=user_id, message=message,
                          keyboard=self.key_review.get_keyboard(),
                          attachment=found_user["user_photos"]
                          )

    def push_next(self, user_id, found_user):
        """Выводит в чат с пользователем очередной результат поиска"""
        message = f'{found_user["first_name"]} {found_user["last_name"]}\n' \
                  f'{found_user["profile_link"]}'
        self.send_message(user_id=user_id, message=message,
                          keyboard=self.key_review.get_keyboard(),
                          attachment=found_user["user_photos"]
                          )

    def push_add_blacklist(self, user_id, challenger):
        """Выводит сообщение, что текущий результат добавлен черный список"""
        message = f'{challenger["first_name"]} теперь в "Черном" списке'
        self.send_message(user_id=user_id, message=message,
                          keyboard=self.key_review.get_keyboard()
                          )

    def push_add_favorite(self, user_id, challenger):
        """Выводит сообщение, что текущий результат добавлен список избранных"""
        message = f'{challenger["first_name"]} теперь в списке "Избранных"'
        self.send_message(user_id=user_id, message=message,
                          keyboard=self.key_review.get_keyboard()
                          )

    def push_show_list(self, user_id, user_info):
        """Выводит в чат данные пользователя из списка избранных или черного списка"""
        fn, ln, link = user_info[:-1]
        message = f'{fn}, {ln}, {link}'
        self.send_message(user_id=user_id, message=message,
                          keyboard=self.key_review.get_keyboard())

    def push_search_more(self, user_id):
        """Выводит сообщение, что текущий результат добавлен список избранных"""
        message = f'Подождите немного... В поиске...)'
        self.send_message(user_id=user_id, message=message,
                          keyboard=self.key_review.get_keyboard())

    def wrong_message(self, user_id):
        """Выыодится в случае, когда бот не смог обработать сообщение от собеседника"""
        message = 'Не понимаю тебя'
        self.send_message(user_id=user_id, message=message)

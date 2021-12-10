import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey, Text
from sqlalchemy.orm import mapper, sessionmaker

from common.variables import SERVER_DATABASE


class DataBaseServer:
    # All Users
    class ChatUsers:
        def __init__(self, user_name, passwd_hash):
            self.user_name = user_name
            self.login_time = datetime.datetime.now()
            self.passwd_hash = passwd_hash
            self.pubkey = None
            self.id = None

    # Login users history
    class ChatUsersHistory:
        def __init__(self, user_name, ip_address, date):
            self.user_name = user_name
            self.login_time = date
            self.ip_address = ip_address
            self.id = None

    # Active Users
    class ChatContacts:
        def __init__(self, user_name, ip_address, login_time):
            self.login_time = login_time
            self.ip_address = ip_address
            self.user_name = user_name
            self.id = None

    # Users Contacts
    class Contacts:
        def __init__(self, user, contact):
            self.id = None
            self.user = user
            self.contact = contact

    # History of actions users
    class UsersHistory:
        def __init__(self, user):
            self.id = None
            self.user = user
            self.sent = 0
            self.accepted = 0

    def __init__(self, path):
        self.database_core = create_engine(f'sqlite:///{path}', echo=False, pool_recycle=7200,
                                           connect_args={'check_same_thread': False})
        self.meta = MetaData()

        chat_users_table = Table('ChatUsers', self.meta,
                                 Column('id', Integer, primary_key=True),
                                 Column('user_name', String(50), unique=True),
                                 Column('login_time', DateTime),
                                 Column('passwd_hash', String),
                                 Column('pubkey', Text)
                                 )
        chat_history_table = Table('ChatUsersHistory', self.meta,
                                   Column('id', Integer, primary_key=True),
                                   Column('user_name', ForeignKey('ChatUsers.id')),
                                   Column('login_time', DateTime),
                                   Column('ip_address', String(50))
                                   )
        chat_contacts_table = Table('ChatContacts', self.meta,
                                    Column('id', Integer, primary_key=True),
                                    Column('user_name', ForeignKey('ChatUsers.id')),
                                    Column('login_time', DateTime),
                                    Column('ip_address', String(50))
                                    )
        contacts = Table('Contacts', self.meta,
                         Column('id', Integer, primary_key=True),
                         Column('user', ForeignKey('ChatUsers.id')),
                         Column('contact', ForeignKey('ChatUsers.id'))
                         )
        users_history_table = Table('UsersHistory', self.meta,
                                    Column('id', Integer, primary_key=True),
                                    Column('user', ForeignKey('ChatUsers.id')),
                                    Column('sent', Integer),
                                    Column('accepted', Integer)
                                    )
        self.meta.create_all(self.database_core)
        mapper(self.ChatUsers, chat_users_table)
        mapper(self.ChatUsersHistory, chat_history_table)
        mapper(self.ChatContacts, chat_contacts_table)
        mapper(self.Contacts, contacts)
        mapper(self.UsersHistory, users_history_table)
        Cursor = sessionmaker(bind=self.database_core)
        self.cursor = Cursor()
        self.cursor.query(self.ChatContacts).delete()
        self.cursor.commit()

    def login(self, user_name, ip_addr, key):
        request = self.cursor.query(self.ChatUsers).filter_by(user_name=user_name)
        if request.count():
            current_user = request.first()
            current_user.login_time = datetime.datetime.now()
            if current_user.pubkey != key:
                current_user.pubkey = key
        else:
            raise ValueError('Пользователь не зарегистрирован.')

        # Теперь можно создать запись в таблицу активных пользователей о факте
        # входа.
        new_active_user = self.ChatContacts(
            current_user.id, ip_addr, datetime.datetime.now())
        self.cursor.add(new_active_user)

        # и сохранить в историю входов
        history = self.ChatUsersHistory(current_user.id, ip_addr, datetime.datetime.now())
        self.cursor.add(history)

        # Сохрраняем изменения
        self.cursor.commit()
        # else:
        #     current_user = self.ChatUsers(user_name)
        #     self.cursor.add(current_user)
        #     self.cursor.commit()
        # new_chat_contact = self.ChatContacts(current_user.id, ip_addr, datetime.datetime.now())
        # user_history = self.ChatUsersHistory(current_user.id, ip_addr, datetime.datetime.now())
        # self.cursor.add(new_chat_contact)
        # self.cursor.add(user_history)
        # self.cursor.commit()

    def logout(self, user_name):
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=user_name).first()
        if user:
            self.cursor.query(self.ChatContacts).filter_by(user_name=user.id).delete()
            self.cursor.commit()

    def history(self, user_name=None):
        query = self.cursor.query(self.ChatUsers.user_name,
                                  self.ChatUsersHistory.login_time,
                                  self.ChatUsersHistory.ip_address
                                  ).join(self.ChatUsers)
        if user_name:
            query = query.filter(self.ChatUsers.user_name == user_name)
        return query.all()

    def message_history(self):
        query = self.cursor.query(
            self.ChatUsers.user_name,
            self.ChatUsers.login_time,
            self.UsersHistory.sent,
            self.UsersHistory.accepted
        ).join(self.ChatUsers)
        return query.all()

    def online(self):
        query = self.cursor.query(
            self.ChatUsers.user_name,
            self.ChatContacts.ip_address,
            self.ChatContacts.login_time
        ).join(self.ChatUsers)
        return query.all()

    def users(self):
        query = self.cursor.query(
            self.ChatUsers.user_name,
            self.ChatUsers.id
        )
        return query.all()

    def add_user(self, user_name, passwd_hash):
        """
        Метод регистрации пользователя.
        Принимает имя и хэш пароля, создаёт запись в таблице статистики.
        """
        user_row = self.ChatUsers(user_name, passwd_hash)
        self.cursor.add(user_row)
        self.cursor.commit()
        history_row = self.UsersHistory(user_row.id)
        self.cursor.add(history_row)
        self.cursor.commit()

    def remove_user(self, name):
        """Метод удаляющий пользователя из базы."""
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=name).first()
        self.cursor.query(self.ChatContacts).filter_by(user_name=user.id).delete()
        self.cursor.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.cursor.query(self.Contacts).filter_by(user=user.id).delete()
        self.cursor.query(
            self.Contacts).filter_by(
            contact=user.id).delete()
        self.cursor.query(self.UsersHistory).filter_by(user=user.id).delete()
        self.cursor.query(self.ChatUsers).filter_by(user_name=name).delete()
        self.cursor.commit()

    def check_user(self, name):
        if self.cursor.query(self.ChatUsers).filter_by(user_name=name).count():
            return True
        else:
            return False

    def message_count(self, sender, recipient):
        sender = self.cursor.query(self.ChatUsers).filter_by(user_name=sender).first().id
        recipient = self.cursor.query(self.ChatUsers).filter_by(user_name=recipient).first().id
        sender_row = self.cursor.query(self.UsersHistory).filter_by(user=sender).first()
        if sender_row is not None:
            sender_row.sent += 1
        else:
            # вручную создаем первую запись отправителя и увеличиваем счетчик отправок на 1
            new_sender = self.UsersHistory(
                user=sender
            )
            self.cursor.add(new_sender)
            self.cursor.commit()
            sender_row = self.cursor.query(self.UsersHistory).filter_by(user=sender).first()
            sender_row.sent = 1
        recipient_row = self.cursor.query(self.UsersHistory).filter_by(user=recipient).first()
        if recipient_row is not None:
            recipient_row.accepted += 1
        else:
            # вручную создаем первую запись получателя и увеличиваем счетчик получений на 1
            new_recipient = self.UsersHistory(
                user=recipient
            )
            self.cursor.add(new_recipient)
            self.cursor.commit()
            recipient_row = self.cursor.query(self.UsersHistory).filter_by(user=recipient).first()
            recipient_row.accepted = 1
        self.cursor.commit()

    def add_contact(self, user, contact):
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=user).first()
        contact = self.cursor.query(self.ChatUsers).filter_by(user_name=contact).first()
        if not contact or self.cursor.query(self.Contacts).filter_by(user=user.id, contact=contact.id).count():
            return
        contact_row = self.Contacts(user.id, contact.id)
        self.cursor.add(contact_row)
        self.cursor.commit()

    def remove_contact(self, user, contact):
        """Метод удаления контакта пользователя."""
        # Получаем ID пользователей
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=user).first()
        contact = self.cursor.query(
            self.ChatUsers).filter_by(
            user_name=contact).first()

        # Проверяем что контакт может существовать (полю пользователь мы
        # доверяем)
        if not contact:
            return

        # Удаляем требуемое
        self.cursor.query(self.Contacts).filter(
            self.Contacts.user == user.id,
            self.Contacts.contact == contact.id
        ).delete()
        self.cursor.commit()

    def get_contacts(self, username):
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=username).one()
        query = self.cursor.query(self.Contacts, self.ChatUsers.user_name). \
            filter_by(user=user.id). \
            join(self.ChatUsers, self.Contacts.contact == self.ChatUsers.id)
        return [contact[1] for contact in query.all()]

    def get_hash(self, name):
        """Метод получения хэша пароля пользователя."""
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=name).first()
        return user.passwd_hash

    def get_pubkey(self, name):
        """Метод получения публичного ключа пользователя."""
        user = self.cursor.query(self.ChatUsers).filter_by(user_name=name).first()
        return user.pubkey


if __name__ == '__main__':
    test_db = DataBaseServer('')
    test_db.login('test1', '192.168.88.2')
    test_db.login('test2', '192.168.88.3')
    print(test_db.users())
    print(test_db.online())
    # test_db.add_contact('test2', 'test1')
    # test_db.add_contact('test2', 'test1')
    # test_db.message_count('test2', 'test1')
    # print(test_db.message_history())

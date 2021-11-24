import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import mapper, sessionmaker

from DBandPyQT.common.variables import SERVER_DATABASE


class DataBaseServer:
    class ChatUsers:
        def __init__(self, user_name):
            self.user_name = user_name
            self.login_time = datetime.datetime.now()
            self.id = None

    class ChatUsersHistory:
        def __init__(self, user_name, ip_address, date):
            self.user_name = user_name
            self.login_time = date
            self.ip_address = ip_address
            self.id = None

    class ChatContacts:
        def __init__(self, user_name, ip_address, login_time):
            self.login_time = login_time
            self.ip_address = ip_address
            self.user_name = user_name
            self.id = None

    def __init__(self):
        self.database_core = create_engine(SERVER_DATABASE, echo=False, pool_recycle=7200)
        self.meta = MetaData()

        chat_users_table = Table('ChatUsers', self.meta,
                                 Column('id', Integer, primary_key=True),
                                 Column('user_name', String(50), unique=True),
                                 Column('login_time', DateTime)
                                 )
        chat_history_table = Table('ChatHistory', self.meta,
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
        self.meta.create_all(self.database_core)
        mapper(self.ChatUsers, chat_users_table)
        mapper(self.ChatUsersHistory, chat_history_table)
        mapper(self.ChatContacts, chat_contacts_table)
        Cursor = sessionmaker(bind=self.database_core)
        self.cursor = Cursor()
        self.cursor.query(self.ChatContacts).delete()
        self.cursor.commit()

    def login(self, user_name, ip_addr):
        request = self.cursor.query(self.ChatUsers).filter_by(user_name=user_name)
        if request.count():
            current_user = request.first()
            current_user.login_time = datetime.datetime.now()
        else:
            current_user = self.ChatUsers(user_name)
            self.cursor.add(current_user)
            self.cursor.commit()
        new_chat_contact = self.ChatContacts(current_user.id, ip_addr, datetime.datetime.now())
        user_history = self.ChatUsersHistory(current_user.id, ip_addr, datetime.datetime.now())
        self.cursor.add(new_chat_contact)
        self.cursor.add(user_history)
        self.cursor.commit()

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

    def chat_contacts(self):
        query = self.cursor.query(
            self.ChatUsers.user_name,
            self.ChatContacts.ip_address,
            self.ChatContacts.login_time
        ).join(self.ChatUsers)
        return query.all()

    def all_users(self):
        query = self.cursor.query(
            self.ChatUsers.user_name
        )
        return query.all()


if __name__ == '__main__':
    test_db = DataBaseServer()

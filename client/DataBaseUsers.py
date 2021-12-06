import datetime

from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, DateTime
from sqlalchemy.orm import mapper, sessionmaker


class DataBaseClients:
    # All messages
    class Messages:
        def __init__(self, from_user, to_user, message):
            self.id = None
            self.from_user = from_user
            self.to_user = to_user
            self.message = message
            self.date = datetime.datetime.now()

    # All users from server
    class AllUsers:
        def __init__(self, user):
            self.id = None
            self.user = user

    # Contacts
    class Contacts:
        def __init__(self, contact):
            self.id = None
            self.name = contact

    def __init__(self, name):
        self.database_core = create_engine(f'sqlite:///client_{name}.db3', echo=False, pool_recycle=7200,
                                           connect_args={'check_same_thread': False})
        self.meta = MetaData()

        all_users = Table('AllUsers', self.meta,
                          Column('id', Integer, primary_key=True),
                          Column('user', String(50), unique=True)
                          )
        user_contacts = Table('Contacts', self.meta,
                              Column('id', Integer, primary_key=True),
                              Column('name', String(50), unique=True)
                              )
        messages = Table('Messages', self.meta,
                         Column('id', Integer, primary_key=True),
                         Column('from_user', String(50)),
                         Column('to_user', String(50)),
                         Column('message', String(500)),
                         Column('date', DateTime)
                         )

        self.meta.create_all(self.database_core)
        mapper(self.Messages, messages)
        mapper(self.AllUsers, all_users)
        mapper(self.Contacts, user_contacts)
        Cursor = sessionmaker(bind=self.database_core)
        self.cursor = Cursor()
        self.cursor.query(self.Contacts).delete()
        self.cursor.commit()

    def add_contact(self, contact):
        if not self.cursor.query(self.Contacts).filter_by(name=contact).count():
            new_contact = self.Contacts(contact)
            self.cursor.add(new_contact)
            self.cursor.commit()

    def remove_contact(self, contact):
        self.cursor.query(self.Contacts).filter_by(name=contact).delete()
        self.cursor.commit()

    def check_contact(self, contact):
        if self.cursor.query(self.Contacts).filter_by(name=contact).count():
            return True
        else:
            return False

    def get_contacts(self):
        return [contact[0] for contact in self.cursor.query(self.Contacts.name).all()]

    def add_users(self, users_list):
        self.cursor.query(self.AllUsers).delete()
        for user in users_list:
            new_user = self.AllUsers(user)
            self.cursor.add(new_user)
        self.cursor.commit()

    def get_users(self):
        return [user[0] for user in self.cursor.query(self.AllUsers.user).all()]

    def check_user(self, user):
        if self.cursor.query(self.AllUsers).filter_by(user=user).count():
            return True
        else:
            return False

    def save_message(self, from_user, to_user, message):
        if self.check_user(from_user) and self.check_user(to_user):
            new_message = self.Messages(from_user, to_user, message)
            self.cursor.add(new_message)
            self.cursor.commit()
            return True
        else:
            return False

    def get_history(self, from_user=None, to_user=None):
        query = self.cursor.query(self.Messages)
        if from_user:
            query = query.filter_by(from_user=from_user)
        if to_user:
            query = query.filter_by(to_user=to_user)
        return [(history_row.from_user, history_row.to_user, history_row.message, history_row.date)
                for history_row in query.all()]


if __name__ == '__main__':
    test_db = DataBaseClients('test1')
    # test_db.add_contact('test1')
    # test_db.remove_contact('test1')
    # test_db.add_contact('test2')
    # test_db.add_contact('test3')
    # test_db.add_contact('test4')
    # print(test_db.check_contact('test2'))
    # print(test_db.get_contacts())
    # test_db.add_users(['test5', 'test6', 'test7', 'test8', 'test9', 'test0', ])
    # print(test_db.get_users())
    # test_db.save_message('test5', 'test0', 'new message')
    # print(test_db.save_message('test11', 'test0', 'new message'))
    # print(test_db.get_history('test5', 'test0'))
#

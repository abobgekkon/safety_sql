#!/usr/bin/env python3

__author__= 'S.N. Pastuhov'
__copyright__= 'Copyright (c) 2019, S.N. Pastuhov'
__license__= 'Apache License, Version 2.0'

import sqlite3, os, sys, rsa
from steg.steg_code import steganography
from rsa_crypt.rsa_code import rsa_code

class db_editor:

    def __init__(self):
        self.name = ''
        self.privkey = ''
        self.pubkey = ''
        self.primage = ''
        self.pubimage = ''
        self.dec = steganography()
        self.crypt = rsa_code()

    def create_db(self, name):
        self.name = name
        self.primage = "priv_" + self.name[:-3] + ".png"
        self.pubimage = "pub_" + self.name[:-3] + ".png"
        con = sqlite3.connect(self.name)
        create_table = """\
        CREATE TABLE passwords (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        url BLOB,
        login BLOB,
        password BLOB,
        comment BLOB
        );"""
        cur = con.cursor()
        try:
            cur.executescript(create_table)
        except sqlite3.DatabaseError as err:
            print("Ошибка:", err)
        else:
            print("""\
-------------------------            
База данных {0} успешно создана
-------------------------""".format(self.name))
        cur.close()
        con.close()
        self.pubkey, self.privkey = self.crypt.get_new_keys()
        self.dec.encode(rsa.PrivateKey.save_pkcs1(self.privkey), self.primage)
        self.dec.encode(rsa.PrivateKey.save_pkcs1(self.pubkey), self.pubimage)
        self.current_db(self.name)



    def get_data(self):
        run = 1
        data = {}
        while run:
            url = input("Введите адрес сайта: ")
            login = input("Введите логин: ")
            password = input("Введите пассворд: ")  # возможно, здесь стоит скрыть ввод
            comment = input("Введите коментарий (при необходимости): ")
            data = {"url":url, "login":login,
                    "password":password, "comment":comment}
            for key in data:
                if data[key] == '' and key != "comment":
                    print("Поле '{0}' не может содержать пустое значение!".format(key))
                    run = 1
                    break
                else:
                    run = 0
                    continue
        for key in data:
            data[key] = self.crypt.rsa_encode(data[key], self.pubkey)
            print(data[key])
        return data


    def insert(self):
        con = sqlite3.connect(self.name)
        cur = con.cursor()
        data = self.get_data()
        print(data)
        insert_sql = """\
        INSERT INTO passwords (url, login, password, comment)
        VALUES (:url, :login, :password, :comment);"""
        try:
            cur.execute(insert_sql, data)
        except sqlite3.DatabaseError as err:
            print("Ошибка:", err)
        else:
            print("""
------------------------            
Запрос успешно выполнен
------------------------""")
            con.commit()
        cur.close()
        con.close()
        self.current_db(self.name)

    def update(self):
        print("Введите id строки для изменения значений:")
        try:
            id = int(input("->"))
        except ValueError as err:
            print("Ошибка ввода", err)
        data = self.get_data()
        data["id"] = id
        update_sql="""
        UPDATE passwords SET url=(:url), login=(:login), password=(:password), comment=(:comment)
        WHERE id=(:id)"""
        con = sqlite3.connect(self.name)
        cur = con.cursor()
        try:
            cur.execute(update_sql, data)
        except sqlite3.DatabaseError as err:
            print("Ошибка", err)
        else:
            print("""
------------------------            
Запрос успешно выполнен
------------------------""")
            con.commit()
        cur.close()
        con.close()
        self.current_db(self.name)


    def read(self, id=None):
        con = sqlite3.connect(self.name)
        cur = con.cursor()
        try:
            if id:
                cur.execute("SELECT * FROM passwords WHERE id=?;", (id,))
            else:
                cur.execute("SELECT id, url FROM passwords;")
        except sqlite3.DatabaseError as err:
            print("Ошибка", err)
        else:
            print("""\
------------------------            
запрос успешно выполнен
------------------------""")
        all = cur.fetchall()
        for i in all:
            print(i[0], end=" ")
            for j in i[1:]:
                print(self.crypt.rsa_decode(j, self.privkey), end=" ")
            print("\n")
        input()
        self.current_db(self.name)

    def current_db(self, name):
        self.name = name
        self.primage = "priv_" + self.name[:-3] + ".png"
        self.pubimage = "pub_" + self.name[:-3] + ".png"
        if not os.path.exists(self.name):
            print("Отсутствует база данных  с таким именем")
            main()
        elif not os.path.exists(self.primage) or \
            not os.path.exists(self.pubimage):
            print("Отсутствуют файлы с ключами")
            main()
        self.privkey = rsa.PrivateKey.load_pkcs1(self.dec.decode(self.primage))
        self.pubkey = rsa.PublicKey.load_pkcs1(self.dec.decode(self.pubimage))
        print("""
\n
--------------------
 База данных:      
 {0}
1->Список сайтов      
2->Запрос по id        
3->Новая запись        
4->Корректировка по id
5->Назад
->Enter для выхода<-""".format(self.name))
        try:
            mode = int(input("->"))
        except ValueError:
            sys.exit()
        if mode == 1:
            self.read()
        elif mode ==2:
            print("Введите номер id:")
            id = int(input("->"))
            self.read(id)
        elif mode == 3:
            self.insert()
        elif mode == 4:
            self.update()
        elif mode == 5:
            main()

def main():
    db = db_editor()

    print("""
Выберите необходимый пункт меню: 
1->Открыть базу данных           
2->Создать базу данных
->Enter для выхода<-""")
    try:
        mode = int(input('->'))
    except ValueError:
        sys.exit()
    db_name = input("Введите название бд: ")
    if mode == 1:
        db.current_db(db_name)
    elif mode ==2:
        db.create_db(db_name)


if __name__ == '__main__' :

    main()
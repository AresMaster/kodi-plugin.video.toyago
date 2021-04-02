# -*- coding: utf-8 -*-

import sqlite3


class Create:
    def __init__(self, db):
        self.conn = sqlite3.connect(db + '.db')
        self.cursor = self.conn.cursor()

    def drop(self, table):
        try:
            self.cursor.execute('DROP TABLE ' + table)
            return True
        except sqlite3.OperationalError:
            return False

    def create(self, table, columns, ifNotExist):
        cols = '(id TEXT'
        for column in columns:
            cols += ', ' + column
        cols += ')'
        sql = 'CREATE TABLE '
        if ifNotExist:
            sql += 'IF NOT EXISTS '
        sql += table + ' ' + cols
        print(sql)
        self.cursor.execute(sql)

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

    def findone(self, table, field, value):
        sql = 'SELECT * FROM ' + table + ' WHERE ' + field + '=?'
        self.cursor.execute(sql, (value,))
        return self.cursor.fetchone()

    def custom(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def customdel(self, sql):
        self.cursor.execute(sql)

    def findall(self, table):
        self.cursor.execute('SELECT * FROM ' + table)
        return self.cursor.fetchall()

    def findallOrderBy(self, table, order):
        self.cursor.execute('SELECT * FROM ' + table + ' ORDER BY ' + order)
        return self.cursor.fetchall()

    def deleteall(self, table):
        self.cursor.execute('DELETE FROM ' + table)

    def delteby(self, table, name, value):
        self.cursor.execute('DELETE FROM ' + table + ' WHERE ' + str(name) + ' = ' + str(value))

    def saveall(self, table, values, size):
        cols = '(?'
        for col in range(size - 1):
            cols += ',?'
        cols += ')'
        print(cols)
        self.cursor.executemany('INSERT INTO ' + table + ' VALUES ' + cols, values)

    def save(self, table, value, size):
        values = []
        values.append(value)
        self.saveall(table, values, size)

    def update(self, table, update, fields, keyname, keyvalue):
        sql = 'UPDATE ' + table + ' SET '
        first = True
        for field in fields:
            if first:
                sql += field + ' = ? '
                first = False
            else:
                sql += ', ' + field + ' = ? '
        sql += 'WHERE ' + keyname + ' = ' + keyvalue
        # print(sql)
        self.cursor.execute(sql, update)


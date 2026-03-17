import sqlite3
import re

class CursorMock:
    def __init__(self, cursor):
        self.cursor = cursor
        self._results = None
        self._idx = 0
        self._rowcount = -1

    def execute(self, query, args=None):
        sqlite_query = query.replace('%s', '?')
        if args is not None:
            if not isinstance(args, (tuple, list)):
                args = (args,)
            self.cursor.execute(sqlite_query, args)
        else:
            self.cursor.execute(sqlite_query)
        
        # Emulate MySQL rowcount for SELECT
        if query.strip().upper().startswith('SELECT'):
            self._results = self.cursor.fetchall()
            self._idx = 0
            self._rowcount = len(self._results)
        else:
            self._results = None
            self._rowcount = self.cursor.rowcount

    def fetchall(self):
        if self._results is not None:
            res = self._results[self._idx:]
            self._idx = len(self._results)
            return res
        return self.cursor.fetchall()

    def fetchone(self):
        if self._results is not None:
            if self._idx < len(self._results):
                res = self._results[self._idx]
                self._idx += 1
                return res
            return None
        return self.cursor.fetchone()
        
    def fetchmany(self, size):
        if self._results is not None:
            res = self._results[self._idx:self._idx+size]
            self._idx = min(len(self._results), self._idx + size)
            return res
        return self.cursor.fetchmany(size)

    @property
    def rowcount(self):
        return self._rowcount
        
    @property
    def lastrowid(self):
        return self.cursor.lastrowid
        
    def close(self):
        self.cursor.close()

class ConnectionMock:
    def __init__(self):
        # Using check_same_thread=False since Flask can share connections across threads in dev
        self.conn = sqlite3.connect('examportal.db', check_same_thread=False)
        self.conn.row_factory = self.dict_factory
        
    def dict_factory(self, cursor, row):
        d = {}
        for idx, col in enumerate(cursor.description):
            d[col[0]] = row[idx]
        return d

    def cursor(self, *args, **kwargs):
        return CursorMock(self.conn.cursor())

    def commit(self):
        self.conn.commit()

    def close(self):
        self.conn.close()

class MySQL:
    def __init__(self, app=None):
        self.app = app
        self._conn = None

    def init_app(self, app):
        self.app = app

    @property
    def connection(self):
        if self._conn is None:
            self._conn = ConnectionMock()
        return self._conn

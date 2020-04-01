import pymysql

class MysqlClass():
    conn = None
    cursor = None
    def __init__(self):
        print("creating mysql class ...")

    def connectDB(self):
        self.conn = pymysql.connect(
            host="127.0.0.1",
            user ="root",
            password ="mysql",
            database ="math_question",
            charset ="utf8"
        )
        self.cursor = self.conn.cursor()
    def selectQbyCpid(self,cp_id):
        sql = "SELECT id,node_id,cp_id,q_stem,choice,answer FROM ques WHERE cp_id=%s" % cp_id
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    #插入数据
    def insertDB(self, sql, data):
        self.cursor.executemany(sql, data)
        self.conn.commit()

    #查询数据并返回全部数据
    def selectDB(self, sql):
        self.cursor.execute(sql)
        return self.cursor.fetchall()

    def closeCursor(self):
        self.cursor.close()

    def closeDB(self):
        self.conn.close()

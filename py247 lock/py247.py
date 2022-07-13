from threading import Thread

from vMysql import MysqlProxy
from time import sleep

db = MysqlProxy()

rst = []
rsts = []

class F(Thread):
    def __init__ (this, no):
        super().__init__()
        this.no = no
        this.paused = True
        this.ready = False
        this.done = False
    def run (this):
        global rst
        print (f'{this.no} starts')
        db = MysqlProxy()
        db('''select * from temp_db.shenzhen_ent for update;''')
        
        print (f'{this.no} is ready')
        this.ready = True
        while this.paused: pass
        db.commit()
        
        rst.append(this.no)
        print (f'{this.no} is done')
        this.done = True
        db.close()
        
        
a =F(1)
b =F(2)
c =F(3)

i = 1
a.start()
while not a.ready:
    print(i)
    i += 1
b.start()
while not b.ready: pass
c.start()

while not c.ready: pass
a.paused = False

while not a.done: pass
b.paused = False

while not b.done: pass
c.paused = False

print (rst)
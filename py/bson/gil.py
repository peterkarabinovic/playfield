def count(n):
    while n > 0:
        n -= 1

def run():
    count(1000*1000*10)
    count(1000*1000*10)



def run2():
    from threading import Thread
    t1 = Thread(target=count,args=(1000*1000*100,))
    t1.start()
    t2 = Thread(target=count,args=(1000*1000*100,))
    t2.start()
    t1.join(); t2.join()



raw_input('beefore run')
run()
raw_input('beefore run2')
run2()
raw_input('after run2')

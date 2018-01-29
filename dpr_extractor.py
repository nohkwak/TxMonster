import urllib.parse
import urllib.request
import re
import json
import time
import pymysql

start_time = time.time()

blockinfo_time = 0
dbread_time = 0
dbwrite_time = 0

depth = 0
count = 0
limit = 2


db = pymysql.connect("localhost","root","1234","txmondb" )

def fetch_contents_from_url( addr, index ):
    global blockinfo_time

    time.sleep(1) # time delay for blockchain.info's policy
    strt_time = time.time()
    #url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=be706ad0-9f27-4230-84ba-d603528ffde3&offset=" + str(index*50) #세진이꺼
    url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=d85f8488-474d-4bc6-9228-8e001512f4fc&offset=" + str(index*50) #노현이 형꺼
    res = urllib.request.urlopen(url)
    res_body = res.read()
    data = json.loads(res_body.decode("utf-8"))
    blockinfo_time += time.time() - strt_time
    return data

def insert_dpr_list(addr, depth):
    global dbwrite_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "INSERT INTO dpr_lists(addr, depth) VALUES ('%s', '%s')" % (addr, depth)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()
    dbwrite_time += time.time() - strt_time

def insert_dpr_time_list(addr, tx_date, tx_month):
    global dbwrite_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "INSERT INTO dpr_time_lists(addr, tx_date, tx_month) VALUES ('%s', '%s', '%s')" % (addr, tx_date, tx_month)
    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()
    dbwrite_time += time.time() - strt_time


def exist_dpr_list(addr):
    global dbread_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "SELECT addr FROM dpr_lists WHERE addr = '" + addr + "'"
    try:
        # Execute the SQL command
        row_count = cursor.execute(sql)
        dbread_time += time.time() - strt_time
        if row_count > 0:
            return True
        else:
            return False
    except:
       print( "DB error" )


def get_addr_list( addr, index ):
    data = fetch_contents_from_url( addr, index )
    global depth
    global count
    global limit
    #depth = depth + 1

    if ( data["n_tx"] - index * 50 < 50 ) :
        itr = data["n_tx"] % 50
    else:
        itr = 50

    for i in range( itr ) :
        for j in range( data["txs"][i]["vout_sz"] ) :
            if ( data["txs"][i]["out"][j].get("addr", None) == addr ):
                for k in range(data["txs"][i]["vin_sz"]):
                    print ("( %d, %d, %d)," %(i,j,k) )
                    if ( exist_dpr_list( data["txs"][i]["inputs"][k]["prev_out"]["addr"] ) == False):
                        print( 'added ' + data["txs"][i]["inputs"][k]["prev_out"]["addr"] + ", %d\n" %depth )
                        # insert_dpr_list( data["txs"][i]["inputs"][k]["prev_out"]["addr"], depth)
                        insert_dpr_time_list( data["txs"][i]["inputs"][k]["prev_out"]["addr"],
                        datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y-%m-%d'),
                        datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y%m') )


def get_hundred_list( addr ):
    data = fetch_contents_from_url( addr, 0 )
    for i in range(int( data["n_tx"]/50 + 1 )):
        print ("=============index============= %d" %i)
        get_addr_list( addr, i )


#DPR Seized coins
addr="1FfmbHfnpaZjKFvyi1okTjJJusN455paPH"

get_hundred_list( addr )

db.close()

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
ntx=100


db = pymysql.connect("localhost","root","1234","TxMonDB" )

def fetch_contents_from_url( addr, index ):
    global blockinfo_time

    time.sleep(1) # time delay for blockchain.info's policy
    strt_time = time.time()
    url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=be706ad0-9f27-4230-84ba-d603528ffde3&offset=" + str(index*50) #세지니꺼
        #url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=d85f8488-474d-4bc6-9228-8e001512f4fc&offset=" + str(index*50) #노현이 형꺼
    res = urllib.request.urlopen(url)
    res_body = res.read()
    data = json.loads(res_body.decode("utf-8"))
    blockinfo_time += time.time() - strt_time
    return data

def insert_blacklist(addr, depth):
    global dbwrite_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "INSERT INTO black_lists(addr,depth) VALUES ('%s', '%s')" % (addr, depth)

    try:
       # Execute the SQL command
       cursor.execute(sql)
       # Commit your changes in the database
       db.commit()
    except:
       # Rollback in case there is any error
       db.rollback()
    dbwrite_time += time.time() - strt_time

def exist_blacklist(addr):
    global dbread_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "SELECT addr FROM black_lists WHERE addr = '" + addr + "'"
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
    #print( "-------------------------")
    #print( "request for %s" %addr)
    data = fetch_contents_from_url( addr, index )
    global depth
    global count
    global limit
    global blockinfo_time
    global dbread_time
    global dbwrite_time
    global ntx

    depth = depth + 1

    if ( data["n_tx"] - index * 50 < 50 ) :
        itr = data["n_tx"] % 50
    else:
        itr = 50

    for i in range( itr ) :
        for j in range( data["txs"][i]["vin_sz"] ) :
            if (  data["txs"][i]["inputs"][j]["prev_out"].get( "addr", None) == addr ):
                for k in range(data["txs"][i]["vout_sz"]):
                    print ("( %d, %d, %d)," %(i,j,k) )
                    if ( depth + 1 < limit ) :
                        get_hundred_list(data["txs"][i]["out"][k]["addr"])
                    if ((int( data["n_tx"])>ntx) and data["txs"][i]["out"][k].get("addr", False) and exist_blacklist( data["txs"][i]["out"][k].get("addr", "") ) == False):
                        print( 'added ' + data["txs"][i]["out"][k]["addr"] + ", %d\n" %depth )
                        insert_blacklist( data["txs"][i]["out"][k]["addr"], depth)
                    else:
                        print('No added')

    depth = depth - 1

def get_hundred_list( addr):
    data = fetch_contents_from_url( addr, 0 )
    for i in range(int( data["n_tx"]/50 + 1 )):
        print("---------------------------------------------")
        print("addr=%s, i=%d" %(addr, i))
        get_addr_list( addr, i )

# dpr_user_list에서 address 읽어온 후 각 address로부터 1depth씩 추출
def extract_from_dpr_user_list():
    global dbread_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "SELECT addr FROM dpr_user_lists"
    # sql = "SELECT addr FROM black_lists WHERE depth = 2"
    try:
        # Execute the SQL command
        row_count = cursor.execute(sql)
        result_set = cursor.fetchall()
        dbread_time += time.time() - strt_time
        if row_count > 0:
            print ("Success in DPR User List")
            return result_set
        else:
            print( "Problem: No DPR User" )
            return False
    except:
       print( "DB error" )

def extract_from_dpr_list():
    global dbread_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "SELECT addr FROM dpr_lists" # FROM black_lists WHERE depth = 2"
    try:
        # Execute the SQL command
        row_count = cursor.execute(sql)
        result_set = cursor.fetchall()
        dbread_time += time.time() - strt_time
        if row_count > 0:
            print ("Success in DPR List")
            return result_set
        else:
            print( "Problem: No DPR" )
            return False
    except:
       print( "DB error" )

#dpr list를 출력
result = extract_from_dpr_list()
for row in result:
    addr = row[0]
    print( addr )
    insert_blacklist( addr, 0)

#dpr user list를 출력
result = extract_from_dpr_user_list()
for row in result:
    addr = row[0]
    print( addr )
    insert_blacklist( addr, 0)
    get_hundred_list( addr )


print( "-------------------------")
print("Depth : %s" %limit)
print( "total : %s" %count)
print( "total time : %s seconds" %(time.time()-start_time) )
print( "blockinfo time : %s seconds" %(blockinfo_time) )
print( "DB read time : %s seconds" %(dbread_time) )
print( "DB write time : %s seconds" %(dbwrite_time) )

# disconnect from server
db.close()

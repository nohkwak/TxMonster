import urllib.parse
import urllib.request
import re
import json
import time
import datetime
import pymysql

start_time = time.time()

blockinfo_time = 0
dbread_time = 0
dbwrite_time = 0

depth = 0
count = 0
limit = 2


db = pymysql.connect("localhost","root","1234","TxMonDB" )

def fetch_contents_from_url( addr, index ):
    global blockinfo_time

    time.sleep(3) # time delay for blockchain.info's policy
    strt_time = time.time()
    #url = "https://blockchain.info/ko/rawaddr/" + addr + str(index*50)
    url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=be706ad0-9f27-4230-84ba-d603528ffde3&offset=" + str(index*50) #세진이꺼
    #url = "https://blockchain.info/ko/rawaddr/" + addr + "?key=d85f8488-474d-4bc6-9228-8e001512f4fc&offset=" + str(index*50) #노현이 형꺼
    res = urllib.request.urlopen(url)
    res_body = res.read()
    print( url )
    print( res )
    data = json.loads(res_body.decode("utf-8"))
    blockinfo_time += time.time() - strt_time
    return data

def insert_dpr_user_txs(sender, receiver, tx_time, tx_month, BTC, typo):
    global dbwrite_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.

    sql = "INSERT INTO dpr_user_txs(sender, receiver, tx_time, tx_month, BTC, typo) VALUES ('%s', '%s','%s', '%s','%s','%s')" % (sender, receiver, tx_time, tx_month, BTC, typo)
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
       print( "DB error in exist_dpr_list" )

def exist_already( sender, receiver, tx_time ):
    #global dbread_time

    #strt_time = time.time()
    # prepare a cursor object using cudrsor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "SELECT * FROM dpr_user_txs WHERE sender = '" + sender + "' and receiver = '" + receiver + "' and tx_time = '" + tx_time + "'"
    #print(sql)
    try:
        # Execute the SQL command
        row_count = cursor.execute( sql )
        #dbread_time += time.time() - strt_time
        if row_count > 0:
            return True
        else:
            return False
    except:
       print( "DB error in exist_already" )


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
        if ( data["txs"][i]["vin_sz"] < 100 and data["txs"][i]["vout_sz"] < 100 ):
            for j in range( data["txs"][i]["vin_sz"] ) :
                if ( data["txs"][i]["inputs"][j].get("prev_out", False) == False ) :
                    continue
                elif ( data["txs"][i]["inputs"][j]["prev_out"].get("addr", False) == addr ):
                    for k in range(data["txs"][i]["vout_sz"]):
                        print ("( tx: %d, in: %d/%d, out: %d/%d)," %(i,j, data["txs"][i]["vin_sz"], k, data["txs"][i]["vout_sz"]) )

                        #2011.2월 Silkroad가 설립되었으므로 이후의 거래만 출력함
                        if (int(data["txs"][i]["time"]) > 1296486000) :
                            #print(int(data["txs"][i]["time"]))

                            #keyerror:'addr' 예외처리를 위해 if문 추가
                            if ( data["txs"][i]["out"][k].get("addr", False) == False) :
                                print( "no addr" )
                                continue

                            elif ( exist_already( data["txs"][i]["inputs"][j]["prev_out"]["addr"] , data["txs"][i]["out"][k]["addr"] ,
                            datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y-%m-%d %H:%M:%S') ) == True ):
                                print( "already exist")
                                continue

                            #dpr_list에 addr이 있으면 DPR로 분류하여 리스트에 넣는다.
                            elif (exist_dpr_list( data["txs"][i]["out"][k]["addr"] ) == True):
                                print( 'DPR added ' +  data["txs"][i]["out"][k]["addr"] )
                                insert_dpr_user_txs( data["txs"][i]["inputs"][j]["prev_out"]["addr"], data["txs"][i]["out"][k]["addr"],
                                datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y-%m-%d %H:%M:%S'),
                                datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y-%m'),
                                data["txs"][i]["out"][k]["value"]/10**8, 'DPR')

                            #dpr_list에 addr이 없으면 Candidate로 분류하여 리스트에 넣는다.
                            #FBI addr=1FfmbHfnpaZjKFvyi1okTjJJusN455paPH은 제외함
                            elif (data["txs"][i]["out"][k].get("addr")!='1FfmbHfnpaZjKFvyi1okTjJJusN455paPH') :
                                print( 'Candidate added ' +  data["txs"][i]["out"][k]["addr"] )
                                insert_dpr_user_txs( data["txs"][i]["inputs"][j]["prev_out"]["addr"], data["txs"][i]["out"][k]["addr"],
                                datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y-%m-%d %H:%M:%S'),
                                datetime.datetime.fromtimestamp(int(data["txs"][i]["time"])).strftime('%Y-%m'),
                                data["txs"][i]["out"][k]["value"]/10**8, 'CANDIDATE')

                            else:
                                continue


def get_hundred_list( addr ):
    data = fetch_contents_from_url( addr, 0 )

    #실크로드가 2011.2월에 서비스 시작하였음. 정상적인 사용자라면 매일 최대 10건의 트랙잭션을 발생하였다고 가정하여 10*365*7년=25,550개로 리밋함
    if ( data["n_tx"] >= 25550 ):
        return

    for i in range(int( data["n_tx"]/50 + 1 )):
        if (i<96) :
            continue
        print("---------------------------------------------")
        print("addr=%s, i=%d" %(addr, i))
        get_addr_list( addr, i )

# dpr_lists 테이블에서 dpr address 읽어온 후 각 address로부터 user를 추출
def extract_from_dpr_user_list():
    global dbread_time

    strt_time = time.time()
    # prepare a cursor object using cursor() method
    cursor = db.cursor()

    # Drop table if it already exist using execute() method.
    sql = "SELECT addr FROM dpr_user_lists WHERE ID>10000" # addr=1NdB1z2qkAhMpWVn67pnFVYrwmFkZ9vjm2
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


result = extract_from_dpr_user_list()
for row in result:
    addr = row[0]
    print("===========================")
    print( addr )
    #insert_dpr_user_lists( addr, 0)
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

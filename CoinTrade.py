import time
import pyupbit
import datetime
import telegram as tel
import threading

bot = tel.Bot(token='5152255815:AAHFRx5Ifc4pkNsL7u_pkaPqXHdofZiAPHk')
chat_id = 5299678383


access = "oR3orWoHQ0y4VneqxMnVgsL8kzxH3gdm95WSdEZh"
secret = "1zU50z4bL0cpQxxd5G3HPXN9wUQEosp4zlr2VL9Y"

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_ma5(ticker):
    """5일 이동 평균선 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=5)
    ma5 = df['close'].rolling(5).mean().iloc[-1]
    return ma5



def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

def test_alive():
    bot.sendMessage(chat_id=chat_id, text="AutoTrading running good!!") 

otc = 'otc'
sp = 'sp'
cnt = 'cnt'
fsticker = 'fsticker'
ftk = 'ftk'
idx = 'idx'
MoneyA = 0
MoneyB = 0

tickers = pyupbit.get_tickers(fiat="KRW")



ptickers = []
stickers = []
noises = []
volumes = []
ptA = []
ptB = []
pts = []
reset = []

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("TRADE START")  

if cnt is cnt:
    cnt = 0

threading.Timer(21600,test_alive).start()
test_alive()

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)
        

        if start_time < now < start_time + datetime.timedelta(seconds=3590):
            MoneyA = get_balance("KRW")
            if get_balance("KRW") > 5000 and cnt == 0:
                    ptickers = []
                    stickers = []
                    volumes = []
                    
                    for ticker in tickers:
                        tk = ticker.split("-")
                        ma5 = get_ma5(ticker)
                        current_price = get_current_price(ticker)
                        if current_price > 500 and current_price < 100000:
                            target_price = get_target_price(ticker,0.2)
                        elif current_price > 10 and current_price < 500:
                            target_price = get_target_price(ticker,0.5)
                        else: 
                            target_price = 1
                            
                        btc = get_balance(tk[1])
                        if otc is otc:
                            if btc < 5000/current_price:
                                otc = 0
                        if sp is sp :
                            if btc < 5000/current_price:
                                sp = 0

                        if target_price < current_price and current_price / target_price < 1.01 and target_price > 100 and target_price < 100000:
                            ptickers.append(ticker)
                            stickers.append(tk[1])
                        

                    for pticker in ptickers:
                        atc = pyupbit.get_ohlcv(pticker,interval="minute5",count=2)
                        time.sleep(0.2)
                        volume = atc['volume']
                        volumes.append((volume[0]+volume[1])/2)
                    print(ptickers)
                    print(volumes)

                    if len(ptickers) > 1 :
                        idx = volumes.index(max(volumes))
                        fsticker = ptickers[idx]
                        ftk = stickers[idx]
                        cnt = 1                 
                    print(fsticker)
                    
            if cnt == 1:
                current_price = get_current_price(fsticker)
                if current_price > 500 and current_price < 100000:
                    target_price = get_target_price(fsticker,0.2)
                elif current_price > 10 and current_price < 500:
                    target_price = get_target_price(fsticker,0.5)
                else: 
                    target_price = 1
                
    
                if target_price < current_price and current_price / target_price < 1.015 :
                    krw = get_balance("KRW")
                    if krw > 5000:
                        upbit.buy_market_order(fsticker, krw*0.9995)
                        btc = get_balance(ftk)
                        otc = btc
                        sp = btc
                        bot.sendMessage(chat_id=chat_id, text="종목 조건 검색 결과 :") 
                        bot.sendMessage(chat_id=chat_id, text=ptickers)
                        bot.sendMessage(chat_id=chat_id, text="종목 거래량 결과 :")
                        bot.sendMessage(chat_id=chat_id, text=volumes)
                        bot.sendMessage(chat_id=chat_id, text="최종 선택 종목 :")
                        bot.sendMessage(chat_id=chat_id, text=fsticker)
                
                #매도를 한번도 하지 않았고, 3% 이익일 경우 50% 매도
                if btc == otc and current_price / target_price >= 1.04:
                    sp = otc / 2
                    otc = otc / 2
                    if sp > 5000 / current_price:
                        upbit.sell_market_order(fsticker,sp)
                        bot.sendMessage(chat_id=chat_id, text="★★★★ 반, 3% 익절 ★★★★") 
                # 8% 이익일 경우 나머지 50% 매도
                if sp == otc and current_price / target_price >= 1.06:
                    sp = otc
                    if sp > 5000 / current_price:
                        upbit.sell_market_order(fsticker,sp)
                        bot.sendMessage(chat_id=chat_id, text="★★★★ 나머지 반, 6% 익절 ★★★★") 
            

                # Target Price 대비 1.5% 손해일 경우 전량 손절
                if current_price / target_price <= 0.99:
                    if btc > 5000 / current_price:
                        upbit.sell_market_order(fsticker,btc)
                        cnt = 0
                        bot.sendMessage(chat_id=chat_id, text="▩▩▩▩ 1.5프로 손절 ▩▩▩▩") 

                if krw > 5000:
                    cnt = 0
                
        #10시 30초전에 전량 매도
        elif start_time + datetime.timedelta(seconds=3570) < now < start_time + datetime.timedelta(seconds=3600) :
            btc = get_balance(ftk)
            if btc > 5000 / current_price:
                upbit.sell_market_order(fsticker, btc)
                cnt = 0
        #10시부터 매매방식 변경
        elif start_time + datetime.timedelta(seconds=3600) < now < end_time - datetime.timedelta(seconds=10):
            if get_balance("KRW") > 5000 and cnt == 0:
                    MoneyA = get_balance("KRW")
                    print(MoneyA)
                    ptickers = []
                    stickers = []
                    noises = []
                    volumes = []
                    ptA = []
                    ptB = []
                    pts = []
                    
                    for rest in reset:
                        if rest in tickers:
                            tickers.remove(rest)
                            print("Remove")

                    for ticker in tickers:
                        tk = ticker.split("-")
                        ma5 = get_ma5(ticker)
                        current_price = get_current_price(ticker)
                        if current_price > 500 and current_price < 100000:
                            target_price = get_target_price(ticker,0.3)
                        elif current_price > 10 and current_price < 500:
                            target_price = get_target_price(ticker,0.6)
                        else: 
                            target_price = 1

                        btc = get_balance(tk[1])
                        if target_price < current_price and current_price / target_price < 1.005 and current_price > ma5 and target_price > 50 and target_price < 100000:
                            ptickers.append(ticker)
                            stickers.append(tk[1])
            
                    for pticker in ptickers:
                        atc = pyupbit.get_ohlcv(pticker,count=4)
                        atv = pyupbit.get_ohlcv(pticker,interval="minute60",count=2)
                        time.sleep(0.2)
                        noise = 1-abs(atc['open']-atc['close'])/abs(atc['high']-atc['low'])
                        volume = atv['volume']
                        noises.append((noise[1]+noise[2]+noise[3])/3)
                        volumes.append(volume[1])
                    

                    for noise in noises:
                        ptA.append(abs(1-abs(0.01-noise)/len(noises))*100*0.98)

                    for volume in volumes:
                        ptB.append(volume/max(volumes)*100*0.02)

                    for number in range(len(ptA)):
                        pts.append(ptA[number]+ptB[number])

                    if len(ptickers) > 1 :
                        idx = pts.index(max(pts))
                        fsticker = ptickers[idx]
                        ftk = stickers[idx]
                        cnt = 1
                        bot.sendMessage(chat_id=chat_id, text="종목 조건 검색 결과 :") 
                        bot.sendMessage(chat_id=chat_id, text=ptickers)
                        bot.sendMessage(chat_id=chat_id, text="종목 Noise 점수 결과 :")
                        bot.sendMessage(chat_id=chat_id, text=ptA)
                        bot.sendMessage(chat_id=chat_id, text="종목 거래량 점수 결과 :")
                        bot.sendMessage(chat_id=chat_id, text=ptB)
                        bot.sendMessage(chat_id=chat_id, text="종목 총 점수 결과 :") 
                        bot.sendMessage(chat_id=chat_id, text=pts)
                        bot.sendMessage(chat_id=chat_id, text="최종 선택 종목 :")
                        bot.sendMessage(chat_id=chat_id, text=fsticker)
                    print(ptickers)
                    print(fsticker)
            if cnt == 1:
                current_price = get_current_price(fsticker)
                if current_price > 500 and current_price < 100000:
                    target_price = get_target_price(fsticker,0.3)
                elif current_price > 10 and current_price < 500:
                    target_price = get_target_price(fsticker,0.6)
                else: 
                    target_price = 1
                btc = get_balance(ftk)
                
                
                if target_price < current_price:
                    if target_price > 5000:
                        if current_price / target_price <= 1.002:
                            krw = get_balance("KRW")
                            if krw > 5000:
                                upbit.buy_market_order(fsticker, krw*0.9995)
                                bot.sendMessage(chat_id=chat_id, text="현재 가격 :") 
                                bot.sendMessage(chat_id=chat_id, text=current_price)
                                bot.sendMessage(chat_id=chat_id, text="목표 매수 가격 :")
                                bot.sendMessage(chat_id=chat_id, text=target_price)
                                btc = get_balance(ftk)
                            
                                

                    elif 2000 < target_price < 5000:
                        if current_price / target_price <= 1.003:
                            krw = get_balance("KRW")
                            if krw > 5000:
                                upbit.buy_market_order(fsticker, krw*0.9995)
                                bot.sendMessage(chat_id=chat_id, text="현재 가격 :") 
                                bot.sendMessage(chat_id=chat_id, text=current_price)
                                bot.sendMessage(chat_id=chat_id, text="목표 매수 가격 :")
                                bot.sendMessage(chat_id=chat_id, text=target_price)
                                btc = get_balance(ftk)

                    
                    elif 500 < target_price < 2000:
                        if current_price / target_price <= 1.005:
                            krw = get_balance("KRW")
                            if krw > 5000:
                                upbit.buy_market_order(fsticker, krw*0.9995)
                                bot.sendMessage(chat_id=chat_id, text="현재 가격 :") 
                                bot.sendMessage(chat_id=chat_id, text=current_price)
                                bot.sendMessage(chat_id=chat_id, text="목표 매수 가격 :")
                                bot.sendMessage(chat_id=chat_id, text=target_price)
                                btc = get_balance(ftk)

                    else:
                        if current_price / target_price <= 1.007:
                            krw = get_balance("KRW")
                            if krw > 5000:
                                upbit.buy_market_order(fsticker, krw*0.9995)
                                bot.sendMessage(chat_id=chat_id, text="현재 가격 :") 
                                bot.sendMessage(chat_id=chat_id, text=current_price)
                                bot.sendMessage(chat_id=chat_id, text="목표 매수 가격 :")
                                bot.sendMessage(chat_id=chat_id, text=target_price)
                                btc = get_balance(ftk)
        
                # 3% 이익일 경우 전량 매도
                if current_price / target_price >= 1.03:
                    if btc > 5000 / current_price:
                        upbit.sell_market_order(fsticker,btc)
                        reset.append(fsticker)
                        cnt = 0
                        MoneyB = get_balance("KRW")
                        bot.sendMessage(chat_id=chat_id, text="★★★★ 3% 익절 ★★★★") 
            
                # Target Price 대비 1% 손해일 경우 전량 손절
                if current_price / target_price <= 0.99:
                    print(current_price/target_price)
                if current_price / target_price <= 0.99:
                    if btc > 5000 / current_price:
                        upbit.sell_market_order(fsticker,btc)
                        cnt = 0
                        bot.sendMessage(chat_id=chat_id, text="▩▩▩▩ 1.5프로 손절 ▩▩▩▩") 
                        MoneyB = get_balance("KRW")

                if krw > 5000:
                    cnt = 0

        #종가에 전량 매도
        else:
            cnt = 0
            reset = []
            if btc > 5000 / current_price:
                upbit.sell_market_order(fsticker, btc)
                MoneyB = get_balance("KRW")
            bot.sendMessage(chat_id=chat_id, text="하루 결과 :")
            bot.sendMessage(chat_id=chat_id, text= MoneyB - MoneyA)
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)

import time
import pyupbit
import datetime

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

otc = 'otc'
sp = 'sp'
cnt = 'cnt'
fsticker = 'fsticker'
ftk = 'ftk'
idx = 'idx'

tickers = pyupbit.get_tickers(fiat="KRW")

ptickers = []
stickers = []
noises = []


# 로그인
upbit = pyupbit.Upbit(access, secret)
print("TRADE START")  

if cnt is cnt:
    cnt = 0


# 자동매매 시작
while True:
    try:
        if get_balance("KRW") > 5000 and cnt == 0:
                ptickers = []
                stickers = []
                noises = []
                for ticker in tickers:
                    tk = ticker.split("-")
                    ma5 = get_ma5(ticker)
                    target_price = get_target_price(ticker, 0.3)
                    current_price = get_current_price(ticker)
                    btc = get_balance(tk[1])
                    if target_price < current_price and current_price / target_price < 1.01 and current_price > ma5 and target_price > 50 and target_price < 100000:
                        ptickers.append(ticker)
                        stickers.append(tk[1])
                        ptickers.remove("KRW-MED")
                        ptickers.remove("KRW-MVL")
                        stickers.remove("MED")
                        stickers.remove("MVL")

                for pticker in ptickers:
                    atc = pyupbit.get_ohlcv(pticker,count=4)
                    noise = 1-abs(atc['open']-atc['close'])/abs(atc['high']-atc['low'])
                    noises.append((noise[1]+noise[2]+noise[3])/3)

                idx = noises.index(min(noises))
                fsticker = ptickers[idx]
                ftk = stickers[idx]
                cnt = 1                  

        now = datetime.datetime.now()
        start_time = get_start_time(fsticker)
        end_time = start_time + datetime.timedelta(days=1)

        if start_time + datetime.timedelta(seconds=3600) < now < end_time - datetime.timedelta(seconds=10) and cnt == 1:
            
            target_price = get_target_price(fsticker, 0.3)
            current_price = get_current_price(fsticker)
            btc = get_balance(ftk)
            if otc is otc:
                if btc < 5000/current_price:
                    otc = 0
        
            if sp is sp :
                if btc < 5000/current_price:
                    sp = 0
                        
            if target_price < current_price and current_price / target_price < 1.005:
                krw = get_balance("KRW")
                if krw > 5000:
                    upbit.buy_market_order(fsticker, krw*0.9995)
                    otc = get_balance(ftk)
            # 매도를 한번도 하지 않았고, 2% 이익일 경우 50% 매도
            if btc == otc and current_price / target_price >= 1.02:
                sp = otc / 2
                otc = otc / 2
                if sp > 5000 / current_price:
                    upbit.sell_market_order(fsticker,sp)

            # 4% 이익일 경우 나머지 50% 매도
            if current_price / target_price >= 1.04:
                    upbit.sell_market_order(fsticker, btc)
                    cnt = 0 
            
            # Target Price 대비 1.5% 손해일 경우 전량 손절
            if current_price / target_price <= 0.985:
                if btc > 5000 / current_price:
                    upbit.sell_market_order(fsticker,btc)
                    cnt = 0
        #종가에 전량 매도
        else:
            btc = get_balance(ftk)
            if btc > 5000 / current_price:
                upbit.sell_market_order(fsticker, btc)
                cnt = 0
        time.sleep(1)
    except Exception as e:
        print(e)
        time.sleep(1)
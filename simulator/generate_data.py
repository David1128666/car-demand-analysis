#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json, random, time
from datetime import datetime, timedelta

random.seed(42)
CAR_COUNT = 24
BRAND_COUNT = 5
USER_COUNT = 1000
BRAND_NAMES = ["比亚迪", "特斯拉", "宝马", "奔驰", "奥迪"]

BEHAVIOR_TYPES = [("browse",0.50),("search",0.25),("consult",0.15),("collect",0.10)]
CAR_TYPES = ["SUV","轿车","MPV","跑车","皮卡","面包车","猎装车"]
FUEL_TYPES = ["纯电动","插电混动","增程式","汽油","柴油","油电混动"]
REGION_IDS = list(range(1,35))
SEARCH_KEYWORDS = ["比亚迪汉","特斯拉Model 3","蔚来ES6","小鹏P7","理想ONE","宝马3系","奔驰C级","奥迪A4L","丰田凯美瑞","本田雅阁","大众帕萨特","马自达阿特兹","凯迪拉克CT5","沃尔沃S60","新能源汽车","纯电动SUV","插电混动","自动驾驶","续航1000公里","家用轿车","商务用车","性价比高","油耗低","空间大"]
CONSULT_TYPES = ["价格咨询","配置咨询","试驾预约","购车优惠","分期付款","售后服务"]
PRICE_CHANGE_REASONS = ["官降","促销活动","限时优惠","置换补贴","金融优惠","节日特惠","库存清仓"]
LOAN_TYPES = ["商业贷款","信用卡分期","汽车金融","银行直贷","融资租赁"]
LOAN_STATUSES = ["待审核","已批准","已拒绝","已放款","已还清"]

def gen_behavior(n=10000):
    print(f"生成 {n} 条用户行为...")
    out=[]
    for i in range(n):
        bt=random.choices([b[0] for b in BEHAVIOR_TYPES],weights=[b[1] for b in BEHAVIOR_TYPES])[0]
        t=datetime.now()-timedelta(days=random.randint(0,7),hours=random.randint(0,23),minutes=random.randint(0,59))
        bid=random.randint(1,BRAND_COUNT)
        out.append({"behavior_id":f"beh_{int(time.time()*1000000)+i}","user_id":f"user_{random.randint(1,USER_COUNT):04d}","car_id":random.randint(1,CAR_COUNT),"behavior_type":bt,"behavior_time":t.strftime("%Y-%m-%d %H:%M:%S"),"brand_id":bid,"brand_name":BRAND_NAMES[bid-1],"series_id":random.randint(1,50),"car_type":random.choice(CAR_TYPES),"fuel_type":random.choice(FUEL_TYPES),"price":round(random.uniform(8,35),1),"region_id":random.choice(REGION_IDS),"session_id":f"sess_{random.randint(100000,999999)}","search_keyword":random.choice(SEARCH_KEYWORDS) if bt in ("search","browse") else None})
    print(f"  -> {len(out)} 条")
    return out

def gen_search(n=10000):
    print(f"生成 {n} 条搜索...")
    out=[]
    for i in range(n):
        t=datetime.now()-timedelta(days=random.randint(0,7),hours=random.randint(0,23),minutes=random.randint(0,59))
        out.append({"search_id":f"sch_{int(time.time()*1000000)+i}","user_id":f"user_{random.randint(1,USER_COUNT):04d}","search_keyword":random.choice(SEARCH_KEYWORDS),"search_time":t.strftime("%Y-%m-%d %H:%M:%S"),"region_id":random.choice(REGION_IDS),"result_count":random.randint(10,200),"click_position":random.randint(0,9)})
    print(f"  -> {len(out)} 条")
    return out

def gen_consult(n=10000):
    print(f"生成 {n} 条咨询...")
    out=[]
    for i in range(n):
        t=datetime.now()-timedelta(days=random.randint(0,7),hours=random.randint(0,23),minutes=random.randint(0,59))
        out.append({"consult_id":f"con_{int(time.time()*1000000)+i}","user_id":f"user_{random.randint(1,USER_COUNT):04d}","car_id":random.randint(1,CAR_COUNT),"consult_time":t.strftime("%Y-%m-%d %H:%M:%S"),"consult_type":random.choice(CONSULT_TYPES),"region_id":random.choice(REGION_IDS),"has_phone":random.choice([True,False]),"followup_status":random.choice(["待跟进","已跟进","已完成","已放弃"])})
    print(f"  -> {len(out)} 条")
    return out

def gen_price_quote(n=10000):
    print(f"生成 {n} 条报价...")
    out=[]
    for i in range(n):
        t=datetime.now()-timedelta(days=random.randint(0,14),hours=random.randint(0,23),minutes=random.randint(0,59))
        bp=round(random.uniform(8,35),1)
        discount=round(random.uniform(0.82,0.98),2)
        bid=random.randint(1,BRAND_COUNT)
        car_type = random.choice(CAR_TYPES)
        promo = random.choice([None,f"限时优惠{random.randint(1,5)}万元",f"送{random.randint(1,3)}年保养",f"免购置税",f"金融贴息{random.randint(3,8)}千元"])
        out.append({"quote_id":f"quo_{int(time.time()*1000000)+i}","car_id":random.randint(1,CAR_COUNT),"brand_id":bid,"brand_name":BRAND_NAMES[bid-1],"series_id":random.randint(1,50),"car_type":car_type,"original_price":bp,"quoted_price":round(bp*discount,2),"discount_rate":discount,"price_change_reason":random.choice(PRICE_CHANGE_REASONS),"region_id":random.choice(REGION_IDS),"dealer_id":f"dealer_{random.randint(1,100):03d}","quote_time":t.strftime("%Y-%m-%d %H:%M:%S"),"validity_period":random.randint(7,30),"promotion_info":promo})
    print(f"  -> {len(out)} 条")
    return out

def gen_loan(n=10000):
    print(f"生成 {n} 条贷款...")
    out=[]
    for i in range(n):
        t=datetime.now()-timedelta(days=random.randint(0,7),hours=random.randint(0,23),minutes=random.randint(0,59))
        cp=round(random.uniform(10,30),1)
        dr=random.choice([0.2,0.3,0.4,0.5])
        lt=random.choice([12,24,36,48,60])
        out.append({"loan_id":f"lon_{int(time.time()*1000000)+i}","user_id":f"user_{random.randint(1,USER_COUNT):04d}","car_id":random.randint(1,CAR_COUNT),"brand_id":random.randint(1,BRAND_COUNT),"car_type":random.choice(CAR_TYPES),"loan_type":random.choice(LOAN_TYPES),"car_price":cp,"down_payment":round(cp*dr,2),"loan_amount":round(cp*(1-dr),2),"loan_term":lt,"interest_rate":round(random.uniform(3.5,8),2),"monthly_payment":round(cp*(1-dr)/lt*1.05,2),"region_id":random.choice(REGION_IDS),"credit_score":random.randint(350,850),"inquiry_time":t.strftime("%Y-%m-%d %H:%M:%S"),"loan_status":random.choice(LOAN_STATUSES),"has_insurance":random.choice([True,False]),"preferred_bank":random.choice(["工商银行","建设银行","中国银行","农业银行","招商银行","平安银行"]) if random.random()>0.3 else None})
    print(f"  -> {len(out)} 条")
    return out

def save_jsonl(data,filename):
    with open(filename,'w',encoding='utf-8') as f:
        for item in data:
            f.write(json.dumps(item,ensure_ascii=False)+'\n')
    print(f"Saved {filename}")

def main():
    print("="*60)
    print("汽车需求数据分析 - 模拟数据生成器")
    print("="*60)
    import os
    od="D:/final project/simulator/data"
    os.makedirs(od,exist_ok=True)
    save_jsonl(gen_behavior(10000),f"{od}/car-user-behavior.json")
    save_jsonl(gen_search(10000),f"{od}/car-search.json")
    save_jsonl(gen_consult(10000),f"{od}/car-consult.json")
    save_jsonl(gen_price_quote(10000),f"{od}/car-price-quote.json")
    save_jsonl(gen_loan(10000),f"{od}/car-loan-inquiry.json")
    print("\nDone! 5 files in data/")

if __name__=="__main__":
    main()

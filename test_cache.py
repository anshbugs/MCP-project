import requests
import time
import json

extract_url = 'http://127.0.0.1:8000/extract-ticker'
query = {'query': 'how is INFY.NS doing?'}

print("=== RUN 1 (Cache Miss Expected) ===")
t0 = time.time()
res1 = requests.post(extract_url, json=query).json()
t1 = time.time()
print(f"[Extract] Time: {t1-t0:.3f}s | Ticker: {res1.get('ticker')}")

ticker = res1.get('ticker')
ana1 = {}
if ticker:
    ana_url = 'http://127.0.0.1:8000/analyze-stock'
    t2 = time.time()
    ana1 = requests.post(ana_url, json={'ticker': ticker}).json()
    t3 = time.time()
    print(f"[Analyze] Time: {t3-t2:.3f}s | Final Score: {ana1['scores']['final']} | Rec: {ana1['recommendation']}")

print("\n=== RUN 2 (Cache Hit Expected) ===")
t0 = time.time()
res2 = requests.post(extract_url, json=query).json()
t1 = time.time()
print(f"[Extract] Time: {t1-t0:.3f}s | Ticker: {res2.get('ticker')}")

if ticker:
    t2 = time.time()
    ana2 = requests.post(ana_url, json={'ticker': ticker}).json()
    t3 = time.time()
    print(f"[Analyze] Time: {t3-t2:.3f}s | Final Score: {ana2['scores']['final']} | Rec: {ana2['recommendation']}")
    
    print("\n=== VERIFICATION ===")
    match = (ana1['scores']['final'] == ana2['scores']['final'])
    speedup = (t3-t2) < 0.5 and (t1-t0) < 0.5
    print(f"Scores Identical?: {match}")
    print(f"Speed Optimization Successful?: {speedup}")

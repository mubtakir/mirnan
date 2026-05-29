import urllib.request, json, time

data=json.dumps({'prompt':'تخيل مدينة','max_words':10,'mode':'creative','dialogue':True}).encode('utf-8')
req=urllib.request.Request('http://127.0.0.1:8000/api/chat', data=data, headers={'Content-Type': 'application/json'})

t0 = time.time()
try:
    res = urllib.request.urlopen(req, timeout=120)
    print("STATUS:", res.getcode())
    print("TIME:", time.time() - t0)
    print("BODY:", res.read().decode())
except Exception as e:
    print("TIME:", time.time() - t0)
    print("ERROR:", str(e))

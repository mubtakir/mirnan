import urllib.request, json

data=json.dumps({'prompt':'تخيل مدينة','max_words':10,'mode':'creative','dialogue':True}).encode('utf-8')
req=urllib.request.Request('http://127.0.0.1:8000/api/chat', data=data, headers={'Content-Type': 'application/json'})

try:
    res = urllib.request.urlopen(req, timeout=10)
    print("STATUS:", res.getcode())
    print("BODY:", res.read().decode())
except Exception as e:
    print("ERROR:", str(e))

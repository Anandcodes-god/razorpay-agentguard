import httpx
r = httpx.post('http://127.0.0.1:8000/api/simulate/all', timeout=60)
print('Status:', r.status_code)
data = r.json()
print('Summary:', data.get('summary'))
for res in data.get('results', []):
    scen = res.get('scenario', {})
    print('[{}] {}: Expected={} Got={} Match={}'.format(scen.get('id'), scen.get('name'), scen.get('expected_decision'), res.get('actual_decision'), res.get('match')))
from fastapi.testclient import TestClient
from app.main import app, warnings_for

client = TestClient(app)

def test_healthz():
    assert client.get('/healthz').status_code == 200

def test_reject_non_pdf():
    r = client.post('/api/transcricoes', files={'arquivo': ('x.txt', b'abc', 'text/plain')}, data={'tipo': 'holerite'})
    assert r.status_code == 400

def test_invalid_type():
    r = client.post('/api/transcricoes', files={'arquivo': ('x.pdf', b'%PDF-1.4', 'application/pdf')}, data={'tipo': 'outro'})
    assert r.status_code == 400

def test_odd_punch_warning():
    value = {'pages':[{'page':1,'days':[{'date_raw':'01/09/2026','punches':[{'kind':'IN','time_raw':'08:00','time_hhmm':'08:00'}]}]}]}
    warnings = warnings_for(value, 'cartao-ponto')
    assert 'Batidas ímpares' in warnings[0]['reasons']

def test_holerite_month_sequence():
    value={'pages':[{'page':1,'year':'2026','month':'01','fields':[],'bases':[]},{'page':2,'year':'2026','month':'03','fields':[],'bases':[]}]}
    warnings=warnings_for(value,'holerite')
    assert 'Mês não sequencial' in warnings[1]['reasons']

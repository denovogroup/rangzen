import json
import requests
import subprocess
import time

url = "http://localhost:1337/"
dburl = "http://localhost:8529/_api/cursor"

db = None
server = None

def start_db():
  global db
  subprocess.call("mkdir temp_db_dir", shell=True)
  db = subprocess.Popen("exec arangod temp_db_dir", shell=True)

def kill_db():
  db.terminate()
  db.kill()
  subprocess.call("rm -rf temp_db_dir", shell=True)

def start_server():
  global server
  server = subprocess.Popen("exec node server.js", shell=True)

def kill_server():
  server.terminate()
  server.kill()

def test_reset_server():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

  # Register Alice.
  alice = {'phoneid': '123', 'friends': [ 'bob' ]}
  r = requests.post(url + "register_phone", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'

  reset = {} 
  r = requests.post(url + "reset", data=json.dumps(reset), headers=headers)
  assert r.json()['status'] == 'ok'

  # Re-Register Alice. This should work.
  alice = {'phoneid': '123', 'friends': [ 'bob' ]}
  r = requests.post(url + "register_phone", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
 
  # Leave server reset.
  reset = {} 
  r = requests.post(url + "reset", data=json.dumps(reset), headers=headers)
  assert r.json()['status'] == 'ok'


def test_register_phone():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

  # Register Alice.
  alice = {'phoneid': '123', 'friends': [ 'bob' ]}
  r = requests.post(url + "register_phone", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'

  # Register Bob.
  bob = {'phoneid': '456', 'friends': [ 'alice' ]}
  r = requests.post(url + "register_phone", data=json.dumps(bob), headers=headers)
  assert r.json()['status'] == 'ok'

  # Try to re-register Bob.
  r = requests.post(url + "register_phone", data=json.dumps(bob), headers=headers)
  assert r.json()['status'] == 'ok'


def test_get_friends():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

  # Get Alice's friends.
  alice = {'phoneid': '123'}
  r = requests.post(url + "get_friends", data=json.dumps(alice), headers=headers)
  alice_friends = r.json()['friends']
  assert 'bob' in alice_friends
  assert len(alice_friends) == 1

  # Get Bob's friends.
  bob = {'phoneid': '456'}
  r = requests.post(url + "get_friends", data=json.dumps(bob), headers=headers)
  bob_friends = r.json()['friends']
  assert 'alice' in bob_friends
  assert len(bob_friends) == 1


def test_update_locations():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

  # Check that Alice has no locations.
  alice = {'phoneid': '123'}
  r = requests.post(url + "get_previous_locations", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['locations']) == 0

  # Add a location for Alice.
  alice = {'phoneid': '123', 'locations': [ {'time': '1', 'latitude': '1.0', 'longitude': '1.0'} ] }
  r = requests.post(url + "update_locations", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'

  # Check that Alice's location is there.
  alice = {'phoneid': '123'}
  r = requests.post(url + "get_previous_locations", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['locations']) == 1
  assert r.json()['locations'][0]['time'] == '1'
  assert r.json()['locations'][0]['latitude'] == '1.0'
  assert r.json()['locations'][0]['longitude'] == '1.0'

  # Add another location for Alice.
  alice = {'phoneid': '123', 'locations': [ {'time': '2', 'latitude': '1.1', 'longitude': '1.1'} ] }
  r = requests.post(url + "update_locations", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'

  # Check that Alice's locations are there.
  r = requests.post(url + "get_previous_locations", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['locations']) == 2
  assert r.json()['locations'][0]['time'] == '1'
  assert r.json()['locations'][0]['latitude'] == '1.0'
  assert r.json()['locations'][0]['longitude'] == '1.0'
  assert r.json()['locations'][1]['time'] == '2'
  assert r.json()['locations'][1]['latitude'] == '1.1'
  assert r.json()['locations'][1]['longitude'] == '1.1'

  # Add a location for Bob.
  bob = {'phoneid': '456', 'locations': [ {'time': '3', 'latitude': '1.2', 'longitude': '1.2'} ] }
  r = requests.post(url + "update_locations", data=json.dumps(bob), headers=headers)
  assert r.json()['status'] == 'ok'

  # Check that Bob's location is there.
  bob = {'phoneid': '456'}
  r = requests.post(url + "get_previous_locations", data=json.dumps(bob), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['locations']) == 1
  assert r.json()['locations'][0]['time'] == '3'
  assert r.json()['locations'][0]['latitude'] == '1.2'
  assert r.json()['locations'][0]['longitude'] == '1.2'


def test_get_nearby_phones():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

  # Check that Alice has no neighbors.
  alice = {'phoneid': '123', 'distance': '1.0'}
  r = requests.post(url + "get_nearby_phones", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['phones']) == 0

  # Check that further out there are still no neighbors.
  alice = {'phoneid': '123', 'distance': '10.0'}
  r = requests.post(url + "get_nearby_phones", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['phones']) == 0

  # Check that Bob is eventually a neighbor.
  alice = {'phoneid': '123', 'distance': '100.0'}
  r = requests.post(url + "get_nearby_phones", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['phones']) == 1
  assert r.json()['phones'][0] == '456'
  

def test_update_exchange():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}

  # Check that Alice has no exchanges.
  alice = {'phoneid': '123'}
  r = requests.post(url + "get_previous_exchanges", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['exchanges']) == 0

  # Add an exchange for Alice with an unknown peer.
  alice = {'phoneid': '123', 'peer_phone_id': '999', 'protocol': 'bluetooth',
      'start_time': '1',
      'end_time': '2',
      'start_location': { 'time': '1', 'latitude': '1.0', 'longitude': '1.0' },
      'end_location': { 'time': '2', 'latitude': '1.0', 'longitude': '1.0' }}
  r = requests.post(url + "update_exchange", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'failed'

  # Add an exchange for Alice with a known peer.
  alice = {'phoneid': '123', 'peer_phone_id': '456', 'protocol': 'bluetooth',
      'start_time': '1',
      'end_time': '2',
      'start_location': { 'time': '1', 'latitude': '1.0', 'longitude': '1.0' },
      'end_location': { 'time': '2', 'latitude': '1.1', 'longitude': '1.1' }}
  r = requests.post(url + "update_exchange", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'

  # Check that Alice's exchange is there.
  alice = {'phoneid': '123'}
  r = requests.post(url + "get_previous_exchanges", data=json.dumps(alice), headers=headers)
  assert r.json()['status'] == 'ok'
  assert len(r.json()['exchanges']) == 1
  assert r.json()['exchanges'][0]['peer_phone_id'] == '456'
  assert r.json()['exchanges'][0]['protocol'] == 'bluetooth'
  assert r.json()['exchanges'][0]['start_location'] == {'time': '1', 'latitude': '1.0', 'longitude': '1.0'}
  assert r.json()['exchanges'][0]['end_location'] == {'time': '2', 'latitude': '1.1', 'longitude': '1.1'}


def test_database_contents():
  headers = {'Content-type': 'application/json', 'Accept': 'text/plain'}
  query = '{"query": "FOR p IN phones RETURN p"}'
  r = requests.post(dburl, data=query, headers=headers)
  assert r.json()['error'] == False

  result = r.json()['result']
  assert result[0]['phoneid'] == '123' or result[0]['phoneid'] == '456'
  assert result[1]['phoneid'] == '123' or result[1]['phoneid'] == '456'
  assert len(result[0]['friends']) == 1
  assert len(result[1]['friends']) == 1
  assert result[0]['friends'][0] == 'alice' or result[0]['friends'][0] == 'bob'
  assert result[1]['friends'][0] == 'alice' or result[1]['friends'][0] == 'bob'
  

# Run all tests.
start_db()
time.sleep(1)
start_server()
time.sleep(1)

# test_reset_server()
test_register_phone()
test_get_friends()
test_update_locations()
test_get_nearby_phones()
test_update_exchange()

test_database_contents()

kill_server()
kill_db()

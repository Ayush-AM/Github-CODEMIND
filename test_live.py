import urllib.request
import json

base = 'http://codemind-prod.ap-south-1.elasticbeanstalk.com'

# 1. Clone
print("1. Cloning...")
clone_req = urllib.request.Request(
    f'{base}/clone',
    data=json.dumps({'repo_url': 'https://github.com/Ayush-AM/Github-CODEMIND'}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
clone_res = json.loads(urllib.request.urlopen(clone_req, timeout=30).read().decode('utf-8'))
repo_id = clone_res['repo_id']
print(f"   Success! repo_id = {repo_id}")

# 2. Index
print("2. Indexing...")
index_req = urllib.request.Request(
    f'{base}/index',
    data=json.dumps({'repo_id': repo_id}).encode('utf-8'),
    headers={'Content-Type': 'application/json'}
)
index_res = json.loads(urllib.request.urlopen(index_req, timeout=60).read().decode('utf-8'))
print(f"   Success! Indexed files = {index_res['files']}, chunks = {index_res['chunks']}")

# 3. Ask suggestions
questions = [
    "Explain this codebase",
    "Describe the project architecture",
    "Which files handle API requests?"
]

for q in questions:
    print(f"\n3. Asking: '{q}'...")
    ask_req = urllib.request.Request(
        f'{base}/ask',
        data=json.dumps({'repo_id': repo_id, 'question': q}).encode('utf-8'),
        headers={'Content-Type': 'application/json'}
    )
    ask_res = json.loads(urllib.request.urlopen(ask_req, timeout=60).read().decode('utf-8'))
    print(f"   Confidence: {ask_res['confidence']}")
    print(f"   Sources: {len(ask_res['sources'])} code citations")
    for s in ask_res['sources'][:2]:
        print(f"     * {s['file']}:{s['start_line']}-{s['end_line']} ({s['name']})")
    ans_clean = ask_res['answer'].encode('ascii', 'ignore').decode('ascii')
    print(f"   Answer:\n{ans_clean[:300]}...\n")

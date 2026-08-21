import json
import sys
args = json.loads(sys.argv[1]) if len(sys.argv) > 1 else {}
main = document.querySelector('main') or document.body
txt = main.innerText or ''
out = txt[-400:] if txt else 'EMPTY'
return json.dumps({'len': len(txt), 'tail': out})
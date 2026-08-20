#!/usr/bin/env python3
import subprocess, json, sys
tabs = [('ChatGPT', 2086229289), ('Claude', 2086229276), ('DeepSeek', 2086229277), ('Grok', 2086229278), ('AIStudio', 2086229287)]
js = r'''var m=document.querySelector("main")||document.body;var t=m.innerText||"";return JSON.stringify({l:t.length,t:t.slice(-300).replace(/\n/g,"|")})'''
for n,t in tabs:
    r = subprocess.run(['agent-browser-cli', 'exec', '--tab', str(t), js], capture_output=True, text=True, timeout=30)
    out = r.stdout + r.stderr
    if '"len"' in out:
        try:
            data = json.loads(out.split('"len"')[0].rsplit('"',1)[1].split('"')[0] + '}' if '}' in out else out[out.index('{'):out.rindex('}')+1])
        except:
            data = json.loads(out[out.index('{'):out.rindex('}')+1])
        print(f"{n}: chars={data['l']}, tail={data['t'][:150]}")
    else:
        print(f"{n}: NO DATA - {out[:150]}")
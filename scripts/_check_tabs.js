// Check last 400 chars of main content
var main = document.querySelector('main') || document.body;
var txt = main.innerText || '';
var out = txt.length > 400 ? txt.slice(-400) : txt;
return JSON.stringify({len: txt.length, tail: out.replace(/\n/g, ' | ')});
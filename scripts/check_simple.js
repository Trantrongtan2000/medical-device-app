var el = document.querySelector('main');
if (!el) el = document.body;
var txt = el.innerText || '';
var msgs = document.querySelectorAll('[data-message-author-role]');
var last = msgs[msgs.length-1];
var lastLen = last ? (last.innerText || '').length : 0;
return 'messages=' + msgs.length + ' lastLen=' + lastLen + ' totalChars=' + txt.length + ' tail=' + txt.slice(-200).replace(/\r\n/g, ' | ');
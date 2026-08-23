const B64 = '__BASE64__';
const p = decodeURIComponent(escape(atob(B64)));
// contenteditable textarea (ChatGPT/DeepSeek/Grok/AIStudio common)
const ta = document.querySelector('textarea') || document.querySelector('[contenteditable="true"]');
if (ta) {
  ta.focus();
  ta.value = '';
  if (ta.tagName !== 'TEXTAREA') {
    ta.innerText = '';
    document.execCommand('selectAll', false);
    document.execCommand('delete', false);
    document.execCommand('insertText', false, p);
  } else {
    ta.value = p;
    ta.dispatchEvent(new Event('input', { bubbles: true }));
  }
  return 'len=' + (ta.value || ta.innerText || '').length;
}
return 'NO_INPUT';
const B64 = '__BASE64__';
const p = decodeURIComponent(escape(atob(B64)));
// ChatGPT textarea
const ta = document.querySelector('textarea[data-testid="conversation-input"]') || document.querySelector('textarea');
if (ta) {
  ta.focus();
  ta.value = '';
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  document.execCommand('insertText', false, p);
  ta.dispatchEvent(new Event('input', { bubbles: true }));
  return 'textarea len=' + ta.value.length;
}
return 'NO_TEXTAREA';
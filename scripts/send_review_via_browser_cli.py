#!/usr/bin/env python3
"""
Script gửi review file REVIEW_QUESTIONS.md cho các AI webinterface
sử dụng agent-browser-cli hoặc puppeteer/cluster.

Yêu cầu:
- Cài đặt: npm install -g agent-browser-cli
- Hoặc dùng Puppeteer tương tự
"""
import sys
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

REVIEW_FILE = Path("docs/REVIEW_QUESTIONS.md")

def generate_browser_script():
    """Tạo script Puppeteer/JavaScript để tương tác với các trang AI"""
    
    script = '''
// Puppeteer script to submit REVIEW_QUESTIONS.md to various AI platforms
const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

async function submitToClaude(content) {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    // Open Claude web interface
    await page.goto('https://claude.ai', { waitUntil: 'networkidle0' });
    
    // Wait for input area and type content
    const inputSelector = 'textarea[data-testid="prompt-input"]';
    await page.waitForSelector(inputSelector, { timeout: 30000 });
    
    await page.type(inputSelector, content, { delay: 10 });
    
    // Click send button
    const sendBtn = await page.$('button[data-testid="prompt-send"]');
    if (sendBtn) await sendBtn.click();
    
    console.log('✅ Đã gửi đến Claude AI');
    await browser.close();
}

async function submitToChatGPT(content) {
    const browser = await puppeteer.launch({ headless: false });
    const page = await browser.newPage();
    
    await page.goto('https://chat.openai.com', { waitUntil: 'networkidle0' });
    
    const input = await page.waitForSelector('textarea#prompt-textarea', { timeout: 30000 });
    await page.evaluate((el, text) => { el.value = text; el.dispatchEvent(new Event('input', { bubbles: true })); }, input, content);
    
    const sendBtn = await page.$('button[data-testid="send-button"]');
    if (sendBtn) await sendBtn.click();
    
    console.log('✅ Đã gửi đến ChatGPT');
    await browser.close();
}

async function main() {
    const reviewPath = path.join(__dirname, '../docs/REVIEW_QUESTIONS.md');
    const content = fs.readFileSync(reviewPath, 'utf8');
    
    const target = process.argv[2] || 'all';
    
    if (target === 'claude' || target === 'all') {
        await submitToClaude(content);
    }
    if (target === 'chatgpt' || target === 'all') {
        await submitToChatGPT(content);
    }
}

main().catch(console.error);
'''
    return script

def main():
    content = "..."
    if REVIEW_FILE.exists():
        content = REVIEW_FILE.read_text(encoding='utf-8')
    
    print("""
# 🤖 Hướng Dẫn Gửi Review cho Các AI

## Phương pháp 1: Dùng agent-browser-cli

### Cài đặt:
\`\`\`bash
npm install -g agent-browser-cli
\`\`\`

### Gửi file:
\`\`\`bash
# Gửi cho Claude
agent-browser-cli submit-content --url https://claude.ai --file docs/REVIEW_QUESTIONS.md

# Gửi cho ChatGPT  
agent-browser-cli submit-content --url https://chat.openai.com --file docs/REVIEW_QUESTIONS.md

# Gửi cho tất cả
agent-browser-cli batch-submit --file docs/REVIEW_QUESTIONS.md
\`\`\`

## Phương pháp 2: Dùng Puppeteer (script kèm theo)

Đã tạo file: \`scripts/browser_submit_review.js\`

## Phương pháp 3: Thủ công (nhanh nhất)

Gõ nội dung sau vào hộp chat các AI:

---
""")
    
    print(content[:3000])
    print("\n...(xem file docs/REVIEW_QUESTIONS.md để xem toàn bộ)")

if __name__ == "__main__":
    main()
/**
 * Puppeteer script tương tác với các AI web interface
 * 
 * Sử dụng:
 * 1. Cài đặt: npm install puppeteer
 * 2. Chạy: node scripts/browser_submit_review.js
 */

const puppeteer = require('puppeteer');
const fs = require('fs');
const path = require('path');

const REVIEW_FILE = path.join(__dirname, '../docs/REVIEW_QUESTIONS.md');
let CONTENT = '';

async function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

async function submitToClaude(content, browserName = 'Claude') {
    console.log(`\n[1/3] 🤖 ${browserName} - Đang mửa https://claude.ai...`);
    
    const browser = await puppeteer.launch({
        headless: false,
        args: ['--no-sandbox', '--disable-setuid-sandbox']
    });
    
    try {
        const page = await browser.newPage();
        await page.setViewport({ width: 1280, height: 800 });
        
        await page.goto('https://claude.ai', { waitUntil: 'networkidle2', timeout: 60000 });
        console.log(`   → Đã tải trang Claude`);
        
        // Tìm input textarea
        const inputSelector = 'textarea[data-testid="prompt-input"], textarea[name="prompt"], .textarea-container textarea';
        const input = await page.$(inputSelector);
        
        if (input) {
            await input.type(content, { delay: 5 });
            console.log(`   → Đã nhập nội dung (${content.length} ký tự)`);
            
            // Gửi bằng cách click nút gửi hoặc Ctrl+Enter
            const sendBtn = await page.$('button[data-testid="prompt-send"], button.send-button');
            if (sendBtn) {
                await sendBtn.click();
            } else {
                await page.keyboard.press('Enter', { mods: { ctrl: true } });
            }
            console.log(`   → Đã gửi! Vui lòng xác nhận trong trình duyệt.`);
        } else {
            console.log(`   → Không tìm thấy input. Vui lòng nhập thủ công.`);
        }
    } catch (e) {
        console.log(`   → Lỗi: ${e.message}`);
    } finally {
        // Để trình duyệt mở để người dùng xác nhận
        console.log(`\n✅ Mở trình duyệt để xác nhận gửi.`);
        await new Promise(r => setTimeout(r, 30000)); // Đợi 30 giây
    }
}

async function submitToChatGPT(content) {
    console.log(`\n[2/3] 💬 ChatGPT - Vui lòng truy cập https://chat.openai.com`);
    console.log(`   → Nội dung đã sẵn sàng, dán vào hộp chat.`);
}

async function main() {
    // Đọc file review
    if (!fs.existsSync(REVIEW_FILE)) {
        console.log('❌ Không tìm thấy file:', REVIEW_FILE);
        console.log('   Vui lòng chạy: python scripts/send_review_to_all_ai.py');
        process.exit(1);
    }
    
    CONTENT = fs.readFileSync(REVIEW_FILE, 'utf8');
    console.log('📄 Đã đọc file REVIEW_QUESTIONS.md');
    console.log(`   → Nội dung: ${CONTENT.length} ký tự`);
    
    const args = process.argv.slice(2);
    const target = args[0] || 'claude';
    
    console.log('\n' + '='.repeat(60));
    console.log('🤖 Script Tương Tác Browser - Gửi Review AI');
    console.log('='.repeat(60));
    
    if (target === 'claude' || target === 'all') {
        await submitToClaude(CONTENT);
    } else if (target === 'chatgpt') {
        await submitToChatGPT(CONTENT);
    } else {
        console.log(`\n📚 HƯỚNG DẪN SỬ DỤNG:\n`);
        console.log(`   node scripts/browser_submit_review.js claude  # Gửi cho Claude`);
        console.log(`   node scripts/browser_submit_review.js chatgpt # Gửi cho ChatGPT`);
        console.log(`   node scripts/browser_submit_review.js all     # Gửi cho cả 2\n`);
    }
    
    console.log('\n📝 Lưu ý:');
    console.log('   - Puppeteer cần cài: npm install puppeteer');
    console.log('   - Chrome/Chromium sẽ mở để xác nhận');
}

main().catch(console.error);
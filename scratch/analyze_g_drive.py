import os
import sys
from pathlib import Path
from collections import defaultdict, Counter

sys.stdout.reconfigure(encoding='utf-8')

root = Path(r'G:\BV QUẬN 7_OCR_WORK_20260712')

print(f"🔍 BẮT ĐẦU PHÂN TÍCH TOÀN BỘ KHO DỮ LIỆU: {root}\n")

if not root.exists():
    print("❌ Thư mục không tồn tại!")
    sys.exit(1)

total_files = 0
total_size = 0
ext_counter = Counter()
dir_stats = defaultdict(lambda: {'files': 0, 'size': 0, 'extensions': Counter()})

for dirpath, dirnames, filenames in os.walk(root):
    rel_dir = os.path.relpath(dirpath, root)
    top_dir = rel_dir.split(os.sep)[0] if rel_dir != '.' else 'ROOT'
    
    for f in filenames:
        total_files += 1
        fp = os.path.join(dirpath, f)
        try:
            sz = os.path.getsize(fp)
        except Exception:
            sz = 0
            
        total_size += sz
        ext = os.path.splitext(f)[1].lower() or '[NO_EXT]'
        ext_counter[ext] += 1
        
        dir_stats[top_dir]['files'] += 1
        dir_stats[top_dir]['size'] += sz
        dir_stats[top_dir]['extensions'][ext] += 1

print("=" * 70)
print(f"📊 TỔNG QUAN KHO DỮ LIỆU:")
print(f"  • Tổng số tệp (Files): {total_files:,} files")
print(f"  • Tổng dung lượng lưu trữ: {total_size / (1024*1024):,.2f} MB ({total_size / (1024*1024*1024):,.2f} GB)")
print("=" * 70)

print("\n📁 PHÂN BỔ CHI TIẾT THEO TỪNG THƯ MỤC CHỨC NĂNG:")
for d_name, stats in sorted(dir_stats.items(), key=lambda x: x[1]['files'], reverse=True):
    mb_sz = stats['size'] / (1024*1024)
    top_exts = ", ".join([f"{k}: {v}" for k, v in stats['extensions'].most_common(3)])
    print(f" 📂 [{d_name}]")
    print(f"    - Số tệp: {stats['files']:,} files | Dung lượng: {mb_sz:,.2f} MB")
    print(f"    - Định dạng chính: {top_exts}")

print("\n📄 THỐNG KÊ THEO ĐỊNH DẠNG TỆP (FILE EXTENSIONS):")
for ext, count in ext_counter.most_common(12):
    print(f"  • {ext:12s}: {count:6,} files ({count/total_files*100:5.1f}%)")

# List key manifests & system scripts in 00_HE_THONG_VA_SCRIPTS
sys_dir = root / "00_HE_THONG_VA_SCRIPTS"
if sys_dir.exists():
    print("\n⚙️ CÁC TỆP CẤU HÌNH & SCRIPTS TRỌNG YẾU TRONG [00_HE_THONG_VA_SCRIPTS]:")
    for item in list(sys_dir.iterdir())[:15]:
        if item.is_file():
            print(f"  - {item.name} ({item.stat().st_size / 1024:.1f} KB)")

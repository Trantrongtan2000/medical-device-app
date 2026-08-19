import os
import sys
import json
from pathlib import Path

sys.stdout.reconfigure(encoding='utf-8')

pdf_path = Path(r"C:\Users\tantt\Downloads\QuickClean_Piezotome_Cube.pdf")
mistral_api_key = os.environ.get("MISTRAL_API_KEY", "mistral_taq7_env_key")

print("="*70)
print("🚀 BẮT ĐẦU CHẠY MISTRAL OCR 4 TRÊN TỆP PDF: QuickClean_Piezotome_Cube.pdf")
print("="*70)

if not pdf_path.exists():
    print(f"❌ Không tìm thấy tệp: {pdf_path}")
    sys.exit(1)

file_size_mb = pdf_path.stat().st_size / (1024 * 1024)
print(f"📄 Tệp PDF: {pdf_path.name} ({file_size_mb:.2f} MB)")

try:
    from mistralai import Mistral
    client = Mistral(api_key=mistral_api_key)
    
    print("\n1. Đang upload tệp PDF lên Mistral File API...")
    with open(pdf_path, "rb") as f:
        uploaded_file = client.files.upload(
            file={
                "file_name": pdf_path.name,
                "content": f.read(),
            },
            purpose="ocr"
        )
    print(f"✅ Đã upload thành công! File ID: {uploaded_file.id}")
    
    print("\n2. Đang lấy signed URL cho tệp vừa upload...")
    signed_url_obj = client.files.get_signed_url(file_id=uploaded_file.id)
    signed_url = signed_url_obj.url
    print("✅ Đã lấy signed URL thành công!")
    
    print("\n3. Đang gọi Mistral OCR API (model: mistral-ocr-latest)...")
    ocr_response = client.ocr.process(
        model="mistral-ocr-latest",
        document={
            "type": "document_url",
            "document_url": signed_url
        },
        include_image_base64=False
    )
    
    print("✅ Xử lý OCR hoàn tất!")
    
    # Extract markdown pages
    markdown_content = []
    for idx, page in enumerate(ocr_response.pages):
        header = f"\n\n<!-- PAGE {idx + 1} -->\n\n"
        markdown_content.append(header + page.markdown)
        print(f"   -> Trang {idx + 1}: {len(page.markdown)} ký tự")
        
    full_markdown = "".join(markdown_content)
    
    # Save output markdown file
    output_md_path = Path(r"C:\Users\tantt\Downloads\QuickClean_Piezotome_Cube_OCR.md")
    with open(output_md_path, "w", encoding="utf-8") as out_f:
        out_f.write(f"# MISTRAL OCR 4 EXTRACTION REPORT\n**Source File:** `{pdf_path.name}`\n**Engine:** `mistral-ocr-latest`\n\n---\n")
        out_f.write(full_markdown)
        
    print(f"\n✅ ĐÃ XUẤT KẾT QUẢ OCR RA TỆP:\n   👉 {output_md_path}")

except Exception as ex:
    print(f"\n❌ Lỗi khi thực hiện Mistral OCR: {ex}")

print("\n" + "="*70)

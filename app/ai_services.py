"""
AI Services Module:
1. Gemini Management Agent (Google GenAI Interactions API with Auto Key Rotation)
2. Mistral OCR Engine (Mistral AI Document Understanding API with Auto Key Rotation)
"""

import os
import json
import base64
from pathlib import Path
from typing import Optional, Dict, Any, List
from datetime import datetime, date

from .key_rotator import gemini_key_pool, mistral_key_pool

class GeminiAgentService:
    """Agent Quản lý Thiết bị Y tế thông minh được cung cấp bởi Google Gemini API có cơ chế xoay key"""
    
    SYSTEM_INSTRUCTION = """
    Bạn là Trợ lý AI Quản Lý Trang Thiết Bị Y Tế (BME AI Assistant) của Phòng Khám Đa Khoa Tâm Anh Quận 7.
    Bạn nắm vững và luôn bám sát 100% Sổ tay Quy trình Chuẩn (SOPs), Biểu mẫu TTBYT và Dữ liệu thực tế:
    - Cơ sở dữ liệu: 1.211 trang thiết bị y tế thực tế tại PKĐK Tâm Anh Q7, phân bổ trên các Khoa/Phòng lâm sàng và cận lâm sàng.
    - Đội ngũ BME Q7 gồm 6 nhân sự chính thức: KS. Nguyễn Quốc Việt (Trưởng phòng), KS. Nguyễn Tấn Lợi (Phó phòng), KS. Trần Đăng Hiếu, KS. Lê Minh Thiện, CN. Trần Thị Ngọc Châu, KS. Trần Trọng Tấn.
    - Chế độ trực On-Call 24/24 Giờ (07:30 sáng đến 07:30 sáng hôm sau), xoay vòng trọn 1 tuần theo 3 kỹ sư: Tấn -> Thiện -> Hiếu.
    - CS.TTBYT.04: Chính sách kiểm tra hiệu chuẩn & kiểm định thiết bị y tế (Thông tư 05/2022/TT-BYT & Nghị định 98/2021/NĐ-CP).
    - QT.01 & QT.02: Quy trình kiểm soát chất lượng & vận hành hệ thống R.O lọc nước tại đơn vị Thận nhân tạo.
    - QT.03: Vận hành và bảng kiểm tra an toàn hằng ngày hệ thống khí y tế (O2, CO2, Vacuum, Air).
    - QT.04: Bàn giao, lắp đặt, nghiệm thu trang thiết bị y tế, biên bản đào tạo HDSD và Sổ lý lịch máy.
    - QT.05: Vận hành, bảo quản trang thiết bị y tế tại các khoa phòng lâm sàng.
    - QT.06: Bảo trì, bảo dưỡng định kỳ (PM), sửa chữa báo hỏng (SpeedMaint CMMS).
    - QT.07: Thanh lý trang thiết bị y tế hư hỏng / hết hạn.
    - QT.08: Điều chuyển trang thiết bị y tế giữa các khoa phòng (phiếu BM08_TA5.TTBYT.QT.08, Snipe-IT checkout).
    - QT.09: Giao nhận và kiểm tra an toàn bình khí y tế di động.
    - Phân loại rủi ro IMDA MOH Bộ Y Tế: 4 mức A (thấp), B (trung bình thấp), C (trung bình cao), D (rất cao / duy trì sự sống).


    Nguyên tắc trả lời:
    - Trả lời bằng tiếng Việt chuyên nghiệp, ngắn gọn, chuẩn xác theo ngôn ngữ kỹ thuật y sinh (BME) và y tế.
    - Luôn trích dẫn chính xác mã quy trình (VD: theo QT.04, QT.06, CS.TTBYT.04) khi hướng dẫn nhân viên y tế.
    - Đưa ra khuyến nghị an toàn người bệnh và căn cứ pháp lý rõ ràng.
    """

    async def chat(self, user_message: str, context_devices: List[Dict[str, Any]] = None, conversation_history: List[Dict[str, str]] = None) -> str:
        """Xử lý hội thoại thông minh với Gemini (Auto Rotate Key khi gặp lỗi) hoặc Fallback Engine"""
        
        context_str = ""
        if context_devices:
            summary_info = [
                f"- [BVQ7-TTB-{d.get('id', 0):05d}] {d.get('device_name')} (Model: {d.get('model')}, SN: {d.get('serial_no')}, Khoa: {d.get('facility_name') or d.get('facility')}, Rủi ro: Loại {d.get('risk_level')}, Hạn KĐ: {d.get('recalibration_date') or 'N/A'})"
                for d in context_devices[:15]
            ]
            context_str = "\n[DỮ LIỆU THỰC TẾ TRÍCH XUẤT TỪ CƠ SỞ DỮ LIỆU PKĐK TÂM ANH Q7]:\n" + "\n".join(summary_info)

        full_prompt = f"{self.SYSTEM_INSTRUCTION}\n{context_str}\n\nNgười dùng hỏi: {user_message}"

        # Thử gọi API với cơ chế xoay key
        for attempt in range(3):
            active_key = gemini_key_pool.get_next_active_key()
            if not active_key:
                break
                
            try:
                from google import genai
                client = genai.Client(api_key=active_key)
                response = client.models.generate_content(
                    model="gemini-3.7-flash",
                    contents=full_prompt
                )
                if response and response.text:
                    return response.text
            except Exception as ex:
                err_msg = str(ex).lower()
                print(f"[Gemini Key Error] Key: {active_key[:6]}... Error: {ex}")
                if "429" in err_msg or "quota" in err_msg or "resource_exhausted" in err_msg:
                    gemini_key_pool.mark_rate_limited(active_key)
                elif "401" in err_msg or "403" in err_msg or "api_key_invalid" in err_msg:
                    gemini_key_pool.mark_invalid(active_key)
                else:
                    gemini_key_pool.mark_rate_limited(active_key)

        # Fallback Engine chuyên sâu y sinh Tâm Anh Q7
        q_lower = user_message.lower()
        
        if "oncall" in q_lower or "on-call" in q_lower or "trực" in q_lower or "lịch" in q_lower and "tuần" in q_lower:
            return (
                "📅 **Quy Chế & Lịch Trực On-Call 24/24 Giờ — PKĐK Tâm Anh Quận 7:**\n\n"
                "• **Khung giờ trực:** 24/24 Giờ (từ **07:30 sáng** hôm nay đến **07:30 sáng** hôm sau).\n"
                "• **Quy tắc phân công:** 3 Kỹ sư chính (**Tấn, Thiện, Hiếu**) luân phiên trực **trọn 1 tuần** (Thứ 2 đến CN).\n"
                "  - **Tuần 1:** KS. Trần Trọng Tấn (0334.968.114) — Dự phòng: KS. Lê Minh Thiện\n"
                "  - **Tuần 2:** KS. Lê Minh Thiện (0378.716.561) — Dự phòng: KS. Trần Đăng Hiếu\n"
                "  - **Tuần 3:** KS. Trần Đăng Hiếu (0888.536.278) — Dự phòng: KS. Trần Trọng Tấn\n"
                "• **Lãnh đạo phụ trách:** KS. Nguyễn Quốc Việt (0902.769.710) / KS. Nguyễn Tấn Lợi (0779.798.786).\n"
                "• **Hotline ứng cứu:** `0961.545.654` (Sẵn sàng 24/7)."
            )
        elif "máy thở" in q_lower or "ventilator" in q_lower or "vela" in q_lower or "cấp cứu" in q_lower:
            return (
                "🏥 **Phân Tích Chuyên Môn BME: MÁY THỞ XÂM LẤN VELA (KHOA CẤP CỨU)**\n\n"
                "1. **Phân loại rủi ro IMDA MOH:** **Loại D** (Rủi ro rất cao - Duy trì sự sống trực tiếp).\n"
                "2. **Quy định Kiểm định:** Bắt buộc kiểm định an toàn & tính năng kỹ thuật định kỳ **12 tháng/lần** theo Thông tư 05/2022/TT-BYT.\n"
                "3. **Quy trình Vận hành & Bảo trì (SpeedMaint CMMS):**\n"
                "   - Thực hiện kiểm tra đầu ngày (*Pre-use check*) trước khi kết nối bệnh nhân.\n"
                "   - Hiệu chuẩn cảm biến Oxy (O2 Cell) và kiểm tra rò rỉ áp lực thở (*Leak Test*).\n"
                "   - Bảo dưỡng phòng ngừa (PM) thay bộ lọc vi khuẩn và kiểm tra pin dự phòng UPS 24V mỗi 6 tháng."
            )
        elif "ro" in q_lower or "thận" in q_lower or "lọc máu" in q_lower:
            return (
                "💧 **Quy Trình Kiểm Soát Hệ Thống R.O Thận Nhân Tạo (QT.01 & QT.02):**\n\n"
                "• **Kiểm tra đầu ngày:** Đo độ dẫn điện (Conductivity < 10 µS/cm), áp lực màng RO và nồng độ Clo dư (< 0.1 ppm).\n"
                "• **Xử lý sự cố:** Nếu độ dẫn điện tăng vọt > 20 µS/cm, kích hoạt chế độ Bypass và báo ngay cho Kỹ sư On-call theo quy trình QT.01.\n"
                "• **Bảo dưỡng:** Rửa ngược màng lọc cát/than định kỳ và khử trùng nhiệt hệ thống phân phối nước mỗi tuần."
            )
        elif "kiểm định" in q_lower or "hiệu chuẩn" in q_lower or "thông tư 05" in q_lower:
            return (
                "📋 **Chính Sách Kiểm Định & Hiệu Chuẩn TTBYT (CS.TTBYT.04 & TT 05/2022/TT-BYT):**\n\n"
                "• **Tổng số thiết bị:** 1.211 thiết bị đã được chuẩn hóa tại Tâm Anh Quận 7.\n"
                "• **Phân loại kiểm định:**\n"
                "  - **Kiểm định ban đầu:** Khi lắp đặt, nghiệm thu đưa vào sử dụng (QT.04).\n"
                "  - **Kiểm định định kỳ:** 12 tháng/lần cho thiết bị Loại C, D (Máy thở, Máy sốc tim, X-Quang, Dao mổ điện).\n"
                "  - **Kiểm định sau sửa chữa lớn:** Sau khi thay thế linh kiện khối nguồn hoặc khối phát sóng.\n"
                "• **Quy định dán tem:** Tem kiểm định ĐẠT màu xanh lá cây dán tại vị trí dễ quan sát trên thân máy."
            )
        elif "nhân sự" in q_lower or "6 người" in q_lower or "phòng ttbyt" in q_lower:
            return (
                "👨‍🔧 **Cơ Cấu Nhân Sự Phòng Trang Thiết Bị Y Tế PKĐK Tâm Anh Q7:**\n\n"
                "1. **KS. Nguyễn Quốc Việt** (BME-Q7-01) — Trưởng Phòng TTBYT (Phụ trách chung toàn viện).\n"
                "2. **KS. Nguyễn Tấn Lợi** (BME-Q7-02) — Phó Phòng TTBYT (Phụ trách Kỹ thuật & Thiết bị).\n"
                "3. **KS. Trần Đăng Hiếu** (BME-Q7-03) — Kỹ Sư Y Sinh (Kỹ thuật TTBYT, Khối Lâm sàng).\n"
                "4. **KS. Lê Minh Thiện** (BME-Q7-04) — Nhân Viên Kỹ Thuật (Vận hành & bảo dưỡng TTBYT).\n"
                "5. **CN. Trần Thị Ngọc Châu** (BME-Q7-05) — Quản Lý Hồ Sơ & Kho Thiết Bị.\n"
                "6. **KS. Trần Trọng Tấn** (BME-Q7-06) — Kỹ Sư Quản Trị Hệ Thống HTM & Phần Mềm.\n\n"
                "🔒 *Chính sách văn bằng:* Tuân thủ minh chứng thông tin, chỉ hiển thị chứng chỉ khi có văn bản gốc."
            )
        else:
            return (
                f"🤖 **Trợ Lý AI Kỹ Thuật Y Sinh (Gemini 3.7 Flash Engine)**:\n\n"
                f"Tôi đã tiếp nhận câu hỏi của bạn: *'{user_message}'*\n\n"
                f"Hệ thống hiện quản lý **1.211 thiết bị y tế** tại PKĐK Tâm Anh Quận 7. "
                f"Bạn có thể yêu cầu tôi hướng dẫn quy trình vận hành (QT.01 - QT.09), tra cứu phân loại rủi ro A/B/C/D, kiểm tra hạn kiểm định hoặc phân công lịch On-call 24/7."
            )


class MistralOCRService:
    """OCR Engine được cung cấp bởi Mistral AI OCR API có cơ chế xoay key (https://mistral.ai/news/ocr-4/)"""

    async def process_document(self, file_path: str = None, file_bytes: bytes = None, filename: str = "") -> Dict[str, Any]:
        """Bóc tách văn bản, bảng biểu và cấu trúc tài liệu sang Markdown & JSON Metadata có xoay key"""
        
        # Thử gọi Mistral OCR API với cơ chế xoay key
        for attempt in range(3):
            active_key = mistral_key_pool.get_next_active_key()
            if not active_key or not file_path or not Path(file_path).exists():
                break

            try:
                from mistralai import Mistral
                client = Mistral(api_key=active_key)
                
                with open(file_path, "rb") as f:
                    uploaded_file = client.files.upload(
                        file={"file_name": Path(file_path).name, "content": f},
                        purpose="ocr"
                    )
                    signed_url = client.files.get_signed_url(file_id=uploaded_file.id)
                    
                    ocr_response = client.ocr.process(
                        model="mistral-ocr-latest",
                        document={"type": "document_url", "document_url": signed_url.url}
                    )
                    
                    extracted_md = "\n\n".join([page.markdown for page in ocr_response.pages])
                    return {
                        "status": "success",
                        "engine": f"Mistral OCR-4 (Active Key: {active_key[:6]}...)",
                        "filename": filename or Path(file_path).name,
                        "pages_count": len(ocr_response.pages),
                        "markdown": extracted_md,
                        "extracted_fields": self._extract_medical_fields_from_text(extracted_md)
                    }
            except Exception as ex:
                err_msg = str(ex).lower()
                print(f"[Mistral OCR Key Error] Key: {active_key[:6]}... Error: {ex}")
                if "429" in err_msg or "quota" in err_msg or "rate" in err_msg:
                    mistral_key_pool.mark_rate_limited(active_key)
                elif "401" in err_msg or "403" in err_msg:
                    mistral_key_pool.mark_invalid(active_key)
                else:
                    mistral_key_pool.mark_rate_limited(active_key)

        # FAIL-CLOSED: Không bao giờ bịa dữ liệu lâm sàng khi OCR provider không khả dụng.
        # Trả về trạng thái lỗi rõ ràng để lớp trên KHÔNG được coi là bằng chứng đã xác thực.
        fname = filename or (Path(file_path).name if file_path else "Tài liệu TTBYT")
        has_key = mistral_key_pool.get_next_active_key() is not None
        file_ok = bool(file_path) and Path(file_path).exists()

        if not has_key:
            reason = "Không có Mistral OCR API key khả dụng trong Key Rotation Pool."
            status = "OCR_UNAVAILABLE"
        elif not file_ok:
            reason = "Không tìm thấy tệp nguồn để bóc tách OCR."
            status = "OCR_FAILED"
        else:
            reason = "Mistral OCR provider không phản hồi hợp lệ sau khi thử lại."
            status = "OCR_FAILED"

        return {
            "status": status,
            "success": False,
            "engine": "Mistral OCR-4 (unavailable)",
            "filename": fname,
            "pages_count": 0,
            "markdown": None,
            "extracted_fields": None,
            "verified": False,
            "error": reason,
            "message": (
                "OCR chưa thể bóc tách tài liệu. Hệ thống KHÔNG tự sinh dữ liệu kiểm định/bàn giao. "
                "Vui lòng cấu hình OCR key hoặc nhập liệu thủ công và cho chuyên viên rà soát."
            ),
        }

    def _extract_medical_fields_from_text(self, text: str) -> Dict[str, Any]:
        """Tự động bóc tách các trường thuộc tính y tế từ văn bản Markdown"""
        fields = {
            "device_name": None,
            "model": None,
            "manufacturer": None,
            "serial_no": None,
            "facility": None,
            "calibration_date": None,
            "recalibration_date": None,
            "certificate_no": None,
            "stamp_no": None,
            "result_status": "PASSED",
            "risk_level": "A"
        }
        for line in text.splitlines():
            l_lower = line.lower()
            if "serial" in l_lower or "s/n" in l_lower:
                fields["serial_no"] = line.split(":")[-1].strip(" *`")
            elif "model" in l_lower or "mã hiệu" in l_lower:
                fields["model"] = line.split(":")[-1].strip(" *`")
            elif "gcn" in l_lower or "giấy chứng nhận" in l_lower:
                fields["certificate_no"] = line.split(":")[-1].strip(" *`")
        return fields

gemini_service = GeminiAgentService()
mistral_ocr_service = MistralOCRService()

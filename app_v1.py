import streamlit as st
import requests
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

API_BASE_URL = os.getenv("API_BASE_URL")
HF_TOKEN = os.getenv("HF_TOKEN")

st.set_page_config(
    page_title="Vietnamese Text Summarizer",
    page_icon="📝",
    layout="wide"
)

st.title("📝 Vietnamese Text Summarizer")
st.markdown("Tóm tắt văn bản tiếng Việt bằng **VietAI/vit5-large-vietnews-summarization**")

# Sidebar settings
with st.sidebar:
    st.header("⚙️ Cài đặt")
    max_new_tokens = st.slider("Max new tokens", 50, 300, 160)
    temperature = st.slider("Temperature", 0.1, 1.0, 0.7, 0.1)
    top_p = st.slider("Top P", 0.1, 1.0, 0.9, 0.1)

# Main input
document = st.text_area(
    "Nhập văn bản cần tóm tắt:",
    height=200,
    placeholder="Nhập văn bản tiếng Việt của bạn tại đây..."
)

col1, col2 = st.columns([1, 5])
with col1:
    summarize_btn = st.button("🚀 Tóm tắt", type="primary", use_container_width=True)

if summarize_btn:
    if not document.strip():
        st.error("❌ Vui lòng nhập văn bản!")
    elif not HF_TOKEN:
        st.error("❌ Thiếu HF_TOKEN trong file .env!")
    else:
        with st.spinner("Đang xử lý..."):
            try:
                # ViT5 chỉ cần text input, không cần role-based prompt như Gemma
                inputs = f"Tóm tắt văn bản sau:\n{document}\nTóm tắt:"

                response = requests.post(
                    API_BASE_URL,
                    headers={
                        "Authorization": f"Bearer {HF_TOKEN}",
                        "Content-Type": "application/json"
                    },
                    json={
                        "inputs": inputs,
                        "parameters": {
                            "max_new_tokens": max_new_tokens,
                            "temperature": temperature,
                            "top_p": top_p,
                            "do_sample": True,
                            "repetition_penalty": 1.2
                        }
                    },
                    timeout=120
                )

                if response.status_code == 200:
                    result = response.json()
                    # st.write("🔍 Raw API response:", result)  # Debug hiển thị kết quả thật

                    summary = ""

                    # Model có thể trả về theo 2 dạng: list hoặc dict
                    if isinstance(result, list) and len(result) > 0:
                        # Trường hợp 1: Model trả về [{"summary_text": "..."}]
                        if "summary_text" in result[0]:
                            summary = result[0]["summary_text"]
                        # Trường hợp 2: Model trả về [{"generated_text": "..."}]
                        elif "generated_text" in result[0]:
                            summary = result[0]["generated_text"]
                    elif isinstance(result, dict):
                        summary = result.get("summary_text") or result.get("generated_text", "")

                    # Làm sạch text
                    summary = (summary or "").strip()
                    summary = " ".join(summary.split())

                    if not summary:
                        st.warning("⚠️ Model không trả về nội dung tóm tắt. Hãy thử giảm `max_new_tokens` hoặc kiểm tra text đầu vào.")
                    else:
                        st.success("✅ Tóm tắt thành công!")
                        st.subheader("📄 Kết quả:")
                        st.info(summary)


                elif response.status_code == 503:
                    st.warning("⏳ Model đang khởi động, vui lòng đợi 20–30 giây rồi thử lại!")
                else:
                    st.error(f"❌ Lỗi API: {response.status_code}")
                    st.code(response.text)

            except requests.exceptions.Timeout:
                st.error("⏱️ Timeout! Model mất quá nhiều thời gian xử lý.")
            except Exception as e:
                st.error(f"❌ Lỗi: {str(e)}")

# Demo examples
with st.expander("💡 Văn bản mẫu"):
    demo_text = """Việt Nam đã ghi nhận những thành tựu đáng kể trong phát triển kinh tế trong những năm gần đây. GDP của nước ta đã tăng trưởng ổn định với tốc độ bình quân 6-7% mỗi năm, thu hút được nhiều nhà đầu tư nước ngoài từ các tập đoàn lớn trên thế giới. Các ngành công nghiệp như điện tử, dệt may, và nông nghiệp đã có những bước tiến vượt bậc, góp phần quan trọng vào xuất khẩu."""
    if st.button("Sử dụng văn bản mẫu"):
        st.session_state["document"] = demo_text
        st.rerun()

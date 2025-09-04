import streamlit as st
import requests
import json
import time
from datetime import datetime
import logging
import os
from dotenv import load_dotenv

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('streamlit_requests.log', encoding='utf-8'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)
load_dotenv()

st.set_page_config(
    page_title="Vietnamese Text Summarization", 
    page_icon="📄", 
    layout="wide"
)

st.markdown("""
<style>
.main-header {
    font-size: 2.5rem;
    font-weight: bold;
    text-align: center;
    margin-bottom: 1rem;
    background: linear-gradient(90deg, #FF6B6B, #4ECDC4);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
}
.stat-card {
    background-color: #f0f2f6;
    padding: 1rem;
    border-radius: 0.5rem;
    border-left: 4px solid #4ECDC4;
}
</style>
""", unsafe_allow_html=True)

API_BASE_URL = os.getenv("API_BASE_URL", st.secrets.get("API_BASE_URL", "http://localhost:8000"))

with st.sidebar:
    st.header("⚙️ Cấu hình Tóm tắt")
    st.subheader("🔌 Trạng thái API")
    
    def check_api_health():
        try:
            response = requests.get(f"{API_BASE_URL}/health", timeout=5)
            if response.status_code == 200:
                health_data = response.json()
                return True, health_data
            else:
                return False, {"error": f"Status code: {response.status_code}"}
        except requests.exceptions.RequestException as e:
            return False, {"error": str(e)}
    
    is_healthy, health_info = check_api_health()
    
    if is_healthy:
        st.success("✅ API hoạt động bình thường")
        st.json(health_info)
    else:
        st.error("❌ API không khả dụng")
        st.json(health_info)
        st.info("Hãy chạy API server trước:\n```python gemma2_api_service.py```")
    
    st.divider()
    
    # Tham số tóm tắt
    st.subheader("🎛️ Tham số")
    max_new_tokens  = st.slider("Độ dài tóm tắt tối đa", 50, 300, 160, 10)
    temperature = st.slider("Temperature (sáng tạo)", 0.1, 1.0, 0.7, 0.1)
    top_p = st.slider("Top-p (đa dạng)", 0.1, 1.0, 0.9, 0.1)
    
    st.divider()
    
    # Demo nhanh
    if st.button("🚀 Demo nhanh"):
        if is_healthy:
            try:
                demo_response = requests.get(f"{API_BASE_URL}/demo", timeout=30)
                if demo_response.status_code == 200:
                    demo_data = demo_response.json()
                    st.session_state["demo_result"] = demo_data
                    st.success("✅ Demo thành công!")
                else:
                    st.error(f"❌ Demo thất bại: {demo_response.text}")
            except Exception as e:
                st.error(f"❌ Lỗi demo: {e}")
        else:
            st.error("❌ API không khả dụng!")

st.markdown('<p class="main-header">📄 Vietnamese Text Summarization</p>', unsafe_allow_html=True)
st.markdown("Sử dụng Gemma-2 để tóm tắt văn bản tiếng Việt một cách thông minh và chính xác.")

if "demo_result" in st.session_state:
    st.subheader("🎯 Kết quả Demo")
    demo_data = st.session_state["demo_result"]
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("**Tóm tắt:**")
        st.info(demo_data["summary"])
    
    with col2:
        st.markdown('<div class="stat-card">', unsafe_allow_html=True)
        st.metric("Thời gian xử lý", f"{demo_data['processing_time']}s")
        st.metric("Độ dài gốc", f"{demo_data['input_length']} ký tự")
        st.metric("Độ dài tóm tắt", f"{demo_data['output_length']} ký tự")
        st.markdown('</div>', unsafe_allow_html=True)
    
    st.divider()

st.subheader("✏️ Nhập văn bản cần tóm tắt")

tab1, tab2, tab3 = st.tabs(["📝 Nhập thủ công", "📋 Ví dụ mẫu", "📁 Upload file"])

with tab1:
    user_text = st.text_area(
        "Nhập văn bản tiếng Việt:",
        height=200,
        placeholder="Dán văn bản cần tóm tắt vào đây...",
        key="manual_input"
    )

with tab2:
    sample_texts = {
        "Kinh tế Việt Nam": """Việt Nam đã ghi nhận những thành tựu đáng kể trong phát triển kinh tế trong những năm gần đây. GDP của nước ta đã tăng trưởng ổn định với tốc độ bình quân 6-7% mỗi năm, thu hút được nhiều nhà đầu tư nước ngoài từ các tập đoàn lớn trên thế giới. Các ngành công nghiệp như điện tử, dệt may, và nông nghiệp đã có những bước tiến vượt bậc, góp phần quan trọng vào xuất khẩu. Chính phủ cũng đã triển khai nhiều chính sách hỗ trợ doanh nghiệp nhỏ và vừa, tạo điều kiện thuận lợi cho sự phát triển của khu vực tư nhân và khởi nghiệp.""",
        
        "Công nghệ AI": """Trí tuệ nhân tạo (AI) đang trở thành một trong những công nghệ quan trọng nhất của thế kỷ 21. Với khả năng xử lý dữ liệu lớn và học hỏi từ kinh nghiệm, AI đã được ứng dụng rộng rãi trong nhiều lĩnh vực từ y tế, giáo dục, giao thông đến tài chính và thương mại điện tử. Các công ty công nghệ lớn như Google, Microsoft, và OpenAI đang đầu tư mạnh mẽ vào nghiên cứu và phát triển AI. Tuy nhiên, sự phát triển của AI cũng đặt ra nhiều thách thức về đạo đức, việc làm, quyền riêng tư và an ninh mạng mà xã hội cần giải quyết.""",
        
        "Biến đổi khí hậu": """Biến đổi khí hậu đang là một trong những thách thức lớn nhất mà nhân loại phải đối mặt trong thế kỷ này. Nhiệt độ trái đất liên tục tăng cao do hoạt động phát thải khí nhà kính từ con người, dẫn đến băng tan ở hai cực, mực nước biển dâng cao và các hiện tượng thời tiết cực đoan ngày càng gia tăng như bão lũ, hạn hán. Các quốc gia trên thế giới đang nỗ lực giảm phát thải khí nhà kính thông qua việc chuyển đổi sang năng lượng tái tạo, áp dụng các công nghệ sạch và thúc đẩy phát triển bền vững."""
    }
    
    selected_sample = st.selectbox("Chọn ví dụ mẫu:", list(sample_texts.keys()))
    
    if st.button("📋 Sử dụng văn bản mẫu"):
        st.session_state["manual_input"] = sample_texts[selected_sample]
        st.rerun()
    
    if selected_sample:
        st.text_area("Xem trước:", value=sample_texts[selected_sample], height=150, disabled=True)

with tab3:
    uploaded_file = st.file_uploader("Chọn file text (.txt)", type=['txt'])
    if uploaded_file is not None:
        file_content = str(uploaded_file.read(), "utf-8")
        st.text_area("Nội dung file:", value=file_content, height=150, disabled=True)
        if st.button("📁 Sử dụng nội dung file"):
            st.session_state["manual_input"] = file_content
            st.rerun()

if st.button("🤖 Tóm tắt văn bản", type="primary", use_container_width=True):
    text_to_summarize = " ".join(st.session_state.get("manual_input", "").split())
    
    if not text_to_summarize:
        st.error("❌ Vui lòng nhập văn bản cần tóm tắt!")
    elif not is_healthy:
        st.error("❌ API không khả dụng. Hãy khởi động API server trước!")
    else:
        with st.spinner("🔄 Đang tóm tắt văn bản..."):
            try:
                # Gọi API
                payload = {
                    "document": text_to_summarize,
                    "max_new_tokens": max_new_tokens,
                    "temperature": temperature,
                    "top_p": top_p
                }
                
                # LOG REQUEST
                logger.info("=" * 80)
                logger.info("NEW SUMMARIZATION REQUEST")
                logger.info(f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                logger.info(f"Document length: {len(text_to_summarize)} characters")
                logger.info(f"Document preview: {text_to_summarize[:200]}...")
                logger.info(f"Parameters: max_tokens={max_new_tokens}, temp={temperature}, top_p={top_p}")
                logger.info("-" * 80)
                
                start_time = time.time()
                response = requests.post(f"{API_BASE_URL}/summarize", json=payload, timeout=240)
                
                if response.status_code == 200:
                    result = response.json()
                    
                    processing_time = time.time() - start_time
                    
                    # LOG RESPONSE
                    logger.info("REQUEST SUCCESS")
                    logger.info(f"API processing time: {result['processing_time']}s")
                    logger.info(f"Total request time: {processing_time:.3f}s")
                    logger.info(f"Summary length: {result['output_length']} characters")
                    logger.info(f"Summary: {result['summary']}")
                    logger.info("=" * 80)
                    # Hiển thị kết quả
                    st.success("✅ Tóm tắt hoàn thành!")
                    
                    # Layout kết quả
                    col1, col2 = st.columns([3, 1])
                    
                    with col1:
                        st.subheader("📋 Kết quả tóm tắt")
                        st.markdown("**Văn bản gốc:**")
                        with st.expander("Xem văn bản gốc", expanded=False):
                            st.write(text_to_summarize)
                        
                        st.markdown("**Tóm tắt:**")
                        st.info(result["summary"])
                        
                        # Copy button
                        if st.button("📄 Copy tóm tắt"):
                            st.write("```")
                            st.write(result["summary"])
                            st.write("```")
                    
                    with col2:
                        st.subheader("📊 Thống kê")
                        st.metric("⏱️ Thời gian xử lý", f"{result['processing_time']}s")
                        st.metric("📏 Độ dài gốc", f"{result['input_length']} ký tự")
                        st.metric("📏 Độ dài tóm tắt", f"{result['output_length']} ký tự")
                        
                        compression_ratio = round((1 - result['output_length'] / result['input_length']) * 100, 1)
                        st.metric("📉 Tỷ lệ nén", f"{compression_ratio}%")
                        
                        st.divider()
                        
                        st.markdown("**Tham số sử dụng:**")
                        st.text(f"Max length: {max_new_tokens }")
                        st.text(f"Temperature: {temperature}")
                        st.text(f"Top-p: {top_p}")
                        
                        current_time = datetime.now().strftime("%H:%M:%S")
                        st.text(f"Thời gian: {current_time}")
                
                else:
                    st.error(f"❌ Lỗi API: {response.status_code}")
                    st.json(response.json())
                    
            except requests.exceptions.Timeout:
                st.error("❌ Timeout: Quá trình tóm tắt mất quá nhiều thời gian!")
            except requests.exceptions.RequestException as e:
                st.error(f"❌ Lỗi kết nối: {e}")
            except Exception as e:
                st.error(f"❌ Lỗi không xác định: {e}")

# ====== Footer ======
st.divider()
st.markdown("""
<div style='text-align: center; color: gray;'>
    <p>🤖 Powered by Gemma-2 | 🚀 Built with Streamlit | 💡 Vietnamese Text Summarization</p>
</div>
""", unsafe_allow_html=True)
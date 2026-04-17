import streamlit as st
import pandas as pd
from datetime import datetime
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px
import json

# Import NLP truyền thống (Dùng làm phương án dự phòng)
try:
    from underthesea import sentiment, word_tokenize
except ImportError:
    sentiment = lambda x: "neutral"
    word_tokenize = lambda x: x.split()

# Import Gemini API
import google.generativeai as genai

# ============================================================
# CẤU HÌNH TRANG
# ============================================================
st.set_page_config(page_title="SV-Feedback AI Pro", page_icon="🎓", layout="wide")

# ============================================================
# STATE MANAGEMENT
# ============================================================
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "history" not in st.session_state:
        st.session_state.history = []

# ============================================================
# LOGIC PHÂN TÍCH (Kết hợp Local NLP & Gemini API)
# ============================================================
@st.cache_data
def local_nlp_analyze(text):
    stopwords = {"và", "của", "là", "có", "rất", "em", "thầy", "cô", "này", "với", "cho", "các", "những", "một", "thì", "mà", "như"}
    label = sentiment(text) or "neutral"
    words = word_tokenize(text.lower())
    keywords = [w for w in words if w.isalnum() and w not in stopwords]
    return label, keywords, 0.7

def api_nlp_analyze(text, api_key):
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"""
        Phân tích câu phản hồi của sinh viên sau đây: "{text}"
        Trả về kết quả DƯỚI DẠNG JSON CHUẨN xác với định dạng sau, không thêm text bên ngoài:
        {{
            "label": "positive" (nếu khen) hoặc "negative" (nếu chê) hoặc "neutral" (nếu bình thường),
            "score": 0.95 (điểm tin cậy từ 0.0 đến 1.0),
            "keywords": ["từ khóa 1", "từ khóa 2", "từ khóa 3"] (tối đa 5 từ khóa quan trọng nhất)
        }}
        """
        response = model.generate_content(prompt)
        # Lọc chuỗi JSON từ response (phòng trường hợp AI trả về markdown)
        result_str = response.text.strip().replace('```json', '').replace('```', '')
        data = json.loads(result_str)
        return data.get("label", "neutral"), data.get("keywords", []), data.get("score", 0.9)
    except Exception as e:
        st.toast(f"Lỗi API: {e}. Đang dùng phân tích Local (Underthesea).", icon="⚠️")
        return local_nlp_analyze(text)

def analyze_feedback(text: str, api_key: str, use_api: bool) -> dict:
    if not text or len(text.strip()) < 2:
        return {"text": text, "label": "neutral", "score": 0.0, "keywords": [], "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    
    if use_api and api_key:
        label, keywords, score = api_nlp_analyze(text, api_key)
    else:
        label, keywords, score = local_nlp_analyze(text)
    
    return {
        "text": text,
        "label": label,
        "score": score,
        "keywords": keywords,
        "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }

# ============================================================
# GIAO DIỆN CHÍNH
# ============================================================
def main():
    init_session_state()

    # ── SIDEBAR ──
    with st.sidebar:
        st.image("https://cdn-icons-png.flaticon.com/512/4712/4712035.png", width=80)
        st.title("⚙️ Cấu hình Hệ thống")
        
        st.subheader("Trí tuệ nhân tạo (AI)")
        use_api = st.checkbox("Sử dụng Gemini API (Chính xác cao)", value=False)
        api_key = ""
        if use_api:
            api_key = st.text_input("Nhập Google Gemini API Key:", type="password")
            st.caption("Nhận API Key miễn phí tại: [Google AI Studio](https://aistudio.google.com/)")

        st.divider()
        st.subheader("📥 Nhập dữ liệu")
        uploaded_file = st.file_uploader("Tải lên file CSV/Excel", type=['csv', 'xlsx'])
        if uploaded_file and st.button("🚀 Phân tích hàng loạt"):
            try:
                df_upload = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
                with st.spinner("Đang xử lý toàn bộ file..."):
                    for text in df_upload.iloc[:, 0].dropna():
                        res = analyze_feedback(str(text), api_key, use_api)
                        st.session_state.history.append(res)
                st.success(f"Đã phân tích {len(df_upload)} phản hồi!")
            except Exception as e:
                st.error(f"Lỗi đọc file: {e}")

    # ── MAIN AREA: TABS ──
    st.title("🤖 Hệ thống Phân tích Phản hồi Sinh viên")
    
    # Chia giao diện thành 3 tab chuyên nghiệp
    tab1, tab2, tab3 = st.tabs(["💬 Trợ lý Phân tích", "📊 Dashboard Thống kê", "📋 Bảng Dữ liệu Lịch sử"])

    # --- TAB 1: GIAO DIỆN CHAT ---
    with tab1:
        st.markdown("### Nhập phản hồi trực tiếp")
        # Khung hiển thị chat
        chat_container = st.container(height=400)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    st.markdown(msg["content"])

        # Ô nhập liệu
        if prompt := st.chat_input("Nhập ý kiến sinh viên (VD: Bài giảng rất hay và sinh động...)"):
            st.session_state.messages.append({"role": "user", "content": prompt})
            st.rerun()

        # Xử lý phản hồi mới nhất (nếu là user)
        if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
            user_text = st.session_state.messages[-1]["content"]
            with st.spinner("AI đang phân tích cảm xúc..."):
                result = analyze_feedback(user_text, api_key, use_api)
                st.session_state.history.append(result)
                
                # Tạo markdown trả lời
                emoji = {"positive": "🟢 Tích cực", "negative": "🔴 Tiêu cực", "neutral": "⚪ Trung lập"}
                answer = f"**Đánh giá:** {emoji.get(result['label'], '⚪ Trung lập')} (Tin cậy: {result['score']*100:.1f}%)\n\n"
                answer += f"**Từ khóa:** `{', '.join(result['keywords']) if result['keywords'] else 'Không có'}`"
                
                st.session_state.messages.append({"role": "assistant", "content": answer})
                st.rerun()

    # --- TAB 2: DASHBOARD THỐNG KÊ ---
    with tab2:
        if not st.session_state.history:
            st.info("Chưa có dữ liệu để thống kê. Hãy nhập phản hồi ở tab 'Trợ lý Phân tích'.")
        else:
            df = pd.DataFrame(st.session_state.history)
            
            # Metrics
            col1, col2, col3 = st.columns(3)
            col1.metric("Tổng số phản hồi", len(df))
            pos_count = len(df[df['label'] == 'positive'])
            col2.metric("Phản hồi Tích cực", f"{pos_count} ({(pos_count/len(df))*100:.1f}%)")
            neg_count = len(df[df['label'] == 'negative'])
            col3.metric("Phản hồi Tiêu cực", neg_count)

            st.divider()

            # Biểu đồ và WordCloud
            col_chart, col_wc = st.columns(2)
            
            with col_chart:
                st.subheader("📈 Tỷ lệ Cảm xúc")
                sentiment_counts = df['label'].value_counts().reset_index()
                sentiment_counts.columns = ['Cảm xúc', 'Số lượng']
                # Đổi tên nhãn cho đẹp
                sentiment_counts['Cảm xúc'] = sentiment_counts['Cảm xúc'].map({"positive": "Tích cực", "negative": "Tiêu cực", "neutral": "Trung lập"})
                color_map = {"Tích cực": "#2ecc71", "Tiêu cực": "#e74c3c", "Trung lập": "#95a5a6"}
                
                fig = px.pie(sentiment_counts, values='Số lượng', names='Cảm xúc', color='Cảm xúc', color_discrete_map=color_map, hole=0.4)
                st.plotly_chart(fig, use_container_width=True)

            with col_wc:
                st.subheader("☁️ Đám mây Từ khóa (Word Cloud)")
                all_keywords = []
                for k_list in df['keywords']:
                    all_keywords.extend(k_list)
                
                text_cloud = " ".join(all_keywords).strip()
                if text_cloud:
                    try:
                        wc = WordCloud(width=600, height=450, background_color="white", colormap="viridis").generate(text_cloud)
                        fig_wc, ax_wc = plt.subplots()
                        ax_wc.imshow(wc, interpolation='bilinear')
                        ax_wc.axis("off")
                        st.pyplot(fig_wc)
                    except ValueError:
                        st.caption("Chưa đủ từ khóa hợp lệ.")
                else:
                    st.caption("Chưa có từ khóa nào.")

    # --- TAB 3: BẢNG LỊCH SỬ ---
    with tab3:
        if not st.session_state.history:
            st.info("Bảng dữ liệu trống.")
        else:
            st.subheader("📋 Chi tiết Lịch sử Phân tích")
            df_history = pd.DataFrame(st.session_state.history)
            
            # Format lại bảng cho đẹp
            df_display = df_history.copy()
            df_display['keywords'] = df_display['keywords'].apply(lambda x: ", ".join(x))
            df_display['score'] = df_display['score'].apply(lambda x: f"{x*100:.1f}%")
            df_display['label'] = df_display['label'].map({"positive": "🟢 Tích cực", "negative": "🔴 Tiêu cực", "neutral": "⚪ Trung lập"})
            
            st.dataframe(df_display, use_container_width=True, height=400)
            
            # Nút Export
            csv = df_display.to_csv(index=False).encode('utf-8-sig')
            st.download_button(label="📥 Xuất dữ liệu ra file CSV", data=csv, file_name="nhat_ky_phan_tich.csv", mime="text/csv")

if __name__ == "__main__":
    main()
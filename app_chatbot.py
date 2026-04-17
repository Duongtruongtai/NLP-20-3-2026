import streamlit as st
import pandas as pd
from datetime import datetime
import io
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import plotly.express as px

# Import NLP truyền thống (Chạy 100% Local)
try:
    from underthesea import sentiment, word_tokenize
except ImportError:
    st.error("Vui lòng cài đặt underthesea: pip install underthesea")
    sentiment = lambda x: "neutral"
    word_tokenize = lambda x: x.split()

# ============================================================
# CẤU HÌNH TRANG
# ============================================================
st.set_page_config(page_title="Phân tích Phản hồi SV", page_icon="🎓", layout="wide")

# CSS tinh chỉnh cho giao diện gọn gàng hơn
st.markdown("""
<style>
    /* Làm viền mỏng và bo góc cho các khối */
    div[data-testid="stMetric"] {
        background-color: #f8f9fa;
        border: 1px solid #e9ecef;
        padding: 15px;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.05);
    }
    /* Chỉnh màu cho dark mode/light mode tự động tốt hơn */
    @media (prefers-color-scheme: dark) {
        div[data-testid="stMetric"] {
            background-color: #1e1e1e;
            border: 1px solid #333;
        }
    }
</style>
""", unsafe_allow_html=True)

# ============================================================
# STATE MANAGEMENT
# ============================================================
def init_session_state():
    if "messages" not in st.session_state:
        st.session_state.messages = [{"role": "assistant", "content": "👋 Xin chào! Nhập phản hồi sinh viên để tôi phân tích cảm xúc và trích xuất từ khóa.", "is_greeting": True}]
    if "history" not in st.session_state:
        st.session_state.history = []

# ============================================================
# LOGIC PHÂN TÍCH (Chỉ dùng Underthesea)
# ============================================================
@st.cache_data
def local_nlp_analyze(text):
    stopwords = {"và", "của", "là", "có", "rất", "em", "thầy", "cô", "này", "với", "cho", "các", "những", "một", "thì", "mà", "như"}
    label = sentiment(text) or "neutral"
    words = word_tokenize(text.lower())
    keywords = [w for w in words if w.isalnum() and w not in stopwords]
    score = 0.85 if label != "neutral" else 0.60
    return {"label": label, "score": score, "tokens": len(words), "language": "vi", "keywords": keywords}

def analyze_feedback(text: str) -> dict:
    if not text or len(text.strip()) < 2: return None
    result_data = local_nlp_analyze(text)
    result_data["text"] = text
    result_data["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return result_data

# ============================================================
# HÀM XUẤT EXCEL
# ============================================================
def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Lich_Su_Phan_Tich')
    return output.getvalue()

# ============================================================
# MAIN APP
# ============================================================
def main():
    init_session_state()

    # ── THIẾT KẾ SIDEBAR (CHỈ CHỨA ĐIỀU KHIỂN) ──
    with st.sidebar:
        st.title("⚙️ Bảng Điều Khiển")
        st.markdown("Quản lý dữ liệu và thiết lập.")
        
        st.divider()
        st.markdown("📂 **Phân tích hàng loạt**")
        uploaded_file = st.file_uploader("Upload CSV / Excel", type=['csv', 'xlsx'], label_visibility="collapsed")
        
        if uploaded_file and st.button("🚀 Xử lý File", use_container_width=True):
            df_upload = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
            with st.spinner("Đang xử lý dữ liệu..."):
                for text in df_upload.iloc[:, 0].dropna():
                    res = analyze_feedback(str(text))
                    if res: st.session_state.history.append(res)
            st.rerun()

        st.divider()
        st.markdown("🛠️ **Công cụ Lịch sử**")
        if st.session_state.history:
            df_history = pd.DataFrame(st.session_state.history)
            excel_data = to_excel(df_history)
            st.download_button("⬇️ Tải xuống Excel", data=excel_data, file_name="Ket_qua_Phan_tich.xlsx", mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", use_container_width=True)
            
            if st.button("🗑️ Xóa toàn bộ dữ liệu", type="primary", use_container_width=True):
                st.session_state.history = []
                st.session_state.messages = [{"role": "assistant", "content": "👋 Xin chào! Nhập phản hồi sinh viên để tôi phân tích cảm xúc và trích xuất từ khóa.", "is_greeting": True}]
                st.rerun()

    # ── MÀN HÌNH CHÍNH (CHIA TABS) ──
    st.title("🤖 Trợ lý Phân tích Phản hồi Sinh viên")
    
    # Tạo 2 Tab riêng biệt cho không gian rộng rãi
    tab_chat, tab_dashboard = st.tabs(["💬 Chat Phân tích", "📊 Dashboard Tổng hợp"])

    # ---------- TAB 1: CHAT INTERFACE ----------
    with tab_chat:
        emoji_map = {"positive": "😊 Tích cực", "negative": "😟 Tiêu cực", "neutral": "😐 Trung lập"}
        color_map = {"positive": "green", "negative": "red", "neutral": "gray"}
        
        # Vùng chứa chat (giới hạn chiều cao để form nhập luôn ở dưới nếu nội dung quá dài)
        chat_container = st.container(height=500, border=False)
        with chat_container:
            for msg in st.session_state.messages:
                with st.chat_message(msg["role"]):
                    if msg.get("is_greeting"):
                        st.markdown(msg["content"])
                    elif msg["role"] == "user":
                        st.markdown(msg["content"]) 
                    else:
                        res = msg["result_data"]
                        label = res.get('label', 'neutral')
                        st.markdown(f"**Kết quả:** :{color_map[label]}[**{emoji_map[label]}**] (Độ tin cậy: {res['score']*100:.0f}%)")
                        
                        keywords = res.get('keywords', [])
                        if keywords:
                            st.markdown(f"**Từ khóa:** `{', '.join(keywords)}`")

        # Ô nhập liệu đặt ngay dưới tab chat
        if prompt := st.chat_input("Nhập ý kiến của sinh viên vào đây..."):
            st.session_state.messages.append({"role": "user", "content": prompt})
            result = analyze_feedback(prompt)
            if result:
                st.session_state.history.append(result)
                st.session_state.messages.append({"role": "assistant", "content": "", "result_data": result})
            st.rerun()

    # ---------- TAB 2: DASHBOARD & LỊCH SỬ ----------
    with tab_dashboard:
        if not st.session_state.history:
            st.info("Chưa có dữ liệu thống kê. Hãy upload file hoặc chat để hệ thống phân tích.")
        else:
            df = pd.DataFrame(st.session_state.history)
            
            # 1. HÀNG SỐ LIỆU TỔNG QUAN (Metrics)
            st.markdown("### Chỉ số Tổng quan")
            col1, col2, col3, col4 = st.columns(4)
            total = len(df)
            pos_count = len(df[df['label'] == 'positive'])
            neg_count = len(df[df['label'] == 'negative'])
            neu_count = len(df[df['label'] == 'neutral'])
            
            col1.metric("📝 Tổng số phản hồi", total)
            col2.metric("🟢 Tích cực", f"{pos_count}", f"{(pos_count/total)*100:.1f}%")
            col3.metric("🔴 Tiêu cực", f"{neg_count}", f"-{(neg_count/total)*100:.1f}%")
            col4.metric("⚪ Trung lập", f"{neu_count}")

            st.divider()

            # 2. HÀNG BIỂU ĐỒ (Charts)
            st.markdown("### Phân tích Trực quan")
            col_chart1, col_chart2 = st.columns(2)
            
            with col_chart1:
                # Biểu đồ tròn
                st.markdown("**Tỷ lệ Cảm xúc**")
                labels_map_vn = {"positive": "Tích cực", "negative": "Tiêu cực", "neutral": "Trung lập"}
                df['Nhãn'] = df['label'].map(labels_map_vn)
                px_color_map = {"Tích cực": "#2ecc71", "Tiêu cực": "#e74c3c", "Trung lập": "#95a5a6"}
                
                fig_pie = px.pie(df, names='Nhãn', color='Nhãn', color_discrete_map=px_color_map, hole=0.4)
                fig_pie.update_layout(margin=dict(t=20, b=20, l=0, r=0), height=300, paper_bgcolor="rgba(0,0,0,0)")
                st.plotly_chart(fig_pie, use_container_width=True)
                
            with col_chart2:
                # Đám mây từ khóa
                st.markdown("**Từ khóa Xuất hiện Nhiều nhất**")
                all_keywords = [word for k_list in df['keywords'] if isinstance(k_list, list) for word in k_list]
                if all_keywords:
                    text_cloud = " ".join(all_keywords)
                    try:
                        wc = WordCloud(width=600, height=300, background_color=None, mode="RGBA", colormap="viridis").generate(text_cloud)
                        fig_wc, ax_wc = plt.subplots(facecolor='none')
                        ax_wc.imshow(wc, interpolation='bilinear')
                        ax_wc.axis("off")
                        st.pyplot(fig_wc)
                    except:
                        st.caption("Chưa đủ từ khóa hợp lệ để vẽ mây từ.")

            st.divider()

            # 3. BẢNG DỮ LIỆU CHI TIẾT
            st.markdown("### Dữ liệu Lịch sử")
            df_display = df[['timestamp', 'text', 'Nhãn', 'score']].copy()
            df_display['score'] = df_display['score'].apply(lambda x: f"{x*100:.0f}%")
            df_display.columns = ['Thời gian', 'Nội dung phản hồi', 'Cảm xúc', 'Độ tin cậy']
            st.dataframe(df_display, use_container_width=True, hide_index=True, height=250)

if __name__ == "__main__":
    main()
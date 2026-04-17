
import streamlit as st
import pandas as pd
from underthesea import pos_tag
import altair as alt

# -----------------------------
# Cấu hình trang
# -----------------------------
st.set_page_config(
    page_title="Xử lý ngôn ngữ tiếng Việt",
    page_icon="🇻🇳",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# CSS tùy chỉnh để giao diện đẹp hơn
# -----------------------------
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1E3A8A;
        font-weight: 700;
        margin-bottom: 0.5rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #4B5563;
        margin-bottom: 2rem;
    }
    .token-box {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #3B82F6;
    }
    .pos-box {
        background-color: #F3F4F6;
        border-radius: 10px;
        padding: 1rem;
        margin: 0.5rem 0;
        border-left: 5px solid #10B981;
    }
    .legend-item {
        display: inline-block;
        margin-right: 1rem;
        margin-bottom: 0.5rem;
        padding: 0.3rem 1rem;
        border-radius: 20px;
        color: white;
        font-weight: 500;
    }
    .highlighted-text {
        background-color: #F9FAFB;
        border-radius: 10px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        font-size: 1.2rem;
        line-height: 2;
    }
    .stButton button {
        background-color: #1E3A8A;
        color: white;
        font-weight: 600;
        border-radius: 10px;
        padding: 0.5rem 2rem;
        border: none;
        transition: all 0.3s;
    }
    .stButton button:hover {
        background-color: #2563EB;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
    }
    .info-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------
# Dữ liệu nhãn và màu sắc
# -----------------------------
POS_DATA = {
    "N": {"name": "Danh từ", "color": "#FF6B6B", "description": "Chỉ người, vật, hiện tượng"},
    "Np": {"name": "Danh từ riêng", "color": "#FF4444", "description": "Tên riêng"},
    "Nc": {"name": "Danh từ chỉ loại", "color": "#FF8888", "description": "Cái, con, chiếc..."},
    "Nu": {"name": "Danh từ đơn vị", "color": "#FFAAAA", "description": "mét, kg, lít..."},
    "V": {"name": "Động từ", "color": "#4ECDC4", "description": "Hành động, trạng thái"},
    "A": {"name": "Tính từ", "color": "#FFE66D", "description": "Tính chất, đặc điểm"},
    "P": {"name": "Đại từ", "color": "#A8E6CF", "description": "Tôi, bạn, nó..."},
    "R": {"name": "Phó từ", "color": "#95E1D3", "description": "rất, quá, lắm..."},
    "L": {"name": "Định từ", "color": "#DDA0DD", "description": "những, các, mọi..."},
    "M": {"name": "Số từ", "color": "#87CEEB", "description": "một, hai, ba..."},
    "E": {"name": "Giới từ", "color": "#FFA07A", "description": "trên, dưới, trong..."},
    "C": {"name": "Liên từ", "color": "#98D8C8", "description": "và, hoặc, nhưng..."},
    "I": {"name": "Thán từ", "color": "#F7DC6F", "description": "ôi, trời ơi..."},
    "T": {"name": "Trợ từ", "color": "#BB8FCE", "description": "nhé, ạ, hử..."},
    "CH": {"name": "Dấu câu", "color": "#BDC3C7", "description": ". , ! ? ..."}
}

# -----------------------------
# Tiêu đề chính
# -----------------------------
st.markdown('<p class="main-header">🇻🇳 Xử lý ngôn ngữ tiếng Việt</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Công cụ tách từ, gán nhãn từ loại và trực quan hóa dữ liệu</p>', unsafe_allow_html=True)

# -----------------------------
# Sidebar - Thông tin sinh viên và bảng màu
# -----------------------------
with st.sidebar:
    st.markdown("## 📋 Thông tin sinh viên")
    
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("**MSSV**")
        st.markdown("123001011")
        st.markdown("")
    with col2:
        st.markdown("**Họ tên**")
        st.markdown("Dương Tài")
        st.markdown("")
    
    st.markdown("---")
    
    st.markdown("## 🎨 Bảng màu từ loại")
    st.markdown("Tra cứu nhanh ý nghĩa các nhãn và màu sắc tương ứng:")
    
    # Tạo bảng màu dạng lưới đẹp mắt
    legend_html = ""
    for tag, info in POS_DATA.items():
        legend_html += f'<span class="legend-item" style="background-color: {info["color"]};">{tag} - {info["name"]}</span>'
    st.markdown(f'<div style="margin-bottom: 1rem;">{legend_html}</div>', unsafe_allow_html=True)
    
    # Bảng chi tiết dạng dataframe
    df_legend = pd.DataFrame([
        {"Nhãn": tag, "Tên": info["name"], "Mô tả": info["description"], "Màu": info["color"]}
        for tag, info in POS_DATA.items()
    ])
    
    # Hiển thị bảng có màu sắc
    for i, row in df_legend.iterrows():
        st.markdown(
            f'<div style="display: flex; align-items: center; margin-bottom: 0.3rem;">'
            f'<div style="width: 30px; height: 30px; background-color: {row["Màu"]}; border-radius: 5px; margin-right: 10px;"></div>'
            f'<div><strong>{row["Nhãn"]}</strong> - {row["Tên"]}<br><small>{row["Mô tả"]}</small></div>'
            f'</div>',
            unsafe_allow_html=True
        )

# -----------------------------
# Main content - Nhập liệu
# -----------------------------
col_input, col_info = st.columns([3, 1])

with col_input:
    text = st.text_area(
        "📝 Nhập văn bản tiếng Việt:",
        "Hệ thống phân loại bình luận tiếng Việt rất chính xác. Tôi rất thích học môn Xử lý ngôn ngữ tự nhiên!",
        height=150,
        placeholder="Ví dụ: Tôi đang học ngôn ngữ học tại trường đại học."
    )

with col_info:
    st.markdown('<div class="info-card">', unsafe_allow_html=True)
    st.markdown("**📊 Hướng dẫn sử dụng**")
    st.markdown("1. Nhập văn bản tiếng Việt")
    st.markdown("2. Nhấn nút **Phân tích**")
    st.markdown("3. Xem kết quả token, POS tag")
    st.markdown("4. Tải file CSV hoặc xem highlight")
    st.markdown('</div>', unsafe_allow_html=True)

# Nút phân tích
col1, col2, col3 = st.columns([1, 1, 1])
with col2:
    analyze_clicked = st.button("🔍 PHÂN TÍCH VĂN BẢN", type="primary", use_container_width=True)

# -----------------------------
# Xử lý và hiển thị kết quả
# -----------------------------
if analyze_clicked:
    # Nhiệm vụ 4: Kiểm tra input rỗng
    if not text or not text.strip():
        st.error("⚠️ Vui lòng nhập văn bản trước khi phân tích!")
    else:
        with st.spinner("🔄 Đang xử lý..."):
            try:
                tagged_words = pos_tag(text)
                
                # Tách token và nhãn
                tokens = [word for word, pos in tagged_words]
                pos_tags = [pos for word, pos in tagged_words]
                
                # Tạo DataFrame kết quả
                result_df = pd.DataFrame({
                    "Token": tokens,
                    "POS Tag": pos_tags,
                    "Loại từ": [POS_DATA.get(tag, {}).get("name", "Khác") for tag in pos_tags],
                    "Mô tả": [POS_DATA.get(tag, {}).get("description", "") for tag in pos_tags]
                })
                
                # -----------------------------
                # Hiển thị kết quả 2 cột (Nhiệm vụ 1 & 2)
                # -----------------------------
                st.markdown("---")
                st.markdown("## 📊 Kết quả phân tích")
                
                col_left, col_right = st.columns(2)
                
                with col_left:
                    st.markdown('<div class="token-box">', unsafe_allow_html=True)
                    st.markdown("### 🔹 Danh sách token")
                    for i, token in enumerate(tokens, 1):
                        st.markdown(f"{i}. {token}")
                    st.markdown('</div>', unsafe_allow_html=True)
                
                with col_right:
                    st.markdown('<div class="pos-box">', unsafe_allow_html=True)
                    st.markdown("### 🔸 Nhãn từ loại")
                    for i, (tag, token) in enumerate(zip(pos_tags, tokens), 1):
                        color = POS_DATA.get(tag, {}).get("color", "#000000")
                        name = POS_DATA.get(tag, {}).get("name", tag)
                        st.markdown(
                            f"{i}. <span style='color:{color}; font-weight:600;'>{tag}</span> - {name}",
                            unsafe_allow_html=True
                        )
                    st.markdown('</div>', unsafe_allow_html=True)
                
                # -----------------------------
                # Highlight màu sắc (Nhiệm vụ 6)
                # -----------------------------
                st.markdown("---")
                st.markdown("## 🎨 Văn bản highlight theo từ loại")
                
                # Tạo HTML highlight
                html_parts = []
                for word, tag in tagged_words:
                    color = POS_DATA.get(tag, {}).get("color", "#000000")
                    html_parts.append(
                        f"<span style='color:{color}; font-weight:600; background-color: {color}20; padding: 2px 4px; border-radius: 4px; margin: 0 2px;'>{word}</span>"
                    )
                highlighted_html = " ".join(html_parts)
                
                st.markdown(
                    f'<div class="highlighted-text">{highlighted_html}</div>',
                    unsafe_allow_html=True
                )
                
                # Hiển thị chú thích nhanh
                st.markdown("**Chú thích màu:**")
                legend_small = ""
                for tag, info in POS_DATA.items():
                    if tag in set(pos_tags):
                        legend_small += f'<span style="display:inline-block; background-color:{info["color"]}; width:20px; height:20px; border-radius:4px; margin-right:5px;"></span> {tag} - {info["name"]} '
                st.markdown(f'<div style="background-color:#F9FAFB; padding:0.8rem; border-radius:8px;">{legend_small}</div>', unsafe_allow_html=True)
                
                # -----------------------------
                # Export CSV (Nhiệm vụ 5)
                # -----------------------------
                st.markdown("---")
                st.markdown("## 📥 Tải kết quả")
                
                col_csv1, col_csv2, col_csv3 = st.columns([1, 2, 1])
                with col_csv2:
                    csv_data = result_df.to_csv(index=False, encoding='utf-8-sig')
                    st.download_button(
                        label="📥 Tải xuống file CSV",
                        data=csv_data,
                        file_name=f"ket_qua_pos_{pd.Timestamp.now().strftime('%Y%m%d_%H%M%S')}.csv",
                        mime="text/csv",
                        use_container_width=True
                    )
                
                # -----------------------------
                # Bảng dữ liệu chi tiết
                # -----------------------------
                with st.expander("📋 Xem bảng dữ liệu chi tiết"):
                    # Thêm cột màu sắc để hiển thị trong bảng
                    display_df = result_df.copy()
                    display_df["Màu"] = [POS_DATA.get(tag, {}).get("color", "#000000") for tag in pos_tags]
                    
                    # Tạo cột hiển thị màu dạng HTML
                    display_df["Màu hiển thị"] = display_df["Màu"].apply(
                        lambda x: f'<div style="background-color:{x}; width:30px; height:20px; border-radius:4px;"></div>'
                    )
                    
                    st.write(display_df[["Token", "POS Tag", "Loại từ", "Mô tả"]].to_html(escape=False, index=False), unsafe_allow_html=True)
                
                # Thống kê nhanh
                st.markdown("---")
                st.markdown("## 📈 Thống kê từ loại")
                stats = result_df["Loại từ"].value_counts().reset_index()
                stats.columns = ["Loại từ", "Số lượng"]
                
                col_stat1, col_stat2 = st.columns(2)
                with col_stat1:
                    st.bar_chart(stats.set_index("Loại từ"))
                with col_stat2:
                    st.dataframe(stats, use_container_width=True, hide_index=True)
                
            except Exception as e:
                st.error(f"❌ Đã xảy ra lỗi: {str(e)}")

# Footer
st.markdown("---")
st.markdown(
    '<div style="text-align: center; color: #6B7280; padding: 1rem;">'
    '© 2026 - Cơ Sở Ngôn Ngữ Học | Đại Học Lạc Hồng<br>'
    'Công nghệ: Python, Streamlit, underthesea, pandas'
    '</div>',
    unsafe_allow_html=True
)

# app.py
import streamlit as st
from underthesea import word_tokenize, pos_tag

st.set_page_config(page_title="Demo POS Tagging Tiếng Việt", layout="wide")

st.title("Demo POS Tagging Tiếng Việt với Streamlit")
st.write("Nhập một câu tiếng Việt, ứng dụng sẽ tách từ và gán nhãn từ loại.")

# Input
text = st.text_area(
    "Nhập câu tiếng Việt ở đây:",
    "Hệ thống phân loại bình luận tiếng Việt rất chính xác.",
    height=100
)

analyze_clicked = st.button("🔍 Phân tích", type="primary", width="stretch")

col1, col2 = st.columns(2)

import pandas as pd
import base64

# Bảng giải thích nhãn từ loại
POS_TAGS_EXPLANATION = {
    "N": "Danh từ",
    "Np": "Danh từ riêng",
    "Nc": "Danh từ chỉ loại",
    "Nu": "Danh từ đơn vị",
    "V": "Động từ",
    "A": "Tính từ",
    "P": "Đại từ",
    "R": "Phó từ",
    "L": "Định từ",
    "M": "Số từ",
    "E": "Giới từ",
    "C": "Liên từ",
    "I": "Thán từ",
    "T": "Trợ từ, tiểu từ",
    "B": "Từ gốc Hán-Việt",
    "Y": "Từ viết tắt",
    "S": "Từ ngoại lai",
    "X": "Từ không phân loại",
    "CH": "Dấu câu",
}

# Màu cho từng loại từ loại
POS_COLORS = {
    "N": "#FF6B6B",
    "Np": "#FF4444",
    "Nc": "#FF8888",
    "Nu": "#FFAAAA",
    "V": "#4ECDC4",
    "A": "#FFE66D",
    "P": "#A8E6CF",
    "R": "#95E1D3",
    "L": "#DDA0DD",
    "M": "#87CEEB",
    "E": "#FFA07A",
    "C": "#98D8C8",
    "I": "#F7DC6F",
    "T": "#BB8FCE",
    "B": "#F0B27A",
    "Y": "#AED6F1",
    "S": "#F5B7B1",
    "X": "#D5DBDB",
    "CH": "#BDC3C7",
}

# TODO: Thêm xử lý tokenize và hiển thị kết quả ở col1
# TODO: Thêm xử lý POS tagging và hiển thị kết quả ở col2
# TODO: Thêm bảng giải thích các nhãn từ loại (POS tags)
# TODO: Thêm xử lý lỗi khi input rỗng
# TODO: Thêm tính năng export kết quả ra file CSV
# TODO: Thêm highlight màu cho từng loại từ loại khác nhau


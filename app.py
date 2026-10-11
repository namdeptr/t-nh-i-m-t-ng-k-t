import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from io import BytesIO

st.set_page_config(page_title="Quản lý điểm sinh viên", page_icon="🎓", layout="wide")

st.title("🎓 Hệ thống quản lý và phân tích điểm sinh viên")
st.caption("Python • Pandas • Streamlit")

# ---------- Dữ liệu mẫu ----------
@st.cache_data
def sample_data():
    return pd.DataFrame({
        "Mã sinh viên": ["SV001", "SV002", "SV003", "SV004", "SV005",
                         "SV006", "SV007", "SV008", "SV009", "SV010"],
        "Họ tên": ["Nguyễn An", "Trần Bình", "Lê Chi", "Phạm Dũng", "Hoàng Giang",
                   "Vũ Hạnh", "Đỗ Khoa", "Bùi Lan", "Đặng Minh", "Ngô Phúc"],
        "Chuyên cần": [9.0, 8.0, 10.0, 7.5, 9.5, 6.0, 8.5, 7.0, 9.0, 5.5],
        "Giữa kỳ":    [8.5, 7.0, 9.5, 6.5, 8.0, 5.0, 7.5, 6.0, 9.0, 4.5],
        "Cuối kỳ":    [9.0, 7.5, 9.0, 6.0, 8.5, 4.5, 8.0, 5.5, 8.5, 4.0],
    })

if "data" not in st.session_state:
    st.session_state.data = sample_data()

# ---------- Hàm tính toán ----------
def calculate(df, weights):
    df = df.copy()
    score_cols = ["Chuyên cần", "Giữa kỳ", "Cuối kỳ"]
    for col in score_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")
    df["Điểm tổng kết"] = (
        df["Chuyên cần"] * weights[0]
        + df["Giữa kỳ"] * weights[1]
        + df["Cuối kỳ"] * weights[2]
    ).round(2)

    def classify(score):
        if pd.isna(score):
            return "Chưa đủ dữ liệu"
        if score >= 9:
            return "Xuất sắc"
        if score >= 8:
            return "Giỏi"
        if score >= 6.5:
            return "Khá"
        if score >= 5:
            return "Trung bình"
        return "Yếu"

    df["Xếp loại"] = df["Điểm tổng kết"].apply(classify)
    return df

# ---------- Thanh bên ----------
st.sidebar.header("⚙️ Cài đặt")
st.sidebar.write("Điều chỉnh trọng số tính điểm:")
w_cc = st.sidebar.slider("Chuyên cần (%)", 0, 100, 10)
w_gk = st.sidebar.slider("Giữa kỳ (%)", 0, 100, 30)
w_ck = st.sidebar.slider("Cuối kỳ (%)", 0, 100, 60)
total_weight = w_cc + w_gk + w_ck
if total_weight != 100:
    st.sidebar.warning(f"Tổng trọng số hiện là {total_weight}%. Hãy chỉnh về 100%.")
weights = [w_cc / 100, w_gk / 100, w_ck / 100]

st.sidebar.markdown("---")
uploaded = st.sidebar.file_uploader("Tải tệp CSV lên (không bắt buộc)", type=["csv"])
if uploaded is not None:
    try:
        imported = pd.read_csv(uploaded)
        required = ["Mã sinh viên", "Họ tên", "Chuyên cần", "Giữa kỳ", "Cuối kỳ"]
        if all(c in imported.columns for c in required):
            st.session_state.data = imported[required].copy()
            st.sidebar.success("Đã tải dữ liệu CSV.")
        else:
            st.sidebar.error("CSV cần có các cột: " + ", ".join(required))
    except Exception as e:
        st.sidebar.error(f"Không đọc được CSV: {e}")

# ---------- Nhập/chỉnh sửa dữ liệu ----------
st.subheader("1. Bảng dữ liệu sinh viên")
st.write("Bạn có thể sửa trực tiếp ô trong bảng hoặc thêm sinh viên bằng cách nhập một dòng mới.")
edited = st.data_editor(
    st.session_state.data,
    num_rows="dynamic",
    use_container_width=True,
    key="student_editor",
    column_config={
        "Mã sinh viên": st.column_config.TextColumn("Mã sinh viên", required=True),
        "Họ tên": st.column_config.TextColumn("Họ tên", required=True),
        "Chuyên cần": st.column_config.NumberColumn("Chuyên cần", min_value=0.0, max_value=10.0, step=0.5),
        "Giữa kỳ": st.column_config.NumberColumn("Giữa kỳ", min_value=0.0, max_value=10.0, step=0.5),
        "Cuối kỳ": st.column_config.NumberColumn("Cuối kỳ", min_value=0.0, max_value=10.0, step=0.5),
    },
)
st.session_state.data = edited.copy()

# Kiểm tra dữ liệu
score_cols = ["Chuyên cần", "Giữa kỳ", "Cuối kỳ"]
for col in score_cols:
    edited[col] = pd.to_numeric(edited[col], errors="coerce")
valid_scores = edited[score_cols].apply(lambda s: s.between(0, 10) | s.isna()).all().all()
if not valid_scores:
    st.error("Điểm phải nằm trong khoảng 0–10. Vui lòng kiểm tra dữ liệu.")
    st.stop()
if total_weight != 100:
    st.info("Điểm tổng kết sẽ được tính theo trọng số hiện tại; nên đặt tổng trọng số bằng 100%.")

results = calculate(edited, weights)

st.subheader("2. Bảng điểm tổng kết")
search_name = st.text_input("🔎 Tìm theo mã sinh viên hoặc họ tên")
grade_options = ["Tất cả"] + [g for g in ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu", "Chưa đủ dữ liệu"]
                                  if g in results["Xếp loại"].values]
selected_grade = st.selectbox("Lọc theo xếp loại", grade_options)
view = results.copy()
if search_name:
    mask = (
        view["Mã sinh viên"].astype(str).str.contains(search_name, case=False, na=False)
        | view["Họ tên"].astype(str).str.contains(search_name, case=False, na=False)
    )
    view = view[mask]
if selected_grade != "Tất cả":
    view = view[view["Xếp loại"] == selected_grade]
st.dataframe(view, use_container_width=True, hide_index=True)

csv_bytes = results.to_csv(index=False).encode("utf-8-sig")
st.download_button("⬇️ Tải bảng điểm CSV", data=csv_bytes,
                   file_name="bang_diem_sinh_vien.csv", mime="text/csv")

# ---------- Thống kê ----------
st.subheader("3. Thống kê cơ bản")
numeric_scores = results["Điểm tổng kết"].dropna()
c1, c2, c3, c4 = st.columns(4)
c1.metric("Số sinh viên", len(results))
c2.metric("Điểm trung bình", f"{numeric_scores.mean():.2f}" if len(numeric_scores) else "—")
c3.metric("Điểm cao nhất", f"{numeric_scores.max():.2f}" if len(numeric_scores) else "—")
c4.metric("Tỷ lệ đạt (≥ 5)", f"{(numeric_scores.ge(5).mean() * 100):.1f}%" if len(numeric_scores) else "—")

with st.expander("Xem thống kê mô tả chi tiết"):
    st.dataframe(results[score_cols + ["Điểm tổng kết"]].describe().round(2), use_container_width=True)

# ---------- Biểu đồ ----------
st.subheader("4. Trực quan hóa dữ liệu")
left, right = st.columns(2)

with left:
    st.markdown("**Phân bố xếp loại**")
    grade_counts = results["Xếp loại"].value_counts().reindex(
        ["Xuất sắc", "Giỏi", "Khá", "Trung bình", "Yếu", "Chưa đủ dữ liệu"], fill_value=0
    )
    fig1, ax1 = plt.subplots()
    grade_counts[grade_counts > 0].plot(kind="bar", ax=ax1)
    ax1.set_xlabel("Xếp loại")
    ax1.set_ylabel("Số sinh viên")
    ax1.tick_params(axis="x", rotation=30)
    fig1.tight_layout()
    st.pyplot(fig1)
    plt.close(fig1)

with right:
    st.markdown("**Điểm tổng kết theo sinh viên**")
    plot_df = results.dropna(subset=["Điểm tổng kết"])
    if not plot_df.empty:
        fig2, ax2 = plt.subplots()
        ax2.bar(plot_df["Mã sinh viên"].astype(str), plot_df["Điểm tổng kết"])
        ax2.axhline(5, linestyle="--", label="Ngưỡng đạt (5 điểm)")
        ax2.set_ylim(0, 10)
        ax2.set_xlabel("Mã sinh viên")
        ax2.set_ylabel("Điểm tổng kết")
        ax2.tick_params(axis="x", rotation=45)
        ax2.legend()
        fig2.tight_layout()
        st.pyplot(fig2)
        plt.close(fig2)
    else:
        st.info("Chưa có điểm hợp lệ để vẽ biểu đồ.")

st.subheader("5. Nhận xét tự động")
if len(numeric_scores):
    passed = int(numeric_scores.ge(5).sum())
    failed = int(numeric_scores.lt(5).sum())
    best = results.loc[results["Điểm tổng kết"].idxmax()]
    st.write(f"- Có **{passed}** sinh viên đạt từ 5 điểm trở lên và **{failed}** sinh viên dưới 5 điểm.")
    st.write(f"- Điểm trung bình của lớp là **{numeric_scores.mean():.2f}**.")
    st.write(f"- Sinh viên có điểm cao nhất: **{best['Họ tên']}** ({best['Điểm tổng kết']:.2f} điểm).")
else:
    st.info("Nhập điểm để xem nhận xét.")

st.caption("Lưu ý: Đây là ứng dụng minh họa; dữ liệu chỉ tồn tại trong phiên chạy ứng dụng.")

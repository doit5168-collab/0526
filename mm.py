import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")
st.title(" 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版")

# 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 讀取最新雲端資料（不使用快取）
df = conn.read(worksheet="Tasks", ttl=0)

# ==========================================
# 區塊一：上方新增任務輸入表單（給予全網唯一 Key）
# ==========================================
st.write("### 指派新任務")

# 修正點：加上 unique 後綴，確保絕對不重複
with st.form(key="task_input_form_unique", clear_on_submit=True):
    c_title, c_status, c_owner = st.columns()
    with c_title:
        new_title = st.text_input(" 任務名稱", placeholder="輸入任務名稱...", key="input_title")
    with c_status:
        new_status = st.selectbox(" 狀態", ["To Do", "In Progress", "Done"], key="input_status")
    with c_owner:
        new_owner = st.text_input(" 負責人", placeholder="誰來負責...", key="input_owner")
    
    submit_btn = st.form_submit_button("確認指派並同步雲端")

if submit_btn:
    if new_title and new_owner:
        new_data = {"title": new_title, "status": new_status, "owner": new_owner}
        new_row = pd.DataFrame([new_data])
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # 同步至雲端
        conn.update(worksheet="Tasks", data=updated_df)
        st.success(" 資料已成功同步寫入 Google 試算表！")
        st.rerun()
    else:
        st.error("請確認『任務名稱』與『負責人』皆已填寫！")

st.write("---")

# ==========================================
# 區塊二：下方 Trello 看板（使用 fragment 獨立保護區塊）
# ==========================================
st.write("### 看板動態狀態監控 (點擊按鈕可推進狀態)")

# 官方推薦：用 @st.fragment 把看板包起來，點按鈕時「只重新渲染看板」，絕不干擾上方表單
@st.fragment
def render_trello_board(data_df):
    trello_col1, trello_col2, trello_col3 = st.columns(3)
    needs_update = False
    
    # 【第一欄：To Do】
    with trello_col1:
        st.markdown("### <span style='color:red'> To Do (待辦)</span>", unsafe_allow_html=True)
        todo_list = data_df[data_df["status"] == "To Do"]
        if not todo_list.empty:
            for idx, row in todo_list.iterrows():
                with st.container(border=True):
                    st.write(f"**{row['title']}**")
                    st.caption(f"負責人: {row['owner']}")
                    if st.button("➔ 開始執行", key=f"to_ip_{idx}", use_container_width=True):
                        data_df.at[idx, "status"] = "In Progress"
                        needs_update = True
        else:
            st.info("暫無待辦任務")

    # 【第二欄：In Progress】
    with trello_col2:
        st.markdown("### <span style='color:orange'> In Progress (執行中)</span>", unsafe_allow_html=True)
        ip_list = data_df[data_df["status"] == "In Progress"]
        if not ip_list.empty:
            for idx, row in ip_list.iterrows():
                with st.container(border=True):
                    st.write(f"**{row['title']}**")
                    st.caption(f"負責人: {row['owner']}")
                    b_col1, b_col2 = st.columns(2)
                    with b_col1:
                        if st.button("↩ 退回待辦", key=f"to_todo_{idx}", use_container_width=True):
                            data_df.at[idx, "status"] = "To Do"
                            needs_update = True
                    with b_col2:
                        if st.button("➔ 完成任務", key=f"to_done_{idx}", use_container_width=True):
                            data_df.at[idx, "status"] = "Done"
                            needs_update = True
        else:
            st.info("暫無執行中任務")

    # 【第三欄：Done】
    with trello_col3:
        st.markdown("### <span style='color:green'> Done (已完成)</span>", unsafe_allow_html=True)
        done_list = data_df[data_df["status"] == "Done"]
        if not done_list.empty:
            for idx, row in done_list.iterrows():
                with st.container(border=True):
                    st.write(f"~~**{row['title']}**~~")
                    st.caption(f"負責人: {row['owner']}")
                    if st.button("↩ 重啟任務", key=f"back_ip_{idx}", use_container_width=True):
                        data_df.at[idx, "status"] = "In Progress"
                        needs_update = True
        else:
            st.info("暫無已完成任務")

    # 如果點擊了任何卡片按鈕，觸發更新雲端並完全刷新網頁
    if needs_update:
        conn.update(worksheet="Tasks", data=data_df)
        st.rerun()

# 執行看板渲染
render_trello_board(df)

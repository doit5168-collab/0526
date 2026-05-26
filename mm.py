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
# 區塊一：上方新增任務輸入表單
# ==========================================
st.write("### 指派新任務")

with st.form("task_input_form", clear_on_submit=True):
    c_title, c_status, c_owner = st.columns([2, 1, 1])
    with c_title:
        new_title = st.text_input(" 任務名稱", placeholder="輸入任務名稱...")
    with c_status:
        new_status = st.selectbox(" 狀態", ["To Do", "In Progress", "Done"])
    with c_owner:
        new_owner = st.text_input(" 負責人", placeholder="誰來負責...")
    
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
# 區塊二：下方 Trello 三縱欄畫布與動態連動卡片
# ==========================================
st.write("### 看板動態狀態監控 (點擊按鈕可推進狀態)")
trello_col1, trello_col2, trello_col3 = st.columns(3)

# 用來記錄是否需要更新雲端的旗標
needs_update = False

# 【第一欄：To Do】
with trello_col1:
    st.markdown("### <span style='color:red'> To Do (待辦)</span>", unsafe_allow_html=True)
    todo_list = df[df["status"] == "To Do"]
    if not todo_list.empty:
        for idx, row in todo_list.iterrows():
            with st.container(border=True):
                st.write(f"**{row['title']}**")
                st.caption(f"負責人: {row['owner']}")
                
                # 動態連動：點擊按鈕將狀態推進到「In Progress」
                # 使用 key=f"btn_{idx}" 確保每個按鈕元件的 ID 唯一
                if st.button("➔ 開始執行", key=f"to_ip_{idx}", use_container_width=True):
                    df.at[idx, "status"] = "In Progress"
                    needs_update = True
    else:
        st.info("暫無待辦任務")

# 【第二欄：In Progress】
with trello_col2:
    st.markdown("### <span style='color:orange'> In Progress (執行中)</span>", unsafe_allow_html=True)
    ip_list = df[df["status"] == "In Progress"]
    if not ip_list.empty:
        for idx, row in ip_list.iterrows():
            with st.container(border=True):
                st.write(f"**{row['title']}**")
                st.caption(f"負責人: {row['owner']}")
                
                # 放兩個按鈕：可以推進到 Done，也可以退回 To Do
                b_col1, b_col2 = st.columns(2)
                with b_col1:
                    if st.button("↩ 退回待辦", key=f"to_todo_{idx}", use_container_width=True):
                        df.at[idx, "status"] = "To Do"
                        needs_update = True
                with b_col2:
                    if st.button("➔ 完成任務", key=f"to_done_{idx}", use_container_width=True):
                        df.at[idx, "status"] = "Done"
                        needs_update = True
    else:
        st.info("暫無執行中任務")

# 【第三欄：Done】
with trello_col3:
    st.markdown("### <span style='color:green'> Done (已完成)</span>", unsafe_allow_html=True)
    done_list = df[df["status"] == "Done"]
    if not done_list.empty:
        for idx, row in done_list.iterrows():
            with st.container(border=True):
                st.write(f"~~**{row['title']}**~~")
                st.caption(f"負責人: {row['owner']}")
                
                # 動態連動：點擊按鈕重啟任務，退回執行中
                if st.button("↩ 重啟任務", key=f"back_ip_{idx}", use_container_width=True):
                    df.at[idx, "status"] = "In Progress"
                    needs_update = True
    else:
        st.info("暫無已完成任務")

# ==========================================
# 核心連動邏輯：檢查是否有卡片被點擊按鈕變更狀態
# ==========================================
if needs_update:
    # 將修改狀態後的完整 DataFrame 寫回 Google Sheets
    conn.update(worksheet="Tasks", data=df)
    st.rerun() # 重新整理網頁，卡片立刻會飛到下一欄
import streamlit as st
import pandas as pd
from streamlit_gsheets import GSheetsConnection

st.set_page_config(layout="wide")
st.title(" 階段四終極完成版：GitHub 雲端同步 Trello 看板")
st.caption("授權標註：edit by 闕河正 | 完整功能版")

# 建立 Google Sheets 連線
conn = st.connection("gsheets", type=GSheetsConnection)

# 修正 1：將 ttl="0" 改為數字 0，確保即時讀取最新雲端資料
df = conn.read(worksheet="Tasks", ttl=0)

# ==========================================
# 區塊一：上方新增任務輸入表單
# ==========================================
st.write("### 指派新任務")

with st.form("task_input_form", clear_on_submit=True):
    c_title, c_status, c_owner = st.columns([2, 1, 1]) # 運用權重比例切分表單
    with c_title:
        new_title = st.text_input(" 任務名稱", placeholder="輸入任務名稱...")
    with c_status:
        new_status = st.selectbox(" 狀態", ["To Do", "In Progress", "Done"])
    with c_owner:
        new_owner = st.text_input(" 負責人", placeholder="誰來負責...")
    
    # 表單提交按鈕
    submit_btn = st.form_submit_button("確認指派並同步雲端")

# 修正 2：核心關鍵！將判斷式與同步邏輯移到表單（with）外面
if submit_btn:
    if new_title and new_owner:
        new_data = {"title": new_title, "status": new_status, "owner": new_owner}
        new_row = pd.DataFrame([new_data])
        
        # 使用 pd.concat 進行表格拼接
        updated_df = pd.concat([df, new_row], ignore_index=True)
        
        # 寫回 Google Sheets
        conn.update(worksheet="Tasks", data=updated_df)
        
        st.success(" 資料已跨越限制，成功同步寫入 Google 試算表！")
        st.rerun() # 強制網頁自我重整，重新讀取，讓新卡片亮起來
    else:
        st.error("請確認『任務名稱』與『負責人』皆已填寫！")

st.write("---")

# ==========================================
# 區塊二：下方 Trello 三縱欄畫布與卡片渲染
# ==========================================
st.write("### 看板動態狀態監控")
trello_col1, trello_col2, trello_col3 = st.columns(3)

# 【第一欄：To Do】
with trello_col1:
    st.markdown("### <span style='color:red'> To Do (待辦)</span>", unsafe_allow_html=True)
    todo_list = df[df["status"] == "To Do"]
    if not todo_list.empty:
        for idx, row in todo_list.iterrows():
            with st.container(border=True):
                st.write(f"** {row['title']}**")
                st.caption(f"負責人: {row['owner']}")
    else:
        st.info("暫無待辦任務")

# 【第二欄：In Progress】
with trello_col2:
    st.markdown("### <span style='color:orange'> In Progress (執行中)</span>", unsafe_allow_html=True)
    ip_list = df[df["status"] == "In Progress"]
    if not ip_list.empty:
        for idx, row in ip_list.iterrows():
            with st.container(border=True):
                st.write(f"** {row['title']}**")
                st.caption(f"負責人: {row['owner']}")
    else:
        st.info("暫無執行中任務")

# 【第三欄：Done】
with trello_col3:
    st.markdown("### <span style='color:green'> Done (已完成)</span>", unsafe_allow_html=True)
    done_list = df[df["status"] == "Done"]
    if not done_list.empty:
        for idx, row in done_list.iterrows():
            with st.container(border=True):
                # 小視覺優化：已完成任務加上刪除線
                st.write(f"~~** {row['title']}**~~")
                st.caption(f"負責人: {row['owner']}")
    else:
        st.info("暫無已完成任務")

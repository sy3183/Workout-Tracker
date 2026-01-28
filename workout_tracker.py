import sqlite3
from datetime import date, timedelta
import pandas as pd
import streamlit as st
import matplotlib.pyplot as plt

DB_PATH = "workouts.db"


# -------------------------
# Database helpers
# -------------------------
def get_conn():
    return sqlite3.connect(DB_PATH, check_same_thread=False)


def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS workout_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            workout_date TEXT NOT NULL,
            exercise TEXT NOT NULL,
            sets INTEGER NOT NULL,
            reps INTEGER NOT NULL,
            weight REAL NOT NULL,
            volume REAL NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def insert_log(workout_date: str, exercise: str, sets: int, reps: int, weight: float):
    volume = sets * reps * weight
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        INSERT INTO workout_logs (workout_date, exercise, sets, reps, weight, volume)
        VALUES (?, ?, ?, ?, ?, ?)
    """, (workout_date, exercise.strip(), sets, reps, weight, volume))
    conn.commit()
    conn.close()


def delete_log(log_id: int):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("DELETE FROM workout_logs WHERE id = ?", (log_id,))
    conn.commit()
    conn.close()


def load_logs() -> pd.DataFrame:
    conn = get_conn()
    df = pd.read_sql_query("SELECT * FROM workout_logs ORDER BY workout_date ASC, id ASC", conn)
    conn.close()
    if not df.empty:
        df["workout_date"] = pd.to_datetime(df["workout_date"]).dt.date
    return df


# -------------------------
# Plot helpers
# -------------------------
def plot_daily_volume(df: pd.DataFrame):
    daily = df.groupby("workout_date", as_index=False)["volume"].sum().sort_values("workout_date")

    fig = plt.figure()
    plt.plot(daily["workout_date"], daily["volume"], marker="o")
    plt.title("Total Volume Over Time (Daily)")
    plt.xlabel("Date")
    plt.ylabel("Total Volume (sets × reps × weight)")
    plt.xticks(rotation=45)
    plt.tight_layout()
    st.pyplot(fig)


def plot_volume_by_exercise(df: pd.DataFrame):
    ex = df.groupby("exercise", as_index=False)["volume"].sum().sort_values("volume", ascending=False)

    fig = plt.figure()
    plt.bar(ex["exercise"], ex["volume"])
    plt.title("Total Volume by Exercise (All Time)")
    plt.xlabel("Exercise")
    plt.ylabel("Total Volume")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    st.pyplot(fig)


# -------------------------
# UI Styling (aesthetics only)
# -------------------------
def inject_css():
    st.markdown(
        """
<style>
/* --- Global layout --- */
.stApp {
  background: radial-gradient(1200px 600px at 10% 0%, rgba(255,255,255,0.08), transparent 60%),
              linear-gradient(180deg, rgba(255,255,255,0.04), transparent 30%),
              #0B0F14;
  color: #E8EEF7;
}

/* --- Sidebar theme: ensure readability --- */
[data-testid="stSidebar"] {
  background: #0E141B !important;
  border-right: 1px solid rgba(255,255,255,0.10) !important;
}

[data-testid="stSidebar"] * {
  color: rgba(232, 238, 247, 0.92) !important;
}

[data-testid="stSidebar"] label,
[data-testid="stSidebar"] p,
[data-testid="stSidebar"] span,
[data-testid="stSidebar"] .stCaption,
[data-testid="stSidebar"] .stMarkdown {
  color: rgba(232, 238, 247, 0.90) !important;
}

/* Inputs in sidebar */
[data-testid="stSidebar"] input,
[data-testid="stSidebar"] textarea {
  background: rgba(255,255,255,0.06) !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  color: rgba(232, 238, 247, 0.95) !important;
}

/* Fix radio text specifically (lbs/kg) */
[data-testid="stSidebar"] [role="radiogroup"] * {
  color: rgba(232, 238, 247, 0.92) !important;
}

/* Make the 'Add Log' button readable */
[data-testid="stSidebar"] .stButton>button {
  background: rgba(255,255,255,0.10) !important;
  border: 1px solid rgba(255,255,255,0.18) !important;
}
[data-testid="stSidebar"] .stButton>button:hover {
  background: rgba(255,255,255,0.14) !important;
}

/* --- container width/padding --- */
.block-container {
  padding-top: 1.2rem;
  padding-bottom: 2.5rem;
  max-width: 1200px;
}

/* --- Typography --- */
h1, h2, h3 {
  letter-spacing: -0.02em;
}
p, label, .stMarkdown, .stText, .stCaption {
  color: rgba(232, 238, 247, 0.92);
}

/* --- Hide Streamlit default menu/footer (KEEP header so sidebar toggle works) --- */
#MainMenu {visibility: hidden;}
footer {visibility: hidden;}

/* --- Card container --- */
.card {
  background: rgba(255, 255, 255, 0.06);
  border: 1px solid rgba(255, 255, 255, 0.10);
  border-radius: 18px;
  padding: 18px 18px 12px 18px;
  box-shadow: 0 10px 30px rgba(0,0,0,0.25);
}

/* --- Hero --- */
.hero {
  border-radius: 22px;
  padding: 20px 22px;
  border: 1px solid rgba(255, 255, 255, 0.10);
  background: linear-gradient(120deg,
      rgba(90, 255, 197, 0.15),
      rgba(82, 165, 255, 0.12),
      rgba(255, 89, 199, 0.08)
  );
  box-shadow: 0 14px 35px rgba(0,0,0,0.35);
}
.hero-title {
  font-size: 34px;
  font-weight: 780;
  margin: 0;
  line-height: 1.1;
}
.hero-sub {
  margin-top: 8px;
  font-size: 15px;
  color: rgba(232, 238, 247, 0.82);
}

/* --- Metric tiles --- */
.metric-tile {
  border-radius: 16px;
  padding: 14px 14px;
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
}
.metric-label {
  font-size: 12px;
  color: rgba(232, 238, 247, 0.68);
  margin-bottom: 6px;
}
.metric-value {
  font-size: 22px;
  font-weight: 780;
}

/* --- Buttons --- */
.stButton>button, .stDownloadButton>button {
  border-radius: 14px !important;
  padding: 0.65rem 0.9rem !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.06) !important;
  color: #E8EEF7 !important;
  transition: transform 0.06s ease-in-out, background 0.15s ease-in-out;
}
.stButton>button:hover {
  transform: translateY(-1px);
  background: rgba(255,255,255,0.10) !important;
}

/* --- Inputs --- */
.stTextInput input, .stNumberInput input, .stTextArea textarea, .stDateInput input {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.05) !important;
  color: #E8EEF7 !important;
}
.stMultiSelect [data-baseweb="select"] > div {
  border-radius: 14px !important;
  border: 1px solid rgba(255,255,255,0.14) !important;
  background: rgba(255,255,255,0.05) !important;
}

/* --- Tabs styling (subtle) --- */
.stTabs [data-baseweb="tab-list"] {
  gap: 6px;
}
.stTabs [data-baseweb="tab"] {
  background: rgba(255,255,255,0.05);
  border: 1px solid rgba(255,255,255,0.10);
  border-radius: 14px;
  padding: 8px 14px;
}
.stTabs [aria-selected="true"] {
  background: rgba(255,255,255,0.10);
}

/* --- Dataframe --- */
[data-testid="stDataFrame"] {
  border-radius: 18px;
  overflow: hidden;
  border: 1px solid rgba(255,255,255,0.10);
}

/* --- Divider --- */
hr {
  border: none;
  border-top: 1px solid rgba(255,255,255,0.10);
  margin: 1.2rem 0;
}
</style>
        """,
        unsafe_allow_html=True
    )


def hero():
    st.markdown(
        """
<div class="hero">
  <div class="hero-title">🏋️ LiftLog</div>
  <div class="hero-sub">
    Log sets in seconds • Track total volume • Spot trends over time
  </div>
</div>
        """,
        unsafe_allow_html=True
    )


def metric_tile(label: str, value: str):
    st.markdown(
        f"""
<div class="metric-tile">
  <div class="metric-label">{label}</div>
  <div class="metric-value">{value}</div>
</div>
        """,
        unsafe_allow_html=True
    )


# -------------------------
# App
# -------------------------
def main():
    st.set_page_config(
        page_title="LiftLog • Workout Tracker",
        page_icon="🏋️",
        layout="wide",
        initial_sidebar_state="expanded",  # ensures sidebar appears
    )

    inject_css()
    init_db()

    # Header / Hero
    hero()
    st.write("")

    # Sidebar: Add log (UX upgraded)
    st.sidebar.markdown("## Add a Set")
    st.sidebar.caption("Quickly log a set. We’ll compute volume automatically.")

    units = st.sidebar.radio("Units", options=["lbs", "kg"], horizontal=True, index=0)
    workout_date = st.sidebar.date_input("Date", value=date.today())
    exercise = st.sidebar.text_input("Exercise", placeholder="e.g., Bench Press")
    c1, c2 = st.sidebar.columns(2)
    sets = c1.number_input("Sets", min_value=1, max_value=50, value=3, step=1)
    reps = c2.number_input("Reps", min_value=1, max_value=200, value=8, step=1)
    weight = st.sidebar.number_input(f"Weight ({units})", min_value=0.0, max_value=2000.0, value=135.0, step=2.5)

    add_btn = st.sidebar.button("➕ Add Log", use_container_width=True)

    if add_btn:
        if not exercise.strip():
            st.sidebar.error("Please enter an exercise name.")
        else:
            insert_log(str(workout_date), exercise, int(sets), int(reps), float(weight))
            st.sidebar.success("Added!")
            st.rerun()

    st.sidebar.divider()
    st.sidebar.caption("Tip: You can filter logs by exercise + date on the Logs tab.")

    # Load data
    df = load_logs()
    if df.empty:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("No workouts yet")
        st.write("Add your first entry from the sidebar to unlock analytics.")
        st.markdown('</div>', unsafe_allow_html=True)
        return

    # Derived quick stats (no functionality change)
    today = date.today()
    last_7 = today - timedelta(days=6)

    total_volume = float(df["volume"].sum())
    total_sessions = int(df["workout_date"].nunique())
    total_entries = int(len(df))
    last_day = df["workout_date"].max()

    today_volume = float(df[df["workout_date"] == today]["volume"].sum())
    last7_volume = float(df[df["workout_date"] >= last_7]["volume"].sum())

    # Tabs “navigation”
    tab_dashboard, tab_logs, tab_trends = st.tabs(["Dashboard", "Logs", "Trends"])

    with tab_dashboard:
        m1, m2, m3, m4 = st.columns(4)
        with m1:
            metric_tile("Total Volume (All Time)", f"{total_volume:,.0f}")
        with m2:
            metric_tile("Training Days Logged", f"{total_sessions}")
        with m3:
            metric_tile("Volume (Last 7 Days)", f"{last7_volume:,.0f}")
        with m4:
            metric_tile("Volume (Today)", f"{today_volume:,.0f}")

        st.write("")

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Quick insights")
        top_ex = (
            df.groupby("exercise", as_index=False)["volume"]
            .sum()
            .sort_values("volume", ascending=False)
            .head(5)
        )
        if len(top_ex) > 0:
            st.write("**Top exercises by total volume:**")
            for _, row in top_ex.iterrows():
                st.write(f"• {row['exercise']}: {row['volume']:,.0f}")
        st.caption("Volume = sets × reps × weight. This is a simple but useful proxy for overall workload.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_logs:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Logs")

        fcol1, fcol2 = st.columns(2)
        exercise_filter = fcol1.multiselect(
            "Filter by exercise",
            options=sorted(df["exercise"].unique().tolist()),
            default=[]
        )
        date_min = fcol2.date_input("Show logs from date", value=min(df["workout_date"]))

        filtered = df.copy()
        filtered = filtered[filtered["workout_date"] >= date_min]
        if exercise_filter:
            filtered = filtered[filtered["exercise"].isin(exercise_filter)]

        show_cols = ["id", "workout_date", "exercise", "sets", "reps", "weight", "volume"]
        st.dataframe(filtered[show_cols], use_container_width=True)

        st.markdown("#### Delete a log entry")
        del_c1, del_c2 = st.columns([2, 1])
        del_id = del_c1.number_input("Log id", min_value=0, step=1, value=0, label_visibility="collapsed")
        del_clicked = del_c2.button("🗑️ Delete", type="secondary", use_container_width=True)

        if del_clicked:
            if del_id == 0:
                st.warning("Enter a valid log id (non-zero).")
            else:
                delete_log(int(del_id))
                st.success(f"Deleted log id {int(del_id)}")
                st.rerun()

        st.caption("Tip: Keep logging consistently—trends become meaningful after ~1–2 weeks of data.")
        st.markdown('</div>', unsafe_allow_html=True)

    with tab_trends:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("Trends")

        # Reuse the same filtering logic as logs tab, but keep it simple:
        tcol1, tcol2 = st.columns(2)
        with tcol1:
            plot_daily_volume(df)
        with tcol2:
            plot_volume_by_exercise(df)

        st.caption("These charts use total volume to visualize workload trends over time.")
        st.markdown('</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()

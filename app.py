import streamlit as st
import pandas as pd
import io

# ==========================
# 🌍 Load Dataset (Robust)
# ==========================
try:
    # Let pandas sniff the separator (engine='python', sep=None)
    df = pd.read_csv("universities.csv", encoding="latin1", sep=None, engine="python")
except Exception:
    # Fallback: try a plain read (common case)
    try:
        df = pd.read_csv("universities.csv", encoding="latin1")
    except Exception as e:
        st.error(f"⚠️ Error loading CSV: {e}")
        st.stop()

# If pandas parsed the file into a single column (common when the whole line is quoted),
# try a few safer fallbacks before giving up.
if len(df.columns) != 5:
    try:
        # Read raw lines and attempt to split on commas (handle lines wrapped in quotes)
        with open("universities.csv", "r", encoding="latin1") as f:
            raw_lines = [x.rstrip('\n\r') for x in f.readlines() if x.strip()]

        if not raw_lines:
            raise ValueError("CSV is empty")

        # Remove surrounding quotes if the whole line is quoted
        lines = []
        for ln in raw_lines:
            ln = ln.strip()
            if (ln.startswith('"') and ln.endswith('"')) or (ln.startswith("'") and ln.endswith("'")):
                ln = ln[1:-1]
            lines.append(ln)

        header_parts = lines[0].split(",")
        if len(header_parts) >= 5:
            data = [line.split(",") for line in lines]
            df = pd.DataFrame(data[1:], columns=data[0])
        else:
            # Last resort: split the single parsed column into multiple columns
            parts = df.iloc[:, 0].str.split(",", expand=True)
            if parts.shape[1] >= 5:
                # strip surrounding quotes from each cell if present
                parts = parts.applymap(lambda v: v.strip().strip('"').strip("'") if isinstance(v, str) else v)
                df = parts.iloc[:, :5]
            else:
                raise ValueError("Could not parse CSV into 5+ columns")
    except Exception as e:
        st.error(f"⚠️ Error parsing CSV: {e}")
        st.stop()

# Ensure we have at least five columns, then normalize column names
if len(df.columns) >= 5:
    df = df.iloc[:, :5]
    df.columns = ["name", "country", "city", "website", "fields"]
else:
    st.error(f"⚠️ CSV parsing failed: expected at least 5 columns but found {len(df.columns)}")
    st.stop()

# ==========================
# 🎨 Page Config
# ==========================
st.set_page_config(page_title="Education Finder", layout="wide")

# Custom CSS — Cyberpunk theme
st.markdown("""
    <style>
    :root {
        --bg-1: #0b0720;
        --bg-2: #1b0536;
        --neon-pink: #ff2d95;
        --neon-cyan: #00e5ff;
        --neon-purple: #7b1fa2;
        --card-bg: rgba(10, 10, 12, 0.65);
        --glass-border: rgba(255,255,255,0.04);
    }

    /* Page background */
    body {
        background: radial-gradient(ellipse at 10% 10%, rgba(0,229,255,0.06) 0%, transparent 10%),
                    linear-gradient(135deg, var(--bg-1) 0%, var(--bg-2) 60%, #120018 100%);
        color: #e6e6f0;
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        min-height: 100vh;
        padding-top: 10px;
    }

    /* Neon title */
    .title {
        text-align: center;
        font-size: 48px;
        font-weight: 800;
        margin-bottom: 6px;
        background: linear-gradient(90deg, var(--neon-cyan), var(--neon-pink), var(--neon-purple));
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-shadow:
            0 0 6px rgba(0,229,255,0.12),
            0 0 12px rgba(255,45,149,0.06),
            0 6px 20px rgba(0,0,0,0.6);
    }

    .subtitle {
        text-align: center;
        color: rgba(230,230,240,0.6);
        font-size: 16px;
        margin-bottom: 28px;
    }

    /* Cards with neon accent */
    .card {
        background: var(--card-bg);
        border: 1px solid var(--glass-border);
        border-left: 6px solid rgba(0,229,255,0.12);
        border-radius: 14px;
        padding: 22px;
        box-shadow: 0 10px 30px rgba(3,6,23,0.6), 0 0 18px rgba(123,31,162,0.06) inset;
        margin-bottom: 22px;
        transition: transform 0.18s ease, box-shadow 0.18s ease;
    }

    .card:hover {
        transform: translateY(-6px);
        box-shadow: 0 18px 40px rgba(3,6,23,0.7), 0 0 30px rgba(255,45,149,0.08);
        border-left-color: var(--neon-pink);
    }

    /* Headings and small accents */
    .card h3 { color: #f8f8ff; margin-bottom: 6px; }
    .card p { color: rgba(230,230,240,0.85); margin: 6px 0; }

    a {
        color: var(--neon-cyan);
        text-decoration: none;
        font-weight: 600;
    }
    a:hover { text-decoration: underline; color: var(--neon-pink); }

    /* Inputs / select styling hint: keep contrast on dark bg */
    .stTextInput>div>div>input, .stSelectbox>div>div>select {
        background: rgba(255,255,255,0.03) !important;
        color: #e8e8f2 !important;
        border: 1px solid rgba(255,255,255,0.04) !important;
    }

    /* Footer tweak */
    footer { color: rgba(200,200,220,0.5); }
    </style>
""", unsafe_allow_html=True)

# ==========================
# 🧭 Header
# ==========================
st.markdown("<div class='title'>🎓 Education Finder</div>", unsafe_allow_html=True)
st.markdown("<div class='subtitle'>Discover top universities worldwide based on your interests 🌍</div>", unsafe_allow_html=True)

# ==========================
# 🔍 Filters
# ==========================
countries = ["All"] + sorted(df["country"].dropna().unique().tolist())
fields = ["All"] + sorted(set("|".join(df["fields"].dropna()).split("|")))

col1, col2 = st.columns(2)
with col1:
    selected_country = st.selectbox("🌎 Choose Country", countries)
with col2:
    selected_field = st.selectbox("📘 Choose Field", fields)

search = st.text_input("🔎 Search by University Name or City")

# ==========================
# 🧠 Filter Logic
# ==========================
filtered_df = df.copy()

if selected_country != "All":
    filtered_df = filtered_df[filtered_df["country"].str.lower() == selected_country.lower()]

if selected_field != "All":
    filtered_df = filtered_df[filtered_df["fields"].str.contains(selected_field, case=False, na=False)]

if search:
    filtered_df = filtered_df[
        filtered_df["name"].str.contains(search, case=False, na=False)
        | filtered_df["city"].str.contains(search, case=False, na=False)
    ]

# ==========================
# 🏫 Display Results
# ==========================
st.markdown("### 📚 Available Universities")

if not filtered_df.empty:
    for _, row in filtered_df.iterrows():
        st.markdown(f"""
        <div class='card'>
            <h3>{row['name']}</h3>
            <p><b>📍 Location:</b> {row['city']}, {row['country']}</p>
            <p><b>📘 Fields:</b> {row['fields']}</p>
            <p><a href='{row['website']}' target='_blank'>🌐 Visit Website</a></p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.warning("No results found. Try adjusting your filters or search term.")

# ==========================
# 🧾 Footer
# ==========================
st.markdown("<br><hr><center>Made with ❤️ using Streamlit</center>", unsafe_allow_html=True)

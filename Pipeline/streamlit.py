import pandas as pd
import psycopg2
from psycopg2.extras import execute_values
from dotenv import load_dotenv
import os
import streamlit as st
import matplotlib.pyplot as plt
import folium
from streamlit_folium import st_folium

# -------------------------
# -- FUNCTIONS -- 
# -------------------------
def build_segments(df, class_names):
    """
    Creates a segmented version of a dataframe suitable for a Gantt Chart.

    df(param): The dataframe, which should have timestamps and the classes.
    class_names(param): The class names which should match the df parameter in column length.
    """
    segments = []

    for cls in class_names:
        active = False
        start = None

        for i in range(len(df)):
            val = df.iloc[i][cls]

            if val == 1 and not active:
                active = True
                start = i

            elif val == 0 and active:
                segments.append({
                    "class": cls,
                    "start": start,
                    "end": i
                })
                active = False

        if active:
            segments.append({
                "class": cls,
                "start": start,
                "end": len(df)
            })

    return segments


def gantt_show(segments):
    """
    Creates the Gantt plot illustration using matplotlib.pyplot. 
    segments(param): The segmented dataframe created from the build_segments() function.
    """
    fig, ax = plt.subplots(figsize=(10, 4), dpi=100)

    # Map each class to a y position
    class_to_y = {cls: i for i, cls in enumerate(CLASS_NAMES)}

    for seg in segments:
        ax.barh(
            y=class_to_y[seg["class"]],
            width=seg["end"] - seg["start"],
            left=seg["start"]
        )

    # Sets the labels, ticks, and titles. 
    ax.set_yticks(list(class_to_y.values()))
    ax.set_yticklabels(CLASS_NAMES)
    ax.set_xlabel("Frame")
    ax.set_ylabel("Class")
    ax.set_title("Detection Timeline")

    # Show frame
    #plt.tight_layout()
    #plt.show()
    fig.tight_layout()
    return fig

# -------------------------
# -- BUTTONS AT TOP (style, logic etc.) -- 
# -------------------------
st.markdown("""
<style>
/* push page content down so fixed nav doesn't cover it */
.main .block-container {
    padding-top: 5.5rem;
}

/* fixed top nav */
.jump-bar {
    position: fixed;
    top: 4rem;
    left: 50%;
    transform: translateX(-50%);
    z-index: 99999;
    display: flex;
    gap: 10px;
    padding: 10px 12px;
    background: rgba(14, 17, 23, 0.95);
    border: 1px solid #333;
    border-radius: 12px;
    backdrop-filter: blur(6px);
}

/* dark button style */
.jump-btn {
    display: inline-block;
    padding: 8px 14px;
    background: #262730;
    color: white !important;
    text-decoration: none !important;
    border-radius: 8px;
    border: 1px solid #444;
    font-size: 14px;
    line-height: 1.2;
}

.jump-btn:hover {
    background: #333;
    border-color: #888;
    color: white !important;
    text-decoration: none !important;
}

/* offset anchor so section title isn't hidden behind nav */
.anchor {
    display: block;
    position: relative;
    top: 150px;
    visibility: hidden;
}

</style>

<div class="jump-bar">
    <a class="jump-btn" href="#home">🏠︎</a>
    <a class="jump-btn" href="#log-dash">RESET CSV</a>
    <a class="jump-btn" href="#csv">Preview CSV</a>
    <a class="jump-btn" href="#gantt-chart">Gantt Chart</a>
    <a class="jump-btn" href="#map">Map</a>
</div>
""", unsafe_allow_html=True)

# -------------------------
# -- CONNECT TO DB + FETCH DATA -- 
# -------------------------
load_dotenv()

try:
    conn = psycopg2.connect(
        host=os.getenv("DB_HOST"),
        port=os.getenv("DB_PORT"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASSWORD")
    )

    with conn.cursor() as cursor:
        cursor.execute("SELECT * FROM object_logs;")

        rows = cursor.fetchall()
        cols = [desc[0] for desc in cursor.description]

        df = pd.DataFrame(rows, columns=cols)
finally:
    conn.close()

CLASS_NAMES = ["bear", "cyclist", "fox", "reindeer", "robot", "santa"]
st.set_page_config(page_title="Rover Project", layout="wide")

# -------------------------
# -- IMAGES / HOME --
# -------------------------
st.markdown('<div id="home"></div>', unsafe_allow_html=True)
st.write("")
st.write("")
col1, col2, col3 = st.columns(3)
with col1:
    st.image(r"C:\Users\edijs\Robotics and AI Project-Team 3-3\rover.jpeg", caption="View 1", use_container_width=True)
with col2:
    st.image(r"C:\Users\edijs\Robotics and AI Project-Team 3-3\rover.jpeg", caption="View 2", use_container_width=True)
with col3:
    st.image(r"C:\Users\edijs\Robotics and AI Project-Team 3-3\rover.jpeg", caption="View 3", use_container_width=True)


# -------------------------
# -- LOG DASH TITLE (change to smt better) --
# -------------------------
st.markdown('<div id="log-dash"></div>', unsafe_allow_html=True)
st.write("")
st.write("")
st.title("Object Log Dashboard")

# -------------------------
# -- SHOW CSV --
# -------------------------
st.markdown('<div id="csv"></div>', unsafe_allow_html=True)
st.write("")
st.write("")
st.title("Preview CSV")
st.dataframe(df)

# -------------------------
# -- GANTT CHART --
# -------------------------
segments = build_segments(df, CLASS_NAMES)
fig = gantt_show(segments)

st.markdown('<div id="gantt-chart"></div>', unsafe_allow_html=True)
st.write("")
st.write("")
st.title("Gantt Chart")
st.pyplot(fig)

# -------------------------
# -- MAP + COORDINATES + DRAW ROUTE -- 
# -------------------------
st.markdown('<div id="map"></div>', unsafe_allow_html=True)
st.write("")
st.write("")
st.title("Rovaniemi Route Map")
st.write("Rovers journey.")

# Sample coordinates in the Rovaniemi area
route_data = [
    {"name": "Rovaniemi City Center", "lat": 66.5039, "lon": 25.7294},
    {"name": "Arktikum", "lat": 66.5090, "lon": 25.7383},
    {"name": "Ounasvaara", "lat": 66.5196, "lon": 25.7817},
    {"name": "Santa Claus Village", "lat": 66.5436, "lon": 25.8473},
    {"name": "Rovaniemi Airport Area", "lat": 66.5648, "lon": 25.8304},
]
#@st.cache_data(ttl=10)
#def load_cloud_route_data() -> pd.DataFrame:
#    """
#    Replace this later with your cloud source.

#    Examples:
#    - pd.read_csv("https://your-url/coordinates.csv")
#    - pd.read_json("https://your-url/route")
#    - database query result to dataframe
#    """
#    return load_local_route_data()

df = pd.DataFrame(route_data)

# Center map roughly around the average coordinate
center_lat = df["lat"].mean()
center_lon = df["lon"].mean()

m = folium.Map(location=[center_lat, center_lon], zoom_start=12, control_scale=True)

# Draw route line
route_points = df[["lat", "lon"]].values.tolist()
left_col, right_col = st.columns([2, 1])

folium.PolyLine(
    locations=route_points,
    weight=5,
    opacity=0.8,
    tooltip="Route",
).add_to(m)

# Optional: mark start and end differently
folium.CircleMarker(
    location=route_points[0],
    radius=8,
    popup="Start",
    tooltip="Start",
    color="green",
    fill=True,
    fill_opacity=0.9,
).add_to(m)

folium.CircleMarker(
    location=route_points[-1],
    radius=8,
    popup="End",
    tooltip="End",
    color="red",
    fill=True,
    fill_opacity=0.9,
).add_to(m)

# Placement for map
with left_col:
    st.subheader("Map")
    st_folium(m, width=900, height=550)

# Placement for coordinate data
with right_col:
    st.subheader("Route Points")
    st.dataframe(df, use_container_width=True)

    st.subheader("Raw Route Coordinates")
    st.code(route_points, language="python")






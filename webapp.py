import streamlit as sl, numpy as np, pandas as pd
import pydeck as pdk
import plotly.express as px

DATA_URL = {
    "data\\Motor_Vehicle_Collisions.csv"
}

sl.title("Vehicles Collisions In NYC")

sl.markdown("This application is dashboard built with Streamlit that can be used to analyze vehicles collisions in NYC 👮💥🚗")
sl.markdown("###### 🔴NOTE : Options/Filtering are available on left-sidebar.")

@sl.cache(persist = True) # it will re-run computation only if code/variable has been changed & it doesn't do computation every-time when we re-run our streamlit app
def load_data(nrows):
    # data = pd.read_csv("data\\Motor_Vehicle_Collisions.csv", nrows = nrows, parse_dates = [["CRASH_DATE", "CRASH_TIME"]]) # for local machine
    data = pd.read_csv("https://drive.google.com/file/d/1mKt8rvPK7bErO4YYnnOSFdafRg8JDcGk/view?usp=sharing", nrows = nrows, parse_dates = [["CRASH_DATE", "CRASH_TIME"]])
    data.dropna(subset = ["LATITUDE", "LONGITUDE"], inplace = True)
    lowercase = lambda x : str(x).lower()
    data.rename(lowercase, axis = "columns", inplace = True)
    data.rename(columns = {"crash_date_crash_time": "date/time"}, inplace = True)
    return data

data = load_data(100000)
original_data = data

sl.header("Where are the most people injured in NYC ?")
sl.sidebar.header("Options ⚙️")
injured_people = sl.sidebar.slider("Number of persons injured in vehicle collision", 0, 19)
# displaying mapbox
sl.map(data.query("injured_persons >= @injured_people")[["latitude", "longitude"]].dropna(how = "any")) # @variable

sl.header("How many collisions occur during a given time of day ?")
hour = sl.sidebar.slider("Hour to look at", 0, 23)
data = data[data["date/time"].dt.hour == hour]

sl.markdown("Vehicle collisions between %i:00 and %i:00" % (hour, (hour + 1) % 24))

midpoint = (np.average(data["latitude"]), np.average(data["longitude"]))
sl.write(
    pdk.Deck(
        map_style = "mapbox://styles/mapbox/light-v9",
        initial_view_state = {
            "latitude": midpoint[0],
            "longitude": midpoint[1],
            "zoom": 11,
            "pitch": 50
        },
        layers = [
            pdk.Layer(
                "HexagonLayer",
                data = data[["date/time", "latitude", "longitude"]],
                get_position = ["longitude", "latitude"],
                radius = 100,
                extruded = True,
                pickable = True,
                elevation_scale = 4,
                elevation_range = [0, 1000],
            ),
        ],
    )
)

sl.subheader("Breakdown by minute between %i:00 and %i:00" % (hour, (hour + 1) % 24))
filtered = data[
    (data["date/time"].dt.hour >= hour) & (data["date/time"].dt.hour < (hour + 1))
]
hist = np.histogram(filtered["date/time"].dt.minute, bins = 60, range = (0, 60))[0]
chart_data = pd.DataFrame({"minute": range(60), "crashes": hist})
fig = px.bar(chart_data, x = "minute", y = "crashes", hover_data = ["minute", "crashes"])
sl.write(fig)

dangerous_option = sl.sidebar.selectbox("Select top dangerous streets by affected type", [5, 10, 15])
sl.header("Top %i dangerous streets by affected type" % (dangerous_option))
select = sl.selectbox("Affected type", ["Pedestrians", "Cyclists", "Motorists"])

if select == "Pedestrians":
    sl.write(original_data.query("injured_pedestrians >= 1")[["on_street_name", "injured_pedestrians"]].sort_values(by = ["injured_pedestrians"], ascending = False).dropna(how = "any")[ : dangerous_option])
elif select == "Cyclists":
    sl.write(original_data.query("injured_cyclists >= 1")[["on_street_name", "injured_cyclists"]].sort_values(by = ["injured_cyclists"], ascending = False).dropna(how = "any")[ : dangerous_option])
elif select == "Motorists":
    sl.write(original_data.query("injured_motorists >= 1")[["on_street_name", "injured_motorists"]].sort_values(by = ["injured_motorists"], ascending = False).dropna(how = "any")[ : dangerous_option])

if sl.checkbox("Show Raw Data", False):
    sl.subheader("Raw Data")
    sl.write(data)

sl.sidebar.subheader("👨🏻‍💻 - Saurav Panchal")
sl.sidebar.markdown("⚒️ - [Edit Project Here](https://github.com/sauravpanchal/vehicle-collision-webapplication)")
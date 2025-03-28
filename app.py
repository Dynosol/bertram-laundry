import streamlit as st
import requests
import time
from datetime import datetime

# Harvard theme colors
HARVARD_CRIMSON = "#A51C30"
HARVARD_LIGHT_BEIGE = "#E2D6B5"

# Constants for the LaundryView API
API_URL = "https://www.laundryview.com/api/currentRoomData"
PARAMS = {
    "school_desc_key": "405",
    "location": "1362511",
    "userContact": "9789088494",
}

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "referer": "https://www.laundryview.com/home/405/1362511/QUAD/CABOT-HOUSE-BERTRAM-HALL",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/134.0.0.0 Safari/537.36"
}

def get_machine_status():
    try:
        response = requests.get(API_URL, params=PARAMS, headers=HEADERS)
        return response.json()
    except Exception as e:
        st.error(f"Error fetching data: {str(e)}")
        return None

def display_machine(machine, machine_type):
    # Determine machine state and colors
    if machine["status_toggle"] == 0:
        status = "Available"
        color = "#28a745"  # Green for available
        bg_color = color
        text_color = "white"
    elif machine["status_toggle"] == 2 and machine["time_remaining"] > 0:
        minutes_remaining = int(machine["time_remaining"])
        progress = machine["percentage"]
        # Show both time and percentage
        status = f"{minutes_remaining} min ({int(progress * 100)}% Finished)"
        color = "#007bff"  # Blue for in progress
        # Show elapsed time in grey (left) and remaining time in blue (right)
        elapsed_percent = progress * 100
        bg_color = f"linear-gradient(to right, #e9ecef {elapsed_percent}%, {color} {elapsed_percent}%)"
        text_color = "black"  # Black text for in-progress machines
    else:
        status = "Finished"
        color = "#343a40"  # Even darker grey for finished
        bg_color = color
        text_color = "white"

    # Create a card-like container for each machine
    with st.container():
        st.markdown(
            f"""
            <div style="
                padding: 1rem;
                border-radius: 10px;
                margin-bottom: 0.5rem;
                background: {bg_color};
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                height: 100px;
            ">
                <h4 style="
                    color: {text_color};
                    margin-bottom: 0.25rem;
                    font-size: 0.9rem;
                ">{machine_type} {machine['appliance_desc']}</h4>
                <div style="
                    font-size: 1.2rem;
                    font-weight: bold;
                    color: {text_color};
                ">{status}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

def is_appliance(machine):
    """Check if the object is a washer or dryer."""
    return (
        isinstance(machine, dict) and
        "type" in machine and
        machine["type"] not in ["D", "cardReader"]  # Filter out walls and card readers
    )

def main():
    st.set_page_config(
        page_title="Bertram Hall Laundry Monitor",
        page_icon="🧺",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Apply light mode styling and remove padding
    st.markdown("""
        <style>
        .stApp {
            background-color: #F8F9FA;
        }
        .main > div {
            padding-top: 1rem;
            padding-bottom: 1rem;
        }
        section[data-testid="stSidebar"] {
            display: none;
        }
        </style>
    """, unsafe_allow_html=True)

    # Title with Harvard theme
    st.markdown(
        f"""
        <div style="
            text-align: center;
            background-color: white;
            padding: 1.5rem;
            border-radius: 10px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            margin-bottom: 1.5rem;
        ">
            <h1 style="
                color: {HARVARD_CRIMSON};
                margin-bottom: 0.5rem;
                font-size: 2.5rem;
            ">Bertram Hall Laundry</h1>
            <p style="
                color: {HARVARD_CRIMSON};
                opacity: 0.8;
                font-size: 1rem;
                margin: 0;
            ">Real-time Machine Status</p>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Create two columns for washers and dryers with less spacing
    col1, col2 = st.columns([1, 1])

    while True:
        data = get_machine_status()
        
        if data and "objects" in data:
            machines = [m for m in data["objects"] if is_appliance(m)]
            washers = [m for m in machines if m["type"].startswith("wash")]
            dryers = [m for m in machines if m["type"].startswith("dry")]

            # Display washers
            with col1:
                st.markdown(f"""
                    <h2 style='
                        color: {HARVARD_CRIMSON};
                        font-size: 1.5rem;
                        margin-bottom: 0.75rem;
                        font-weight: bold;
                        padding-left: 0.5rem;
                    '>Washers</h2>
                """, unsafe_allow_html=True)
                
                for washer in washers:
                    display_machine(washer, "Washer")

            # Display dryers
            with col2:
                st.markdown(f"""
                    <h2 style='
                        color: {HARVARD_CRIMSON};
                        font-size: 1.5rem;
                        margin-bottom: 0.75rem;
                        font-weight: bold;
                        padding-left: 0.5rem;
                    '>Dryers</h2>
                """, unsafe_allow_html=True)
                
                for dryer in dryers:
                    display_machine(dryer, "Dryer")

            # Update timestamp
            st.markdown(
                f"""
                <div style='
                    text-align: center;
                    color: {HARVARD_CRIMSON};
                    font-size: 1rem;
                    margin-top: 1rem;
                    opacity: 0.7;
                '>
                    Last updated: {datetime.now().strftime('%I:%M:%S %p')}
                </div>
                """,
                unsafe_allow_html=True
            )

        time.sleep(2)
        st.experimental_rerun()

if __name__ == "__main__":
    main() 
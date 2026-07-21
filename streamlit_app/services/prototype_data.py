import pandas as pd
import numpy as np

def get_overview_kpis():
    """Returns top-level operational metrics for the Overview page."""
    return {
        "total_flights": "6,842,105",
        "total_flights_sub": "+1.2% YoY",
        "total_flights_positive": True,
        "avg_delay_rate": "21.4%",
        "avg_delay_sub": "+1.8%",
        "avg_delay_positive": False,
        "avg_arr_delay": "18.6 min",
        "avg_arr_sub": "+2.1 min",
        "avg_arr_positive": False,
        "cancel_rate": "1.82%",
        "cancel_rate_sub": "-0.3%",
        "cancel_rate_positive": True,
    }

def get_monthly_delay_trend():
    """Provides monthly delay rate performance for 2025."""
    return pd.DataFrame({
        "Month": ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"],
        "DelayRate": [18.2, 16.5, 19.4, 17.8, 20.1, 28.5, 27.2, 23.4, 15.8, 16.2, 17.5, 29.1]
    })

def get_delay_causes_breakdown():
    """Provides accumulated delay minutes distribution by cause."""
    return pd.DataFrame({
        "Cause": ["Late Aircraft", "Carrier", "Weather", "NAS"],
        "Percentage": [38, 26, 18, 18],
    })

def get_explorer_data():
    """Generates a rich synthetic dataset ensuring data presence across common filter combinations."""
    carriers = ["Delta Air Lines", "American Airlines", "United Airlines", "Southwest Airlines", "JetBlue"]
    origins = ["KATL", "KORD", "KDFW", "KDEN", "KJFK"]
    dests = ["KLAX", "KMIA", "KSFO", "KBOS", "KSEA", "KORD", "KDFW"]
    months = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]
    
    rows = []
    np.random.seed(42)
    
    # Generate 1,000 synthetic flight entries
    for i in range(1, 1001):
        carrier = np.random.choice(carriers, p=[0.3, 0.25, 0.2, 0.15, 0.1])
        origin = np.random.choice(origins, p=[0.35, 0.2, 0.2, 0.15, 0.1])
        valid_dests = [d for d in dests if d != origin]
        dest = np.random.choice(valid_dests)
        month = np.random.choice(months, p=[0.08, 0.07, 0.08, 0.08, 0.09, 0.11, 0.1, 0.09, 0.07, 0.08, 0.07, 0.08])
        
        hour = np.random.randint(6, 23)
        minute = int(np.random.choice([0, 15, 30, 45]))
        if hour < 12:
            dep_window = "Morning"
        elif hour < 18:
            dep_window = "Afternoon"
        else:
            dep_window = "Evening"

        prob = round(float(np.random.uniform(0.1, 0.95)), 3)
        status = "CRITICAL" if prob > 0.8 else ("HIGH" if prob > 0.5 else "LOW")

        rows.append({
            "Flight": f"FL-{1000 + i}",
            "Carrier": carrier,
            "Origin": origin,
            "Destination": dest,
            "SchedDep": f"{hour:02d}:{minute:02d}",
            "DepWindow": dep_window,
            "DelayProb": prob,
            "DelayProbPct": f"{prob * 100:.1f}%",
            "Status": status,
            "Month": month,
        })
    return pd.DataFrame(rows)
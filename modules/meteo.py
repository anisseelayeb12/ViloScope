import requests
import pandas as pd
import datetime

def get_previsions(lat, lon):
    # Prévisions sur 7 jours via Open-Meteo (sans clé API)
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": lat,
        "longitude": lon,
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_sum",
            "windspeed_10m_max",
            "weathercode",
        ],
        "current_weather": True,
        "timezone": "Europe/Paris",
        "forecast_days": 7,
    }
    try:
        r = requests.get(url, params=params, timeout=10)
        r.raise_for_status()
        data = r.json()
        current = data.get("current_weather", {})
        daily = data.get("daily", {})
        df = pd.DataFrame({
            "Date":             pd.to_datetime(daily["time"]).to_series().dt.strftime("%d/%m").values,
            "Max (C)":          [round(v, 1) for v in daily["temperature_2m_max"]],
            "Min (C)":          [round(v, 1) for v in daily["temperature_2m_min"]],
            "Precipitations (mm)": [round(v, 1) for v in daily["precipitation_sum"]],
            "Vent max (km/h)":  [round(v, 1) for v in daily["windspeed_10m_max"]],
        })
        return current, df
    except Exception:
        return None, None


def get_climat_annuel(lat, lon):
    # Températures et précipitations moyennes sur les 12 derniers mois
    today = datetime.date.today()
    start = today.replace(year=today.year - 1).strftime("%Y-%m-%d")
    end = today.strftime("%Y-%m-%d")
    url = "https://archive-api.open-meteo.com/v1/archive"
    params = {
        "latitude": lat,
        "longitude": lon,
        "start_date": start,
        "end_date": end,
        "daily": ["temperature_2m_max", "temperature_2m_min", "precipitation_sum"],
        "timezone": "Europe/Paris",
    }
    try:
        r = requests.get(url, params=params, timeout=15)
        r.raise_for_status()
        data = r.json()
        daily = data.get("daily", {})
        df = pd.DataFrame({
            "Date":    pd.to_datetime(daily["time"]),
            "tmax":    daily["temperature_2m_max"],
            "tmin":    daily["temperature_2m_min"],
            "precip":  daily["precipitation_sum"],
        })
        df["mois"] = df["Date"].dt.to_period("M").astype(str)
        result = df.groupby("mois").agg(
            tmax=("tmax", "mean"),
            tmin=("tmin", "mean"),
            precip=("precip", "sum"),
        ).reset_index()
        result.columns = ["Mois", "Temp max moy (C)", "Temp min moy (C)", "Precipitations totales (mm)"]
        result["Temp max moy (C)"] = result["Temp max moy (C)"].round(1)
        result["Temp min moy (C)"] = result["Temp min moy (C)"].round(1)
        result["Precipitations totales (mm)"] = result["Precipitations totales (mm)"].round(1)
        return result
    except Exception:
        return None


def code_vers_description(code):
    # Traduction des codes météo WMO en français
    table = {
        0: "Ciel degagé",
        1: "Peu nuageux", 2: "Partiellement nuageux", 3: "Couvert",
        45: "Brouillard", 48: "Brouillard givrant",
        51: "Bruine legere", 61: "Pluie legere", 63: "Pluie moderee", 65: "Pluie forte",
        71: "Neige legere", 73: "Neige moderee", 75: "Neige forte",
        80: "Averses legeres", 81: "Averses", 82: "Averses violentes",
        95: "Orage", 99: "Orage avec grele",
    }
    return table.get(int(code), f"Code {code}")

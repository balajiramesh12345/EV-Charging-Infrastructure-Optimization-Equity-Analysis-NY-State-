# EV Charging Infrastructure Optimization & Equity Analysis

A geospatial decision-support system for optimizing EV charging infrastructure using equity, corridor coverage, and demand-risk analytics.

---

## Overview

This project develops a **data-driven planning framework** to support strategic deployment of EV charging infrastructure across New York State.

The system addresses a core planning question:

> **Where should EV charging stations be placed to balance spatial equity and corridor network efficiency?**

In addition, it enables **scenario-based analysis** to evaluate how changes in policy, adoption rates, and incentives influence EV uptake, emissions, and infrastructure demand over time.

---

## Key Features

### Spatial Explorer
- Identifies **charging infrastructure gaps** along transportation corridors  
- Maps **equity coverage for disadvantaged communities (DACs)**  
- Evaluates **queue risk and demand pressure**  
- Generates **priority zones for station placement**  
- Supports **interactive multi-criteria weighting**  

### Scenario Analysis
- Models **EV adoption dynamics over time**  
- Simulates impact of:
  - Incentives  
  - Growth rates  
  - Replacement rates  
- Projects:
  - EV adoption  
  - CO₂ emissions  
  - Infrastructure demand  

---

## System Architecture

The platform integrates spatial analysis and scenario modeling into a unified decision-support workflow:

1. **Data Processing Layer**
   - GeoPandas-based spatial preprocessing  
   - Integration of geographic, infrastructure, and socio-economic datasets  

2. **Analysis Layer**
   - Corridor gap detection  
   - Multi-criteria scoring (equity + efficiency + risk)  
   - Grid-based spatial aggregation  

3. **Interface Layer**
   - Streamlit-based interactive dashboard  
   - Real-time parameter tuning and visualization  

---

## Data Sources

### Geographic Data
- NY State boundaries and county shapefiles  
- Disadvantaged Community (DAC) designations  
- Alternative fuel corridors  
- Charging station locations  

### Historical & System Data
- Vehicle registrations (ICEV, BEV, PHEV)  
- Vehicle miles traveled (VMT)  
- CO₂ emissions  
- Incentive programs  

---

## Methodology

The system combines:

- **Corridor-based accessibility analysis**  
- **Equity-driven spatial prioritization**  
- **Multi-criteria decision analysis (MCDA)**  
- **Scenario-based system modeling**  

Each location is scored based on:
- Corridor gap
- Equity (DAC coverage)
- Queue risk
- Low-density accessibility  

These scores are combined into a **priority index** for infrastructure placement.

---

## Tech Stack

- Python (GeoPandas, Pandas)
- Streamlit (interactive UI)
- Folium / Leaflet (mapping)
- GeoJSON / shapefiles

---

## My Contribution

- Built the **Spatial Explorer module** for infrastructure gap detection and priority analysis  
- Designed and implemented the **geospatial data processing pipeline** using GeoPandas  
- Developed the **multi-criteria decision framework** for station placement  
- Contributed to **interactive visualization and interface design**  

---

## Future Work

- Integration with **real-time data sources and APIs**  
- Expansion to **multi-state and national-scale analysis**  
- Incorporation of **optimization models (e.g., OR-Tools / Gurobi)**  
- Policy-driven scenario modeling for **incentive and infrastructure planning**  
- Collaboration with **public agencies and stakeholders**  

---

## Running the App

```bash
pip install -r requirements.txt
streamlit run app.py

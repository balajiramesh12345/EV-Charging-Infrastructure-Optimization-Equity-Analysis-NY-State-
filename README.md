# EV Charging Infrastructure Optimization & Equity Analysis

A geospatial decision-support system for optimizing EV charging infrastructure using equity, corridor coverage, and demand-risk analytics.

---

## Overview

This project develops a **data-driven planning framework** to support strategic deployment of EV charging infrastructure across New York State.

<img width="1134" height="754" alt="image" src="https://github.com/user-attachments/assets/f82bca74-3f9c-4632-bb59-7f5376609df3" />


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
<img width="1824" height="879" alt="image" src="https://github.com/user-attachments/assets/1a720823-41cd-4f24-8a5b-8b898cfe59e3" />
<img width="1275" height="858" alt="image" src="https://github.com/user-attachments/assets/577a1af1-8408-4131-b44a-6ef07fa6c3ae" />
<img width="1431" height="899" alt="image" src="https://github.com/user-attachments/assets/30e1485e-c894-4e3a-92b6-459ad4d35ffd" />
<img width="1414" height="887" alt="image" src="https://github.com/user-attachments/assets/9e2b6ae7-b21e-46c9-a6f0-12fb2a29fbd3" />
<img width="1268" height="589" alt="image" src="https://github.com/user-attachments/assets/072596a4-4c8f-4d42-81d8-c7844988d4ec" />



### Scenario Analysis
- Models **EV adoption dynamics over time**  
- Simulates impact of:
  - Incentives  
  - Growth rates  
  - Replacement rates
  - <img width="1179" height="820" alt="image" src="https://github.com/user-attachments/assets/2bfef529-442f-4b4a-a0e8-838f50be117e" />

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

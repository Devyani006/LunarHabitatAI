[Lunar_Habitat_AI_Developer_Research_Documentation.docx](https://github.com/user-attachments/files/31424328/Lunar_Habitat_AI_Developer_Research_Documentation.docx)
# 🌙 Lunar Habitat AI

### AI-Powered Decision Support System for Lunar South Pole Habitat Site Selection

Lunar Habitat AI is an **AI-driven decision support system** designed to identify and rank potential lunar habitat sites by combining **terrain analysis, solar illumination, water-ice potential, radiation modelling, clustering, and live space-weather data**.

The goal is simple:

> **Turn complex lunar environmental data into an explainable recommendation for where a future habitat should be built.**

---

## 🚀 What Does It Do?

The system evaluates candidate locations across multiple mission-critical factors:

- 🏔️ **Terrain & Landing Safety**
- ☀️ **Solar Illumination**
- 💧 **Water-Ice Potential**
- ☢️ **Radiation Exposure**
- 🌑 **Terrain Shielding / Sky View Factor**
- 🌌 **Live Space Weather**
- 🤖 **ML-Based Site Clustering & Ranking**
- 📊 **Multi-Criteria Decision Analysis using AHP**

The result is an interactive decision-support interface that provides:

**Site → Environmental Analysis → ML Evaluation → AHP Ranking → Habitat Recommendation**

---

## 🧠 System Architecture

```text
NASA / Scientific Datasets
          │
          ▼
   Data Processing Pipeline
          │
          ├── Terrain & Elevation
          ├── Solar Illumination
          ├── Water-Ice Proxy
          └── Terrain / Landing Factors
          │
          ▼
     Feature Engineering
          │
          ├───────────────┐
          ▼               ▼
 Radiation ML       Site Clustering ML
     Model                Model
          │               │
          └───────┬───────┘
                  ▼
             AHP Ranking
                  │
                  ▼
       Final Habitat Suitability
                  │
          ┌───────┴────────┐
          ▼                ▼
   Site Recommendation   Explainable UI
          │
          ▼
   Live NOAA Space Weather

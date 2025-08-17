# Elyx Journey — Member 360

🚀 **Elyx Journey — Member 360** is a **Streamlit-based interactive dashboard** designed to give a **360° view of a member’s health journey**.  
It integrates **key metrics, timeline decisions, progress tracking, and communication logs** into one sleek app.

---

## ✨ Features

- **📂 Sidebar Navigation** — Quick access to all major sections:
  - 🚀 Member Profile  
  - 📊 Key Metrics  
  - 🗺️ Journey Timeline  
  - 📈 Progress Metrics  
  - 💬 Conversation Log  

- **🎨 Theme Toggle** — Switch between **Light** and **Dark** mode for a personalized experience.  

- **📊 Key Metrics Dashboard** — Summarizes total hours across multiple health pillars (Doctor, Performance, Nutrition, PT, Concierge).  

- **🗺️ Journey Timeline**  
  - Searchable & expandable decision logs.  
  - Decisions color-coded by type (Medication, Therapy, Diagnostics, Lifestyle, Logistics, etc.).  
  - Detailed rationale, before/after changes, and linked communication trail.  

- **📈 Progress Metrics**  
  - Interactive date-range filtering.  
  - Altair charts (stacked area + HRV line chart) for trends.  
  - Reset option to restore full range.  

- **💬 Conversation Log**  
  - Searchable message history.  
  - Styled chat bubbles with speaker, timestamp, and highlighted keywords.  

---

📂 Project Structure
elyx-journey/
│
├── app.py # Main Streamlit app
├── data/ # Data files (JSON/CSV)
│ ├── persona.json
│ ├── decisions.json
│ ├── messages.json
│ └── internal_metrics.csv
├── docs/ # Documentation assets (screenshots, etc.)
│ └── screenshots/
│ ├── light_mode.png
│ └── dark_mode.png
└── requirements.txt # Dependencies

🚀 Roadmap / Future Enhancements

📅 Calendar-based scheduling view.

📊 Exportable PDF health summaries.

🔔 Notification system for missed/updated intervals.

🤖 AI insights on conversation logs.

🙌 Acknowledgements

Built with ❤️ using Streamlit

Inspired by real-world member care journey trackin


---

## 📄 requirements.txt

```txt
streamlit
pandas
altair

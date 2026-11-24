# 🌍 ClimateWise - Climate Change Agent

A simple AI agent (LlamaIndex + Groq) with a Streamlit chat UI.
It answers climate change questions, explores real daily climate data for **Cairo, Egypt (2015-2025, NASA POWER)**, and estimates a personal carbon footprint.

## How it works

The agent (`FunctionAgent`) decides which tool to use for each question:

| Tool | What it does |
|---|---|
| `climate_knowledge_base` | RAG over the text files in `knowledge/` (causes, effects, solutions, dataset info) |
| `get_yearly_stats` | Average / max / min temperature, rain, humidity and hot days for one year |
| `get_temperature_trend` | Yearly average temperature and the warming trend |
| `get_hottest_days` | Hottest days of a given year |
| `calculate_carbon_footprint` | Yearly CO2 estimate from electricity and car use |

- **LLM:** `openai/gpt-oss-120b` on Groq (free API key). Groq changes its model list from time to time; if you get a "model does not exist" error, set another tool-calling model in `LLM_MODEL` in `config.py` (or the `GROQ_MODEL` env variable)
- **Embeddings:** `BAAI/bge-small-en-v1.5` (FastEmbed, runs on CPU)
- **Memory:** the chat history is sent to the agent on every message

## Pages

- **💬 Chat:** talk to the agent, with a typing effect and a status box that shows which tools were used.
- **📊 Dashboard:** pick a year and see metrics and charts (yearly temperature, hot days, monthly temperature and rain).
- **🌱 Carbon calculator:** sliders for electricity and car use, with a live result.

## Project structure

```
climate-agent/
├── app.py              # Streamlit app: pages, chat, sidebar
├── style.py            # custom CSS (animated header, fade-in, hover effects)
├── dashboard.py        # Dashboard page + carbon calculator page
├── agent.py            # builds the RAG index, the tools and the agent
├── tools.py            # the functions the agent can call
├── data_loader.py      # reads the NASA csv file
├── config.py           # settings + the system prompt
├── requirements.txt
├── data/               # the csv data file
├── knowledge/          # text files used by RAG
└── .streamlit/         # config.toml (theme) + secrets.toml.example
```

## Run locally

```bash
pip install -r requirements.txt
export GROQ_API_KEY="your_key"      # get a free key from console.groq.com
streamlit run app.py
```

You can also skip the export and paste the key in the app sidebar.
The first run downloads the embedding model, so it takes a bit longer.

## Deploy on Streamlit Community Cloud

1. Push this folder to a GitHub repository (the `data/` and `knowledge/` folders must be included).
2. Go to [share.streamlit.io](https://share.streamlit.io) and click **Create app**.
3. Choose your repository, branch, and set **Main file path** to `app.py`.
4. Open **Advanced settings**, choose **Python 3.11** (or 3.12), and in **Secrets** paste:
   ```toml
   GROQ_API_KEY = "your_groq_key_here"
   ```
5. Click **Deploy**.

## Change the data

1. Download a new **daily** csv from [NASA POWER](https://power.larc.nasa.gov/data-access-viewer/) and put it in `data/`.
2. In `config.py`, update `DATA_PATH` and `LOCATION_NAME`.
3. Make sure the csv has these columns: `YEAR, DOY, T2M, T2M_MAX, T2M_MIN, RH2M, PRECTOTCORR`
   (the NASA text header at the top of the file is skipped automatically).
4. Update `knowledge/dataset_info.txt` so it describes the new location and dates.
   The system prompt in `config.py` also mentions "2015-2025", so update it too.

If you use a different kind of data (not NASA POWER), edit `data_loader.py` and `tools.py`.

## Example questions

- How does climate change affect agriculture?
- How did the average temperature change from 2015 to 2025?
- What were the hottest days in 2024?
- I use 300 kWh monthly and drive 100 km weekly. What is my footprint?
- Will it rain in Cairo tomorrow? (out of scope, the agent should say it cannot forecast)

## Limitations

- The data covers one location and only 11 years, so it cannot prove a long-term trend.
- NASA POWER values come from satellite models (MERRA-2), not from a ground weather station.
- The carbon footprint uses rough average emission factors (0.5 kg CO2/kWh, 0.2 kg CO2/km).

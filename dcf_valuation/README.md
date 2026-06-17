# 📈 DCF Stock Valuation Tool

> Automated Discounted Cash Flow analysis for any US-listed stock — built by Vansh Ajmera, Economics @ IIT Kanpur

---

## 🎯 What It Does

This tool automatically values any US-listed stock using the **Discounted Cash Flow (DCF)** method — the same technique used by equity analysts at Goldman Sachs, Morgan Stanley, and every major investment bank.

Given a stock ticker, it:
- Fetches real financial statements via Alpha Vantage API
- Calculates Free Cash Flow and historical CAGR
- Projects FCF forward 5 years
- Calculates WACC using CAPM from scratch
- Discounts everything to present value → Intrinsic Value per Share
- Compares vs market price → Undervalued or Overvalued verdict

---

## 🖥️ Demo

---

## 🏗️ Project Structure
---

## ⚙️ How It Works

### 1. Free Cash Flow

We calculate historical FCF going back 20 years and compute CAGR.

### 2. FCF Projection

Growth rate is capped between 2%–25% to stay realistic.

### 3. WACC

### 4. DCF Valuation

### 5. Terminal Value (Gordon Growth Model)

---

## 📊 Sample Output — Apple (AAPL)

| Metric | Value |
|---|---|
| FCF (2025) | $98.77B |
| FCF CAGR (20yr) | 24.39% |
| WACC | 10.25% |
| Terminal Value | $3,891B |
| Enterprise Value | $3,109B |
| Intrinsic Value | ~$211 |
| Market Price | $291 |
| Verdict | 🔴 Overvalued by 27% |

### Scenario Analysis
| Scenario | Growth | WACC | Intrinsic Value | Upside |
|---|---|---|---|---|
| 🐻 Bear | 5% | 12.25% | $72 | -75% |
| 📊 Base | 10% | 10.25% | $114 | -61% |
| 🐂 Bull | 20% | 8.25% | $236 | -19% |

---

## 🚀 How to Run

### 1. Clone the repo
```bash
git clone https://github.com/VanshA17/projects.git
cd projects/dcf_valuation
```

### 2. Install dependencies
```bash
pip install yfinance pandas numpy matplotlib seaborn scipy statsmodels streamlit requests
```

### 3. Add your API key
Get a free key at [alphavantage.co](https://www.alphavantage.co/support/#api-key)

Replace `your_alpha_vantage_key_here` in `data_fetcher.py` and `wacc_calculator.py`

### 4. Run the Streamlit app
```bash
streamlit run app.py
```

### 5. Or run the demo notebook
```bash
jupyter notebook demo.ipynb
```

---

## 🛠️ Tech Stack

| Tool | Purpose |
|---|---|
| `pandas` | Financial data wrangling |
| `numpy` | DCF calculations |
| `matplotlib` / `seaborn` | Charts and heatmaps |
| `requests` | Alpha Vantage API calls |
| `streamlit` | Interactive web app |
| `Alpha Vantage API` | Financial data source |

---

## 💡 Key Finance Concepts Used
- Discounted Cash Flow (DCF)
- Free Cash Flow (FCF)
- Capital Asset Pricing Model (CAPM)
- Weighted Average Cost of Capital (WACC)
- Gordon Growth Model (Terminal Value)
- Sensitivity Analysis
- Bull/Base/Bear Scenario Modeling

---

## 👤 Author
**Vansh Ajmera**  
Economics, IIT Kanpur  
[GitHub](https://github.com/VanshA17) | [LinkedIn](https://www.linkedin.com/in/vansh-ajmera-347a56339/)

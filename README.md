# 🌾 Kaggriculture — Competition Agent

## 🏆 Competition Overview
- **Competition name:** Kaggriculture (Kaggle Simulation Competition)
- **Link:** [https://www.kaggle.com/competitions/kaggriculture](https://www.kaggle.com/competitions/kaggriculture)
- **Type:** Turn-based farming simulation, two AI agents compete head-to-head
- **Goal:** Earn the most money by end of 30-day season (720 turns)
- **Prize pool:** $50,000 total ($5,000 for each of top 10 places)
- **Deadline:** Final submission September 30, 2026

## 🎮 What We Are Solving
Two players spawn on separate 10x10 farm grids, competing over a 30-day season (720 turns). The objective is to intelligently manage resources by planting, watering, and harvesting crops, raising animals, and trading on a highly dynamic market.

Key mechanics to master:
- **Dynamic Economy:** Market prices react heavily to supply and demand in real time. Over-supplying crashes prices.
- **Town Shops:** As the season progresses, town shops (like bakeries and smoothie shops) unlock, spiking demand for specific produce like eggs and strawberries.
- **Win Condition:** The player with the most coins in the bank at the end of the season wins. Unsold inventory is not counted toward the final score.

## 🧠 Our Strategy & Approach
Our agent relies on a multi-phased timeline and a modular architecture to scale operations seamlessly:

- **Phase 1 (Days 1-5):** Wheat loop for a fast cash flow foundation. Wheat's 2-day cycle allows rapid early compounding.
- **Phase 2 (Days 6-15):** Shift into Melon waves and Carrot planting with fertilizer integration (high yield ROI). Melons boast a 250 base price with up to 6 yield.
- **Phase 3 (Days 10+):** Enter animal husbandry. Geese are purchased first (daily eggs), pivoting to cows based on specific shop unlocks (e.g., bakeries opening).
- **Phase 4 (Days 15+):** Land expansion and strawberry plantations for compounding, ongoing yields.

**Economy & Labor Strategy:**
- **Market:** Employs batch selling (max 10 units/turn) to prevent price crashes. Premium crops are held in inventory if their price dips below minimum thresholds.
- **Labor:** Automatically hires farm hands when over 15 tiles require attention, capped at a maximum of 2 hires per day to respect Fibonacci cost scaling.

## 📁 Project Structure
```text
kaggriculture/
├── main.py                    # Agent entry point (agent() function)
├── strategy/
│   ├── crop_manager.py        # Crop lifecycle: plant/water/fertilize/harvest logic
│   ├── animal_manager.py      # Animal care: feed/care/harvest/fertilizer collection
│   ├── market_manager.py      # Buy/sell orders, land expansion, hiring decisions
│   └── movement.py            # BFS pathfinding, unit task management
├── utils/
│   ├── state.py               # GameState wrapper around raw obs dict
│   └── constants.py           # All game constants (crops, animals, prices, timings)
├── tests/
│   └── test_agent.py          # Local testing suite
├── requirements.txt
└── README.md
```

## ⚙️ Setup & Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/kumardhruv88/kaggriculture.git
   cd kaggriculture
   ```
2. Install the necessary packages:
   ```bash
   pip install kaggle-environments kaggle
   ```
3. Set up your Kaggle API token (place your `kaggle.json` in `~/.kaggle/`).
4. Accept the competition rules at [kaggle.com/competitions/kaggriculture](https://www.kaggle.com/competitions/kaggriculture).

## 🧪 How to Test the Agent Locally

**Quick smoke test (72 steps):**
```python
from kaggle_environments import make
from main import agent

env = make("kaggriculture", configuration={"episodeSteps": 72}, debug=True)
env.run([agent, "random"])
final = env.steps[-1]

print(f"Our agent: ${final[0].reward:.0f}")
print(f"Random agent: ${final[1].reward:.0f}")
```

**Full season test (720 steps):**
```python
env = make("kaggriculture", configuration={"episodeSteps": 720}, debug=True)
env.run([agent, "random"])
final = env.steps[-1]

print(f"Our agent: ${final[0].reward:.0f}")
print(f"Random agent: ${final[1].reward:.0f}")
env.render(mode="ipython", width=1200, height=800)
```

**Self-play test:**
```python
env.run([agent, agent])
```

**Save replay for visualization:**
```python
import json
with open("replay.json", "w") as f:
    json.dump(env.toJSON(), f)
```

## 📊 Key Game Mechanics We Exploit
- **Melons:** Features a 250 base price and up to 6 yield. The `above_target=3.6` mechanic means an oversupply crashes the price hard, so our agent carefully paces sales.
- **Eggs:** Exhibits hinge pricing, meaning prices spike sharply when bakeries or brunch spots unlock.
- **Fertilizer:** Doubles the per-day yield bonus for 3 days. We prioritize fertilizing based on ROI: Melon > Carrot > Wheat.
- **Farm hands:** Follows a Fibonacci cost curve (1, 1, 2, 3, 5...). We strictly cap hiring at 2 per day to maintain a positive ROI.
- **Shed cap:** Maximum 100 items. We trigger an emergency bulk sell at 80% capacity to prevent overflow waste.

## 🚀 Submission
```bash
kaggle competitions submit kaggriculture -f main.py -m "describe your version"
```

## 📈 Progress Tracking
| Version | Strategy | Score vs Random | Notes |
|---------|----------|-----------------|-------|
| v0.1 | Wheat loop baseline | TBD | Initial scaffold |
| v0.2 | + Melon waves | TBD | High value crop focus |
| v0.3 | + Animals + BFS | TBD | Full strategy |

## 🔗 Resources
- **Competition page:** [https://www.kaggle.com/competitions/kaggriculture](https://www.kaggle.com/competitions/kaggriculture)
- **My Kaggle profile:** [https://www.kaggle.com/dhruvkumar11](https://www.kaggle.com/dhruvkumar11)
- **kaggle-environments docs:** [https://github.com/Kaggle/kaggle-environments](https://github.com/Kaggle/kaggle-environments)

# Tennis Momentum Visualizer
Creates a clean visualization through Streamlit showing momentum trends from ATP tennis Grand Slam matches.

In tennis, momentum refers to  the perceived advantage a player has during a match, often fluctuating throughout. It can be influenced by both physical and mental aspects, and analyzing these trends gives some more insights into match outcomes. 

Based on point by point data by Jeff Sackmann, this Streamlit app visualizes momentum through any Grand Slam match from 2011-2024. Built on the lightning fast Polars, users can quickly see set by set breakdowns, line charts, summaries, and more for the most famous matches of all time.

## Installation

1. Clone the repo with

```bash
git  clone https://github.com/austindinhh/tennis-momentum-visualizer.git
```
2. Install dependencies  

```bash
    pip install -r requirements.txt
  ```
  
  3. Run Streamlit app
  
  ```bash
  python -m streamlit run app/main.py
  ```

## Getting Started
First run the Streamlit app through the terminal as instructed. The homepage will load in a local browser where further instructions can be found to load any match. 

## Future
- Reformat homepage 
- Add more visualizations 
- Write unit tests 

## Acknowledgements
All data is from Jeff Sackmann based on https://github.com/JeffSackmann/tennis_slam_pointbypoint. 
# InterviewAI 🎯

An AI-powered technical interview preparation chatbot built with **Python**, **Streamlit**, and **Groq API** (LLaMA 3.3 70B).

## Features

- **7 Job Roles** — Software Engineer, AI/ML Engineer, Backend, Full Stack, Data Scientist, Systems Engineer, DevOps
- **30+ Topics** — Role-specific topic lists tailored to each career path
- **MCQ & Open-ended Modes** — Multiple choice or typed answers
- **Adaptive Difficulty** — Auto-adjusts Easy/Medium/Hard based on your performance
- **Real-time Scoring** — Per-answer score (1–10) with strengths, gaps, and model answers
- **Mock Interview Mode** — Timed questions to simulate real interview pressure
- **Hints & Skip** — Type `hint` for a clue or `skip` to move on
- **Session Debrief** — Full AI-generated end-of-session performance summary
- **Dark Theme UI** — Glassmorphism cards, animated SVG score rings, custom CSS

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | Streamlit + Custom CSS |
| Backend | Python 3.10+ |
| AI Model | LLaMA 3.3 70B via Groq API |
| Env Management | python-dotenv |

## Project Structure

```
interviewAi/
├── app.py           # Streamlit UI, session state, chat flow
├── interviewer.py   # Question/MCQ generation, session summaries
├── evaluator.py     # Answer scoring and hint generation
├── prompts.py       # All LLM prompt templates
├── utils.py         # Score helpers, timers, adaptive difficulty
├── requirements.txt
├── .env.example
└── README.md
```

## Setup & Run

```bash
# 1. Clone the repo
git clone https://github.com/emaniftikharr/interviewAi.git
cd interviewAi

# 2. Install dependencies
pip install -r requirements.txt

# 3. Add your Groq API key
cp .env.example .env
# Edit .env and paste your GROQ_API_KEY

# 4. Run the app
streamlit run app.py
```

Get your free Groq API key at [console.groq.com](https://console.groq.com).

## Usage

1. Select your **target role** and **topic** from the sidebar
2. Choose **difficulty** and **question type** (MCQ or Open-ended)
3. Pick **Practice** or **Mock Interview** mode
4. Click **Start Interview** and answer questions
5. Type `hint` for a clue, `skip` to move on
6. Click **End Session** in the sidebar for your full debrief

## License

MIT

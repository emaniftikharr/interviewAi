"""
interviewer.py — Question generation, follow-ups, and session summaries via Groq.
"""

import logging

import json
import re

from groq import Groq
from prompts import (
    QUESTION_GENERATION_PROMPT,
    MCQ_GENERATION_PROMPT,
    FOLLOW_UP_PROMPT,
    SESSION_SUMMARY_PROMPT,
    WELCOME_MESSAGE,
    PRACTICE_MODE_INSTRUCTIONS,
    MOCK_MODE_INSTRUCTIONS,
)

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────────────────────────────────────
# CONSTANTS — imported by app.py for UI dropdowns
# ──────────────────────────────────────────────────────────────────────────────

DIFFICULTIES = ["Easy", "Medium", "Hard"]

ROLES = [
    "Software Engineer",
    "AI/ML Engineer",
    "Backend Engineer",
    "Full Stack Engineer",
    "Data Scientist",
    "Systems Engineer",
    "DevOps Engineer",
]

# Topics per role — each key must match an entry in ROLES exactly
ROLE_TOPICS: dict[str, list[str]] = {
    "Software Engineer": [
        "Data Structures",
        "Algorithms",
        "Object-Oriented Programming",
        "Complexity Analysis",
        "System Design",
        "Databases",
        "Networking & Web",
        "Version Control (Git)",
        "Testing",
        "Operating Systems",
        "Behavioral",
    ],
    "AI/ML Engineer": [
        "Machine Learning",
        "Deep Learning",
        "Natural Language Processing",
        "Computer Vision",
        "Mathematics for ML",
        "Data Preprocessing",
        "Model Evaluation & Metrics",
        "Python & ML Libraries",
        "MLOps",
        "Behavioral",
    ],
    "Backend Engineer": [
        "APIs & REST",
        "Databases",
        "System Design",
        "Data Structures",
        "Algorithms",
        "Caching & Performance",
        "Authentication & Security",
        "Message Queues",
        "Microservices",
        "Behavioral",
    ],
    "Full Stack Engineer": [
        "Frontend Development",
        "Backend Development",
        "Databases",
        "APIs & REST",
        "System Design",
        "Web Security",
        "Performance Optimization",
        "Version Control (Git)",
        "Testing",
        "Behavioral",
    ],
    "Data Scientist": [
        "Statistics & Probability",
        "Machine Learning",
        "Data Wrangling & EDA",
        "SQL & Databases",
        "Python for Data Science",
        "Data Visualization",
        "Feature Engineering",
        "Model Evaluation & Metrics",
        "Big Data Tools",
        "Behavioral",
    ],
    "Systems Engineer": [
        "Operating Systems",
        "Networking & Protocols",
        "C/C++ Programming",
        "Memory Management",
        "Concurrency & Threads",
        "Embedded Systems",
        "System Design",
        "Performance & Profiling",
        "Version Control (Git)",
        "Behavioral",
    ],
    "DevOps Engineer": [
        "CI/CD Pipelines",
        "Containerization (Docker/K8s)",
        "Cloud Platforms",
        "Infrastructure as Code",
        "Networking & Security",
        "Monitoring & Observability",
        "Scripting & Automation",
        "Databases",
        "Version Control (Git)",
        "Behavioral",
    ],
}

# Flat deduplicated list for any legacy use
TOPICS = sorted({t for topics in ROLE_TOPICS.values() for t in topics})

# Seconds per question in Mock Interview mode
MOCK_TIME_LIMITS = {
    "Easy": 120,   # 2 min
    "Medium": 180, # 3 min
    "Hard": 300,   # 5 min
}

# ──────────────────────────────────────────────────────────────────────────────
# FALLBACK QUESTIONS (used when the API is unavailable)
# ──────────────────────────────────────────────────────────────────────────────

_FALLBACK_QUESTIONS: dict[str, dict[str, str]] = {
    "Data Structures": {
        "Easy":   "What is the difference between an array and a linked list?",
        "Medium": "Explain how a hash map works internally and how it handles collisions.",
        "Hard":   "Compare AVL trees and Red-Black trees — when would you choose one over the other?",
    },
    "Algorithms": {
        "Easy":   "Explain how binary search works and what its time complexity is.",
        "Medium": "Describe the two-pointer technique and give an example problem where it applies.",
        "Hard":   "Explain Dijkstra's algorithm, its time complexity, and when you'd prefer Bellman-Ford instead.",
    },
    "Object-Oriented Programming": {
        "Easy":   "What are the four pillars of OOP? Briefly explain each.",
        "Medium": "What is the difference between method overloading and method overriding?",
        "Hard":   "Explain the SOLID principles and give a real-world example for each.",
    },
    "Complexity Analysis": {
        "Easy":   "What does Big O notation represent and why is it useful?",
        "Medium": "What is the time and space complexity of merge sort? Explain why.",
        "Hard":   "Analyse the time complexity of a recursive Fibonacci implementation vs a dynamic programming approach.",
    },
    "Databases": {
        "Easy":   "What is the difference between SQL and NoSQL databases? Give one use case for each.",
        "Medium": "Explain what database indexing is and how it improves query performance.",
        "Hard":   "What are ACID properties? Describe how a relational database enforces them.",
    },
    "Networking & Web": {
        "Easy":   "What is the difference between HTTP GET and POST requests?",
        "Medium": "Explain REST API design principles and what makes an API RESTful.",
        "Hard":   "Describe what happens step-by-step when you type a URL into a browser and press Enter.",
    },
    "Version Control (Git)": {
        "Easy":   "What is the difference between git merge and git rebase?",
        "Medium": "Explain the Git branching strategy you would use on a team of 5 engineers.",
        "Hard":   "How would you recover a commit that was accidentally removed with git reset --hard?",
    },
    "Testing": {
        "Easy":   "What is unit testing and why is it important?",
        "Medium": "What is the difference between mocking and stubbing in unit tests?",
        "Hard":   "Explain test-driven development (TDD) and describe its advantages and trade-offs.",
    },
    "Operating Systems": {
        "Easy":   "What is the difference between a process and a thread?",
        "Medium": "Explain how virtual memory works and why it is useful.",
        "Hard":   "Compare and contrast different CPU scheduling algorithms, including their trade-offs.",
    },
    "Behavioral": {
        "Easy":   "Tell me about yourself and why you're interested in this role.",
        "Medium": "Describe a challenging project you worked on using the STAR method.",
        "Hard":   "Tell me about a time you disagreed with a technical decision. How did you handle it?",
    },
    # ── AI/ML Engineer ────────────────────────────────────────────────────────
    "Machine Learning": {
        "Easy":   "What is the difference between supervised and unsupervised learning?",
        "Medium": "Explain the bias-variance trade-off and how it affects model selection.",
        "Hard":   "Compare gradient boosting and random forests — when would you prefer each?",
    },
    "Deep Learning": {
        "Easy":   "What is a neural network and how does backpropagation work?",
        "Medium": "Explain vanishing gradients and how techniques like batch normalisation address them.",
        "Hard":   "Describe the Transformer architecture and explain how multi-head self-attention works.",
    },
    "Natural Language Processing": {
        "Easy":   "What is tokenisation and why is it a necessary step in NLP pipelines?",
        "Medium": "Explain the difference between word2vec and contextual embeddings like BERT.",
        "Hard":   "How would you design an end-to-end NLP pipeline for a multi-class text classification task?",
    },
    "Computer Vision": {
        "Easy":   "What is a convolutional neural network and why is it suited to image data?",
        "Medium": "Explain the role of pooling layers and how they affect spatial resolution.",
        "Hard":   "Compare object detection architectures: YOLO vs Faster R-CNN — trade-offs and use cases.",
    },
    "Mathematics for ML": {
        "Easy":   "What is a gradient and why is it central to training machine learning models?",
        "Medium": "Explain PCA — what it does geometrically and when you would use it.",
        "Hard":   "Derive the update rule for logistic regression using maximum likelihood estimation.",
    },
    "Data Preprocessing": {
        "Easy":   "What is the difference between normalisation and standardisation?",
        "Medium": "How would you handle missing values in a dataset with 30% null entries in one feature?",
        "Hard":   "Describe strategies to handle class imbalance in a binary classification problem.",
    },
    "Model Evaluation & Metrics": {
        "Easy":   "What is the difference between precision and recall?",
        "Medium": "When would you choose AUC-ROC over F1-score as your primary metric?",
        "Hard":   "Explain how cross-validation works and describe its variants (k-fold, stratified, time-series).",
    },
    "Python & ML Libraries": {
        "Easy":   "What is the difference between a list and a NumPy array?",
        "Medium": "Explain how pandas GroupBy works under the hood and common pitfalls.",
        "Hard":   "How would you optimise a slow scikit-learn pipeline for production inference?",
    },
    "MLOps": {
        "Easy":   "What is model drift and why does it matter in production?",
        "Medium": "Describe how you would version and track experiments across a team of ML engineers.",
        "Hard":   "Design a CI/CD pipeline for an ML model including retraining triggers and rollback strategy.",
    },
    # ── Backend Engineer ──────────────────────────────────────────────────────
    "APIs & REST": {
        "Easy":   "What are the main HTTP methods and when is each used?",
        "Medium": "Explain idempotency in REST APIs and why it matters for PUT vs PATCH.",
        "Hard":   "How would you design a rate-limiting system for a public REST API?",
    },
    "System Design": {
        "Easy":   "What is horizontal vs vertical scaling?",
        "Medium": "Design a URL shortener — walk through your data model and API design.",
        "Hard":   "Design a distributed message queue system that can handle 1 million messages per second.",
    },
    "Caching & Performance": {
        "Easy":   "What is a cache and why is it used?",
        "Medium": "Explain cache eviction policies (LRU, LFU, FIFO) and when to choose each.",
        "Hard":   "How would you implement a distributed cache with consistency guarantees?",
    },
    "Authentication & Security": {
        "Easy":   "What is the difference between authentication and authorisation?",
        "Medium": "Explain how JWT tokens work and their security trade-offs compared to session cookies.",
        "Hard":   "Describe how you would protect a REST API against OWASP Top 10 vulnerabilities.",
    },
    "Message Queues": {
        "Easy":   "What is a message queue and what problem does it solve?",
        "Medium": "Compare Kafka and RabbitMQ — when would you choose one over the other?",
        "Hard":   "How do you guarantee exactly-once delivery semantics in a distributed messaging system?",
    },
    "Microservices": {
        "Easy":   "What is the difference between a monolith and a microservices architecture?",
        "Medium": "Explain the Saga pattern for managing distributed transactions across microservices.",
        "Hard":   "How would you handle service discovery, load balancing, and circuit breaking in a microservices mesh?",
    },
    # ── Full Stack Engineer ───────────────────────────────────────────────────
    "Frontend Development": {
        "Easy":   "What is the difference between the DOM and the virtual DOM?",
        "Medium": "Explain the React component lifecycle and when you would use useEffect.",
        "Hard":   "How would you optimise a React application with 500+ components for rendering performance?",
    },
    "Backend Development": {
        "Easy":   "What is middleware in a web framework such as Express or Django?",
        "Medium": "Explain the request-response lifecycle in a Node.js Express application.",
        "Hard":   "How would you architect a backend to serve 10 million daily active users?",
    },
    "Web Security": {
        "Easy":   "What is Cross-Site Scripting (XSS) and how do you prevent it?",
        "Medium": "Explain CSRF attacks and the token-based defence mechanism.",
        "Hard":   "Describe a Content Security Policy and how you would configure it for a React SPA.",
    },
    "Performance Optimization": {
        "Easy":   "What is lazy loading and how does it improve web performance?",
        "Medium": "Explain how browser caching works and how cache-control headers are configured.",
        "Hard":   "Walk through a systematic approach to diagnosing and fixing a slow first contentful paint.",
    },
    # ── Data Scientist ────────────────────────────────────────────────────────
    "Statistics & Probability": {
        "Easy":   "What is the difference between mean, median, and mode?",
        "Medium": "Explain the Central Limit Theorem and why it matters in statistical inference.",
        "Hard":   "Describe how you would design an A/B test and determine the required sample size.",
    },
    "Data Wrangling & EDA": {
        "Easy":   "What steps would you take when first exploring a new dataset?",
        "Medium": "How do you detect and handle outliers in a numerical feature?",
        "Hard":   "Describe your approach to merging three large datasets with overlapping but inconsistent keys.",
    },
    "SQL & Databases": {
        "Easy":   "What is the difference between INNER JOIN and LEFT JOIN?",
        "Medium": "Explain window functions and give an example using RANK() or LAG().",
        "Hard":   "How would you optimise a slow SQL query on a table with 100 million rows?",
    },
    "Python for Data Science": {
        "Easy":   "What is the difference between `.apply()` and `.map()` in pandas?",
        "Medium": "Explain broadcasting in NumPy and give an example where it speeds up computation.",
        "Hard":   "How would you build a memory-efficient data pipeline in Python for a 50 GB CSV file?",
    },
    "Data Visualization": {
        "Easy":   "When would you use a bar chart vs a histogram?",
        "Medium": "How do you choose the right visualisation type for showing correlation between two variables?",
        "Hard":   "Design an interactive dashboard for a business stakeholder to monitor key sales KPIs.",
    },
    "Feature Engineering": {
        "Easy":   "What is one-hot encoding and when would you use it?",
        "Medium": "Explain target encoding and the risk of data leakage when applying it.",
        "Hard":   "Describe a complete feature engineering strategy for a time-series churn prediction model.",
    },
    "Big Data Tools": {
        "Easy":   "What is the difference between batch processing and stream processing?",
        "Medium": "Explain how Apache Spark distributes computation using RDDs or DataFrames.",
        "Hard":   "Design a data pipeline using Spark, Kafka, and a data warehouse for real-time analytics.",
    },
    # ── Systems Engineer ──────────────────────────────────────────────────────
    "Networking & Protocols": {
        "Easy":   "What is the difference between TCP and UDP?",
        "Medium": "Explain the TLS handshake process step by step.",
        "Hard":   "How does BGP routing work and how do autonomous systems exchange routing information?",
    },
    "C/C++ Programming": {
        "Easy":   "What is the difference between a pointer and a reference in C++?",
        "Medium": "Explain RAII and how smart pointers implement it.",
        "Hard":   "Describe undefined behaviour in C++ and give three real-world examples and how to avoid them.",
    },
    "Memory Management": {
        "Easy":   "What is the difference between the stack and the heap?",
        "Medium": "Explain memory fragmentation and strategies to mitigate it in a long-running process.",
        "Hard":   "How would you design a custom memory allocator for a latency-sensitive embedded application?",
    },
    "Concurrency & Threads": {
        "Easy":   "What is a race condition and how can it be prevented?",
        "Medium": "Explain the difference between a mutex, semaphore, and condition variable.",
        "Hard":   "Design a lock-free queue implementation and explain the ABA problem.",
    },
    "Embedded Systems": {
        "Easy":   "What is the difference between a microcontroller and a microprocessor?",
        "Medium": "Explain interrupt handling and the concept of an ISR (Interrupt Service Routine).",
        "Hard":   "How would you implement a real-time scheduler for a bare-metal embedded system?",
    },
    "Performance & Profiling": {
        "Easy":   "What is CPU cache locality and why does it matter for performance?",
        "Medium": "Describe how you would use perf or gprof to identify a hot path in a C++ application.",
        "Hard":   "Explain false sharing in multi-threaded applications and how to eliminate it.",
    },
    # ── DevOps Engineer ───────────────────────────────────────────────────────
    "CI/CD Pipelines": {
        "Easy":   "What is the difference between continuous integration and continuous delivery?",
        "Medium": "Design a CI/CD pipeline for a microservice that includes testing, building, and deploying.",
        "Hard":   "How would you implement blue-green deployments with automated rollback in Kubernetes?",
    },
    "Containerization (Docker/K8s)": {
        "Easy":   "What is the difference between a Docker image and a Docker container?",
        "Medium": "Explain how Kubernetes Deployments, Services, and Ingress work together.",
        "Hard":   "How would you design a Kubernetes cluster for a multi-tenant SaaS with hard resource isolation?",
    },
    "Cloud Platforms": {
        "Easy":   "What is the difference between IaaS, PaaS, and SaaS?",
        "Medium": "Compare AWS Lambda and ECS Fargate — when would you use each?",
        "Hard":   "Design a multi-region, highly available architecture on AWS for a globally distributed application.",
    },
    "Infrastructure as Code": {
        "Easy":   "What is Terraform and what problem does it solve?",
        "Medium": "Explain Terraform state management and the risks of state file corruption.",
        "Hard":   "How would you manage secrets and sensitive variables in a large Terraform codebase?",
    },
    "Networking & Security": {
        "Easy":   "What is a VPC and why do you use one in cloud environments?",
        "Medium": "Explain the principle of least privilege and how you enforce it with IAM policies.",
        "Hard":   "Design a zero-trust network architecture for a cloud-native application.",
    },
    "Monitoring & Observability": {
        "Easy":   "What is the difference between monitoring and observability?",
        "Medium": "Explain the three pillars of observability: logs, metrics, and traces.",
        "Hard":   "How would you set up alerting and SLO tracking for a service with a 99.9% availability target?",
    },
    "Scripting & Automation": {
        "Easy":   "What is the difference between a shell script and a Python script for automation?",
        "Medium": "Write a bash script that checks disk usage and sends an alert if it exceeds 80%.",
        "Hard":   "How would you automate the provisioning of 50 identical cloud servers with idempotent scripts?",
    },
}


class Interviewer:
    """Generates questions, follow-ups, and session summaries using Groq."""

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    # ──────────────────────────────────────────────────────────────────────────
    # QUESTION GENERATION
    # ──────────────────────────────────────────────────────────────────────────

    def generate_question(
        self,
        topic: str,
        difficulty: str,
        role: str,
        previous_questions: list[str],
    ) -> str:
        """Generate a fresh interview question, avoiding previous ones."""
        prev_str = (
            "\n".join(f"- {q}" for q in previous_questions[-5:])
            if previous_questions
            else "None yet."
        )

        prompt = QUESTION_GENERATION_PROMPT.format(
            difficulty=difficulty,
            topic=topic,
            role=role,
            previous_questions=prev_str,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=400,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()

        except Exception as exc:
            logger.error("Error generating question: %s", exc)
            return _FALLBACK_QUESTIONS.get(topic, {}).get(
                difficulty, f"Explain a key concept in {topic}."
            )

    def generate_mcq(
        self,
        topic: str,
        difficulty: str,
        role: str,
        previous_questions: list[str],
    ) -> dict:
        """Generate a multiple-choice question and return structured data."""
        prev_str = (
            "\n".join(f"- {q}" for q in previous_questions[-5:])
            if previous_questions else "None yet."
        )
        prompt = MCQ_GENERATION_PROMPT.format(
            difficulty=difficulty, topic=topic,
            role=role, previous_questions=prev_str,
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model, max_tokens=600,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse_mcq(response.choices[0].message.content.strip(), topic, difficulty)
        except Exception as exc:
            logger.error("Error generating MCQ: %s", exc)
            return self._fallback_mcq(topic, difficulty)

    def _parse_mcq(self, text: str, topic: str, difficulty: str) -> dict:
        """Extract and validate MCQ JSON from the model response."""
        for candidate in [text,
                          re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL) and
                          re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL).group(1),
                          re.search(r"\{[\s\S]*\}", text) and
                          re.search(r"\{[\s\S]*\}", text).group()]:
            if not candidate:
                continue
            try:
                data = json.loads(candidate)
                if all(k in data for k in ("question", "options", "correct", "explanation")):
                    if data["correct"] in data["options"] and len(data["options"]) == 4:
                        return data
            except (json.JSONDecodeError, TypeError):
                continue
        return self._fallback_mcq(topic, difficulty)

    @staticmethod
    def _fallback_mcq(topic: str, difficulty: str) -> dict:
        """Return a hardcoded MCQ when the API fails."""
        fallbacks = {
            "Data Structures": {
                "question": "What is the average time complexity of inserting into a hash map?",
                "options": {"A": "O(1)", "B": "O(log n)", "C": "O(n)", "D": "O(n²)"},
                "correct": "A",
                "explanation": "Hash maps use a hash function to compute an index directly, giving O(1) average insertion. O(n) occurs only in worst-case collision scenarios.",
            },
            "Algorithms": {
                "question": "Which algorithm is best suited for finding the shortest path in a weighted graph?",
                "options": {"A": "BFS", "B": "DFS", "C": "Dijkstra's", "D": "Merge Sort"},
                "correct": "C",
                "explanation": "Dijkstra's algorithm is designed for shortest paths in weighted graphs. BFS works for unweighted graphs only.",
            },
        }
        default = {
            "question": f"Which of the following best describes a key concept in {topic}?",
            "options": {"A": "Option A", "B": "Option B", "C": "Option C", "D": "Option D"},
            "correct": "A",
            "explanation": f"This is a fallback question for {topic}. Please check your API connection.",
        }
        return fallbacks.get(topic, default)

    def generate_follow_up(
        self,
        previous_question: str,
        previous_answer: str,
        missing_concepts: list[str],
        topic: str,
        difficulty: str,
    ) -> str:
        """Generate a contextual follow-up question based on the candidate's answer."""
        missing_str = (
            ", ".join(missing_concepts[:3]) if missing_concepts else "none identified"
        )

        prompt = FOLLOW_UP_PROMPT.format(
            topic=topic,
            difficulty=difficulty,
            previous_question=previous_question,
            previous_answer=previous_answer[:500],
            missing_concepts=missing_str,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()

        except Exception as exc:
            logger.error("Error generating follow-up: %s", exc)
            return self.generate_question(topic, difficulty, "Software Engineer", [previous_question])

    # ──────────────────────────────────────────────────────────────────────────
    # SESSION SUMMARY
    # ──────────────────────────────────────────────────────────────────────────

    def generate_session_summary(
        self,
        role: str,
        topic: str,
        qa_history: list[dict],
    ) -> str:
        """Generate a full debrief for the completed session."""
        if not qa_history:
            return "No questions were answered in this session."

        scores = [qa["score"] for qa in qa_history]
        avg_score = sum(scores) / len(scores)

        # Score trend label
        if len(scores) > 1:
            trend = (
                "Improving ↗" if scores[-1] > scores[0]
                else "Declining ↘" if scores[-1] < scores[0]
                else "Stable →"
            )
        else:
            trend = "N/A (single question)"

        # Compact Q&A history for the prompt
        qa_formatted = "\n\n".join(
            f"Q{i + 1} [Score: {qa['score']}/10]: {qa['question']}\n"
            f"Answer: {qa['answer'][:200]}{'…' if len(qa['answer']) > 200 else ''}"
            for i, qa in enumerate(qa_history)
        )

        prompt = SESSION_SUMMARY_PROMPT.format(
            role=role,
            topic=topic,
            questions_count=len(qa_history),
            avg_score=round(avg_score, 1),
            score_trend=trend,
            qa_history=qa_formatted,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=1500,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content

        except Exception as exc:
            logger.error("Error generating summary: %s", exc)
            perf = "Strong" if avg_score >= 7 else "Average" if avg_score >= 5 else "Needs Improvement"
            return (
                f"## Session Summary\n\n"
                f"**Role:** {role} | **Topic:** {topic}\n"
                f"**Questions:** {len(qa_history)} | **Avg Score:** {avg_score:.1f}/10\n"
                f"**Performance:** {perf}\n\n"
                f"Keep practising to sharpen your skills!"
            )

    # ──────────────────────────────────────────────────────────────────────────
    # WELCOME MESSAGE
    # ──────────────────────────────────────────────────────────────────────────

    def create_welcome_message(
        self, role: str, topic: str, difficulty: str, mode: str
    ) -> str:
        """Build a personalised welcome message for the session opener."""
        if mode == "Mock Interview":
            mins = MOCK_TIME_LIMITS[difficulty] // 60
            mode_instructions = MOCK_MODE_INSTRUCTIONS.format(time_limit=mins)
        else:
            mode_instructions = PRACTICE_MODE_INSTRUCTIONS

        return WELCOME_MESSAGE.format(
            topic=topic,
            role=role,
            difficulty=difficulty,
            mode=mode,
            mode_instructions=mode_instructions,
        )

"""
evaluator.py — Answer evaluation and hint generation via Groq.
"""

import json
import re
import logging

from groq import Groq
from prompts import EVALUATION_PROMPT, HINT_PROMPT

logger = logging.getLogger(__name__)


class Evaluator:
    """Evaluates candidate answers and generates hints using Groq."""

    def __init__(self, api_key: str):
        self.client = Groq(api_key=api_key)
        self.model = "llama-3.3-70b-versatile"

    # ──────────────────────────────────────────────────────────────────────────
    # PUBLIC API
    # ──────────────────────────────────────────────────────────────────────────

    def evaluate_answer(
        self,
        question: str,
        answer: str,
        topic: str,
        difficulty: str,
        role: str,
    ) -> dict:
        """
        Send the question + answer to Claude and return a structured evaluation.

        Returns a dict with keys:
            score, brief_verdict, strengths, missing_concepts,
            detailed_feedback, ideal_answer, should_follow_up, follow_up_question
        """
        if not answer or not answer.strip():
            return self._empty_answer_response()

        prompt = EVALUATION_PROMPT.format(
            role=role,
            topic=topic,
            difficulty=difficulty,
            question=question,
            answer=answer.strip(),
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=2000,
                messages=[{"role": "user", "content": prompt}],
            )
            return self._parse_evaluation(response.choices[0].message.content.strip())

        except Exception as exc:
            logger.error("Groq API error during evaluation: %s", exc)
            return self._error_response()

    def get_hint(self, question: str, topic: str, difficulty: str) -> str:
        """Return a helpful hint for the current question."""
        prompt = HINT_PROMPT.format(
            topic=topic,
            difficulty=difficulty,
            question=question,
        )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                max_tokens=300,
                messages=[{"role": "user", "content": prompt}],
            )
            return response.choices[0].message.content.strip()

        except Exception as exc:
            logger.error("Error generating hint: %s", exc)
            return (
                "Think about the fundamental concepts related to this topic. "
                "What are the key components or steps involved?"
            )

    # ──────────────────────────────────────────────────────────────────────────
    # PRIVATE HELPERS
    # ──────────────────────────────────────────────────────────────────────────

    def _parse_evaluation(self, text: str) -> dict:
        """Try several strategies to extract a valid JSON evaluation from `text`."""

        # 1. Direct parse
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # 2. Markdown code-block (```json … ```)
        match = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass

        # 3. Any {...} block in the text
        match = re.search(r"\{[\s\S]*\}", text)
        if match:
            try:
                return json.loads(match.group())
            except json.JSONDecodeError:
                pass

        # 4. Fallback — surface the raw text so the user sees something useful
        return {
            "score": 5,
            "brief_verdict": "Answer reviewed (could not parse structured response).",
            "strengths": ["Attempted the question"],
            "missing_concepts": [],
            "detailed_feedback": text[:600] if text else "No feedback available.",
            "ideal_answer": "Please consult study materials for a comprehensive answer.",
            "should_follow_up": False,
            "follow_up_question": None,
        }

    @staticmethod
    def _empty_answer_response() -> dict:
        return {
            "score": 0,
            "brief_verdict": "No answer provided.",
            "strengths": [],
            "missing_concepts": ["A complete answer is required."],
            "detailed_feedback": "Please provide a meaningful answer to receive feedback.",
            "ideal_answer": None,
            "should_follow_up": False,
            "follow_up_question": None,
        }

    @staticmethod
    def _error_response() -> dict:
        return {
            "score": 0,
            "brief_verdict": "Evaluation temporarily unavailable.",
            "strengths": [],
            "missing_concepts": [],
            "detailed_feedback": "Could not evaluate at this time — please try again.",
            "ideal_answer": None,
            "should_follow_up": False,
            "follow_up_question": None,
        }

from roadman_mind.core.plugins import Plugin
from typing import Dict, Callable, List, Any

class LearningLabPlugin(Plugin):
    """
    A plugin that provides a simple cybersecurity quiz.
    """
    def __init__(self):
        self.quiz_data: List[Dict[str, str]] = [
            {
                "question": "What does 'phishing' refer to in cybersecurity?",
                "answer": "A fraudulent attempt to obtain sensitive information, such as usernames, passwords, and credit card details, by disguising as a trustworthy entity in an electronic communication."
            },
            {
                "question": "What is the primary purpose of a firewall?",
                "answer": "To act as a barrier between a trusted internal network and untrusted external networks (like the Internet), monitoring and controlling incoming and outgoing network traffic based on predetermined security rules."
            },
            {
                "question": "What is a 'Zero-Day' vulnerability?",
                "answer": "A security flaw in a piece of software that is unknown to the vendor. This vulnerability can be exploited by hackers before the vendor becomes aware and releases a patch."
            }
        ]

    @property
    def name(self) -> str:
        return "lab"

    @property
    def version(self) -> str:
        return "1.0.0"

    @property
    def description(self) -> str:
        return "A small, interactive learning lab for cybersecurity concepts."

    def routes(self) -> Dict[str, Callable]:
        """Provides routes to access quiz content."""
        return {
            "quiz_count": self.get_quiz_count,
            "first_q": self.get_first_question,
            "first_a": self.get_first_answer,
        }

    def get_quiz_count(self) -> int:
        """Returns the number of questions in the quiz."""
        return len(self.quiz_data)

    def get_first_question(self) -> str:
        """Returns the first question from the quiz."""
        if not self.quiz_data:
            return "No questions available."
        return self.quiz_data[0]["question"]

    def get_first_answer(self) -> str:
        """Returns the answer to the first question."""
        if not self.quiz_data:
            return "No answer available."
        return self.quiz_data[0]["answer"]

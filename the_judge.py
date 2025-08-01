from __future__ import annotations

import argparse
import asyncio
from dataclasses import dataclass
from typing import Literal

from dotenv import load_dotenv
from agents import Agent, ItemHelpers, Runner, TResponseInputItem, trace

# Load environment variables from .env file
load_dotenv()

"""
Majority of this file came from here: https://github.com/openai/openai-agents-python/blob/main/examples/agent_patterns/llm_as_a_judge.py
This example shows the LLM as a judge pattern. The first agent generates an article.
The second agent judges the article and provides feedback. We loop until the judge is satisfied
with the article.
"""

article_writer = Agent(
    name="article_writer",
    instructions=(
        "You write a comprehensive, engaging, and human-sounding article based on the user's request. "
        "If there is any feedback provided, use it to improve the article. "
        "The article should be in Markdown format."
    ),
)


@dataclass
class EvaluationFeedback:
    feedback: str
    score: Literal["pass", "needs_improvement", "fail"]


evaluator = Agent[None](
    name="evaluator",
    instructions=(
        "You evaluate an article and decide if it's good enough to publish. "
        "If it's not good enough, you provide specific, actionable feedback on what needs to be improved. "
        "Key criteria are: clarity, depth, engagement, and sounding like a human wrote it (not an LLM). "
        "Never give it a pass on the first try. After 3-4 attempts, you can give it a pass if the article is good enough - do not go for perfection."
    ),
    output_type=EvaluationFeedback,
)


def create_sanitized_filename(text: str) -> str:
    """Creates a safe filename from the first few words of the article title."""
    safe_text = "".join(c for c in text if c.isalnum() or c in (" ", "-")).rstrip()
    return "-".join(safe_text.split()[:6]).lower() + ".md"


async def main(article_topic: str) -> None:
    """
    Runs the LLM as a judge workflow to write and evaluate an article.

    Args:
        article_topic: The topic of the article to be written.
    """
    input_items: list[TResponseInputItem] = [{"content": article_topic, "role": "user"}]
    latest_article: str | None = None
    filename = "article.md"  # Default filename

    # We'll run the entire workflow in a single trace
    with trace("LLM as a judge writing an article"):
        for i in range(5):  # Limit to 5 attempts to avoid infinite loops
            print(f"--- Attempt {i+1} ---")
            article_result = await Runner.run(
                article_writer,
                input_items,
            )

            input_items = article_result.to_input_list()
            latest_article = ItemHelpers.text_message_outputs(article_result.new_items)
            print("Article draft generated.")

            if i == 0 and latest_article:
                # Create a filename from the initial draft's title/content
                filename = create_sanitized_filename(latest_article)

            evaluator_result = await Runner.run(evaluator, input_items)
            result: EvaluationFeedback = evaluator_result.final_output

            print(f"Evaluator score: {result.score}")

            if result.score == "pass":
                print("Article is good enough, exiting.")
                break

            print(f"Feedback: {result.feedback}")
            print("Re-running with feedback...")

            input_items.append({"content": f"Feedback: {result.feedback}", "role": "user"})
        else:
            print("Reached maximum attempts. Saving the latest version of the article.")

    if latest_article:
        with open(filename, "w") as f:
            f.write(latest_article)
        print(f"\nFinal article saved to: {filename}")
    else:
        print("Could not generate an article.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate an article using the LLM as a Judge pattern.")
    parser.add_argument(
        "topic",
        type=str,
        help='The topic for the article, e.g., "write me a 1000 word Medium article about how to use the LLM as a judge pattern without sounding like an LLM wrote it"',
    )
    args = parser.parse_args()

    asyncio.run(main(args.topic))

# LLM as a Judge

This project demonstrates the "LLM as a Judge" pattern, where one LLM generates a full article and another evaluates it iteratively.

## Prerequisites

1.  This project uses the OpenAI API. You need to have an API key.
2.  Rename the `.env.example` file to `.env`.
3.  Open the `.env` file and add your OpenAI API key:
    ```
    OPENAI_API_KEY=sk-...
    ```

## Running the project

### Natively

1.  Install the dependencies:
    ```bash
    pip install -r requirements.txt
    ```
2.  Run the script with a topic. The script will automatically load your API key from the `.env` file.
    ```bash
    python the_judge.py "your article topic here"
    ```
    For example:
    ```bash
    python the_judge.py "write a 1000 word Medium article about how to use the LLM as a judge pattern"
    ```

### With Docker

1.  Build the Docker image:
    ```bash
    docker build -t llm_as_a_judge .
    ```
2.  Run the Docker container, passing the `.env` file to it.
    ```bash
    docker run --rm -v $(pwd):/app --env-file .env llm_as_a_judge "your article topic here"
    ```
    For example:
    ```bash
    docker run --rm -v $(pwd):/app --env-file .env llm_as_a_judge "The LLM as a judge pattern. The first agent generates an outline for a story. The second agent judges the outline and provides feedback. We loop until the judge is satisfied
        with the outline. We want to write a Medium article on this subject. It should not sound like it was written by an LLM. The subject of the article is using this pattern to get OpenAI Agents to write an articloe about how they write this article"
    ```
    - The `-v $(pwd):/app` command mounts the current directory, allowing the script to save the final markdown file to your host machine.
    - The `--env-file .env` flag securely passes your API key to the container.

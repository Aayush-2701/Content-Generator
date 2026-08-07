# Content Generator

What this is
------------
Content Generator is a Streamlit-based LinkedIn post generator that uses few-shot examples and a Groq-hosted LLM to produce short-to-long LinkedIn posts across multiple languages. It is intended for developers, content creators, and product teams who want programmatic, example-driven post generation for social media workflows.

### Stack
- **Language(s):** Python 3.10+ (primary)
- **Framework / runtime:** Streamlit application (UI) with LangChain-style prompt chains
- **Notable libraries:** streamlit, langchain / langchain-core, langchain_groq (Groq LLM integration), pandas

How it's organized
------------------
Top-level layout (annotated):

```
Data/                      # Raw and processed post datasets (raw_posts.json, processed_posts.json)
few_shot.py                # Loads processed examples and provides filtered few-shot examples
post_generator.py          # Builds prompts from user choices and examples; calls LLM via llm_helper
preprocess.py              # Enriches raw posts with metadata (line counts, language, tags) using the LLM
llm_helper.py              # LLM client initialization (Groq Chat model); reads GROQ_API_KEY from env
main.py                    # Streamlit entrypoint (UI): topic, length, language selection and generate button
requirements.txt           # Python dependencies
.gitignore
README.md                  # This file
```

How it fits together
---------------------
At runtime the Streamlit UI (`main.py`) accepts three user inputs (Topic/Tag, Length, Language). It uses `few_shot.py` to select example posts from the processed dataset, then `post_generator.py` assembles a prompt containing the selected parameters and up to two examples, and sends that prompt to the LLM client exposed by `llm_helper.py`. If you need to prepare or refresh the example set, `preprocess.py` ingests raw posts and produces the dataset used by `few_shot.py`.

Architecture and workflow
-------------------------
High-level flow:
1. Data preparation: `Data/raw_posts.json` -> (preprocess.py using the LLM) -> `Data/processed_posts.json`
2. Few-shot selection: `few_shot.py` loads processed posts and exposes tag list and filtered examples
3. Prompt construction: `post_generator.py` forms the generation prompt (parameters + examples)
4. LLM invocation: `llm_helper.py` (ChatGroq client) sends prompt and receives content
5. UI: `main.py` presents the result in Streamlit

A
Textual workflow (fallback)
- Raw data -> preprocess (extract line_count, language, canonical tags) -> processed dataset
- Streamlit pulls tag list from processed dataset -> user selects Topic/Language/Length -> generator fetches up to 2 examples -> LLM invoked -> generated post returned and shown in UI

How to run it
--------------
Prerequisites:
- Python 3.10+
- A Groq API key (set as environment variable `GROQ_API_KEY` or in a `.env` file)

Install and run:

```bash
# create virtual environment (optional but recommended)
python -m venv venv
source venv/bin/activate          # on Windows: venv\Scripts\activate

# install dependencies
pip install -r requirements.txt

# set environment variable (example)
export GROQ_API_KEY="your_groq_api_key_here"
# or create a .env file with:
# GROQ_API_KEY=your_groq_api_key_here

# (Optional) preprocess raw posts to regenerate processed dataset
python preprocess.py

# Run the Streamlit app
streamlit run main.py
```

Important environment / files
- GROQ_API_KEY — required to instantiate the ChatGroq client in `llm_helper.py`.
- `Data/raw_posts.json` — raw input posts for preprocessing.
- `Data/processed_posts.json` — processed posts used by `few_shot.py`. Note: the code references `data/processed_posts.json` (lowercase `data`) in a few locations; ensure path casing matches your environment (see Known issues).

Files and responsibilities (explicit)
- few_shot.py: class `FewShotPosts` — loads processed JSON, normalizes into DataFrame, categorizes lengths, exposes `get_tags()` and `get_filtered_posts(length, language, tag)`.
- post_generator.py:
  - `get_length_str(length)` — maps friendly label to "1 to 5 lines" etc.
  - `get_prompt(length, language, tag)` — builds prompt including up to two examples.
  - `generate_post(length, language, tag)` — invokes `llm.invoke(prompt)` and returns `response.content`.
- preprocess.py:
  - `process_posts(raw_file_path, processed_file_path)` — iterates raw posts, enriches metadata via `extract_metadata()` that uses the LLM and LangChain prompt wrappers to produce JSON with `line_count`, `language`, `tags`.
  - `get_unified_tags(posts_with_metadata)` — generates unified title-case tag mapping using the LLM.
- llm_helper.py: initializes `ChatGroq(model="llama-3.3-70b-versatile", api_key=os.getenv("GROQ_API_KEY"))`.
- main.py: Streamlit UI; pulls tags from `FewShotPosts()` and displays generator results.

Notes and known issues / recommendations
---------------------------------------
- Path casing: `few_shot.py` refers to `"data/processed_posts.json"` while the repository stores `Data/processed_posts.json`. This will cause failures on case-sensitive file systems (Linux/macOS depending on config). Recommendation: normalize the path to the actual directory name or make file lookup resilient.
- LLM vendor abstraction: `llm_helper.py` tightly couples the app to Groq. If you want a different provider (OpenAI, Anthropic), create an adapter module that implements the same `invoke` interface.
- Rate limits & cost: production use should include rate limiting, caching of prompts/responses, and monitoring for token usage.
- Prompt safety: the current prompts do not sanitize user-provided tags — consider escaping or validation.

Extending the project
---------------------
- Add response caching (file or Redis) keyed by the prompt fingerprint.
- Add prompt templates stored in a templates directory for easier iteration and testing.
- Introduce unit tests for prompt construction and data preprocessing (mock the LLM).
- Add CI that lints, runs tests, and validates that Data/processed_posts.json is present.

Contributing
------------
Contributions are welcome. Please open issues or PRs for bug fixes or enhancements. Follow standard commit message and PR practices.

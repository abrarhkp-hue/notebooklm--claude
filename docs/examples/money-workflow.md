# Money Workflow Integration

This example shows how to use `notebooklm-py` as the research and knowledge layer inside a business-automation skill suite (e.g. the [money skills](https://github.com/abrarhkp-hue/desktop-tutorial)).

## Overview

The money skill suite covers the full lifecycle of an online business: idea discovery, strategy, content, outreach, SEO, ads, ops, finance, and more. NotebookLM slots in as the **knowledge and research engine**—turning raw URLs, PDFs, and documents into structured insights, podcasts, quizzes, and reports that each sub-skill can consume.

```
money (router)
  ├── money-discover   ← NotebookLM: web research → briefing doc
  ├── money-strategy   ← NotebookLM: competitor analysis → mind map
  ├── money-diagnose   ← NotebookLM: doc analysis → diagnosis notes
  ├── money-content    ← NotebookLM: source material → audio / slides
  ├── money-ops        ← NotebookLM: runbooks → quiz / study guide
  └── money-finance    ← NotebookLM: financial PDFs → structured Q&A
```

## Setup

```bash
pip install "notebooklm-py[browser]"
playwright install chromium
notebooklm login          # one-time browser OAuth
notebooklm status         # verify: shows authenticated email
```

For CI or headless environments, export the stored auth as an env var:

```bash
export NOTEBOOKLM_AUTH_JSON=$(cat ~/.notebooklm/storage_state.json)
```

## Pattern 1 — Research Briefing (money-discover / money-strategy)

```python
import asyncio
from notebooklm import NotebookLMClient

async def research_briefing(topic: str, urls: list[str]) -> str:
    async with await NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create(f"Research: {topic}")

        # Add sources and wait for indexing
        source_ids = []
        for url in urls:
            src = await client.sources.add_url(nb.id, url)
            source_ids.append(src.id)
        for sid in source_ids:
            await client.sources.wait_for_ready(nb.id, sid, timeout=120)

        # Generate a briefing doc and download it
        status = await client.artifacts.generate_report(
            nb.id, report_format="briefing-doc"
        )
        await client.artifacts.wait_for_completion(nb.id, status.task_id)
        path = await client.artifacts.download_report(nb.id, "briefing.md")
        return path

asyncio.run(research_briefing(
    "AI SaaS market 2026",
    ["https://example.com/ai-saas", "https://example.com/competitors"]
))
```

## Pattern 2 — Content Generation (money-content)

```python
async def content_pipeline(notebook_id: str, angle: str) -> dict:
    async with await NotebookLMClient.from_storage() as client:
        # Chat to surface key hooks
        hooks = await client.chat.ask(
            notebook_id,
            f"Give me 3 compelling angles for content about: {angle}"
        )

        # Generate podcast audio
        audio_task = await client.artifacts.generate_audio(
            notebook_id, instructions=f"Engaging deep-dive on: {angle}"
        )
        await client.artifacts.wait_for_completion(notebook_id, audio_task.task_id)
        audio_path = await client.artifacts.download_audio(notebook_id, "podcast.mp3")

        # Generate slide deck
        slide_task = await client.artifacts.generate_slide_deck(
            notebook_id, slide_format="detailed"
        )
        await client.artifacts.wait_for_completion(notebook_id, slide_task.task_id)
        slides_path = await client.artifacts.download_slide_deck(
            notebook_id, "slides.pdf"
        )

        return {
            "hooks": hooks.answer,
            "audio": audio_path,
            "slides": slides_path,
        }
```

## Pattern 3 — Team Training (money-ops)

```python
async def generate_training_materials(runbook_path: str, topic: str) -> None:
    async with await NotebookLMClient.from_storage() as client:
        nb = await client.notebooks.create(f"Training: {topic}")

        # Add local runbook document
        src = await client.sources.add_file(nb.id, runbook_path)
        await client.sources.wait_for_ready(nb.id, src.id)

        # Quiz
        quiz_task = await client.artifacts.generate_quiz(
            nb.id, difficulty="medium", quantity="more"
        )
        await client.artifacts.wait_for_completion(nb.id, quiz_task.task_id)
        await client.artifacts.download_quiz(
            nb.id, "team-quiz.md", output_format="markdown"
        )

        # Flashcards
        fc_task = await client.artifacts.generate_flashcards(
            nb.id, quantity="more"
        )
        await client.artifacts.wait_for_completion(nb.id, fc_task.task_id)
        await client.artifacts.download_flashcards(
            nb.id, "flashcards.json", output_format="json"
        )

        # Study guide
        guide_task = await client.artifacts.generate_report(
            nb.id, report_format="study-guide"
        )
        await client.artifacts.wait_for_completion(nb.id, guide_task.task_id)
        await client.artifacts.download_report(nb.id, "study-guide.md")
```

## CLI Equivalents

Each Python pattern above has a direct CLI equivalent for shell scripts or agent automation:

```bash
# Research briefing
NB=$(notebooklm create "Research: AI SaaS" --json | python -c "import sys,json; print(json.load(sys.stdin)['id'])")
notebooklm use $NB
notebooklm source add-research "AI SaaS market 2026" --import-all
notebooklm generate report --format briefing-doc
notebooklm download report ./briefing.md

# Content pipeline
notebooklm generate audio "engaging deep-dive" --wait
notebooklm download audio ./podcast.mp3
notebooklm generate slide-deck --format detailed
notebooklm download slide-deck ./slides.pdf

# Team training
notebooklm source add ./runbook.md
notebooklm generate quiz --difficulty medium --quantity more
notebooklm download quiz --format markdown ./team-quiz.md
notebooklm generate flashcards --quantity more
notebooklm download flashcards --format json ./flashcards.json
```

## Parallel Agent Safety

When multiple money sub-skills run concurrently, isolate each agent's NotebookLM context:

```bash
# Each agent gets its own home directory
export NOTEBOOKLM_HOME=/tmp/notebooklm-$(uname -n)-$$
```

Or pass notebook IDs explicitly instead of relying on `notebooklm use`:

```bash
notebooklm generate audio --notebook $NB_ID
notebooklm download audio ./out.mp3 -n $NB_ID
```

## See Also

- [CLI Reference](../cli-reference.md)
- [Python API Reference](../python-api.md)
- [NotebookLM Skill for Agents](../../SKILL.md)

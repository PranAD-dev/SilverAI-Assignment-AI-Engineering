"""Handbook generation using the AgentWrite pipeline (plan → write).

Adapted from LongWriter-main/agentwrite/ to use Grok 4.1 and RAG context.
"""

from app.llm_client import chat

# ---------------------------------------------------------------------------
# Prompt templates (adapted from LongWriter prompts/)
# ---------------------------------------------------------------------------

PLAN_PROMPT = """\
I need you to create a detailed outline for a comprehensive, professional handbook. The handbook MUST be at least 20,000 words. Each subtask will guide the writing of one section.

The writing instruction is as follows:

{instruction}

Here is context retrieved from the uploaded documents to inform your plan:

{context}

REQUIREMENTS:
- Create at least 30 subtasks (sections)
- Each section should target 600-800 words
- Include: Table of Contents, Executive Summary, Introduction, multiple detailed chapters, case studies, practical examples, best practices, future directions, conclusion, glossary, and references
- Be highly specific in each subtask description — give detailed content guidance

Format each subtask on its own line exactly like this:

Paragraph 1 - Main Point: [Detailed description of what to write] - Word Count: [target, e.g., 700 words]

Paragraph 2 - Main Point: [Detailed description of what to write] - Word Count: [target, e.g., 700 words]

...

Do not output any other content besides the subtask lines.\
"""

WRITE_PROMPT = """\
You are an expert technical writer creating a comprehensive handbook. Write the assigned section with depth, detail, and substance. Use specific examples, data points, and thorough explanations.

Writing instruction:

{instruction}

Full writing plan:

{plan}

Already written text (last 3000 words shown for context):

{text}

YOUR TASK: Write {step}

IMPORTANT RULES:
- You MUST write AT LEAST the word count specified in the step above
- Include detailed explanations, examples, and analysis
- Use proper markdown formatting with headers (##, ###), bullet points, and emphasis where appropriate
- Only output the new section — do NOT repeat already written text
- Do NOT write a conclusion or wrap up the document — more sections will follow\
"""


def generate_plan(instruction: str, context: str) -> list[str]:
    """Phase 1: Break instruction into paragraph-level subtasks."""
    prompt = PLAN_PROMPT.format(instruction=instruction, context=context)
    response = chat(prompt, max_tokens=4096, temperature=0.7)
    steps = [line.strip() for line in response.strip().split("\n") if line.strip()]
    return steps


def _get_recent_text(full_text: str, max_words: int = 3000) -> str:
    """Get the last N words of the text to stay within reasonable prompt size."""
    words = full_text.split()
    if len(words) <= max_words:
        return full_text
    return "... " + " ".join(words[-max_words:])


def generate_handbook(instruction: str, context: str):
    """Full AgentWrite pipeline: plan then write each paragraph sequentially.

    Yields (step_num, total_steps, accumulated_text) tuples for progress updates.
    """
    # Phase 1: Planning
    steps = generate_plan(instruction, context)
    plan_text = "\n".join(steps)
    total = len(steps)

    yield 0, total, f"**Plan created with {total} sections.** Starting generation...\n\n"

    # Phase 2: Writing (iterative, one paragraph at a time)
    full_text = ""
    for i, step in enumerate(steps):
        recent_text = _get_recent_text(full_text) if full_text else "(Beginning of document)"
        prompt = WRITE_PROMPT.format(
            instruction=instruction,
            plan=plan_text,
            text=recent_text,
            step=step,
        )
        paragraph = chat(prompt, max_tokens=4096, temperature=0.7)
        full_text += paragraph + "\n\n"

        yield i + 1, total, full_text

    return full_text.strip()

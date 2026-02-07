"""Handbook generation using the AgentWrite pipeline (plan → write).

Adapted from LongWriter-main/agentwrite/ to use Grok 4.1 and RAG context.
"""

from app.llm_client import chat

# ---------------------------------------------------------------------------
# Prompt templates (adapted from LongWriter prompts/)
# ---------------------------------------------------------------------------

PLAN_PROMPT = """\
I need you to help me break down the following long-form writing instruction into multiple subtasks. Each subtask will guide the writing of one section in the handbook, and should include the main points and word count requirements for that section.

The writing instruction is as follows:

{instruction}

Here is context retrieved from the uploaded documents to inform your plan:

{context}

Please break it down in the following format, with each subtask taking up one line:

Paragraph 1 - Main Point: [Describe the main point of the paragraph, in detail] - Word Count: [Word count requirement, e.g., 400 words]

Paragraph 2 - Main Point: [Describe the main point of the paragraph, in detail] - Word Count: [word count requirement, e.g. 1000 words].

...

Make sure that each subtask is clear and specific, and that all subtasks cover the entire content of the writing instruction. Each subtask's paragraph should be no less than 200 words and no more than 1000 words. Aim for at least 25-30 subtasks to reach the 20,000-word target. Include a table of contents section at the beginning. Do not output any other content.\
"""

WRITE_PROMPT = """\
You are an excellent writing assistant. I will give you an original writing instruction and my planned writing steps. I will also provide you with the text I have already written. Please help me continue writing the next paragraph based on the writing instruction, writing steps, and the already written text.

Writing instruction:

{instruction}

Writing steps:

{plan}

Already written text (last 3000 words shown for context):

{text}

Please integrate the original writing instruction, writing steps, and the already written text, and now continue writing {step}. If needed, you can add a small subtitle at the beginning. Remember to only output the paragraph you write, without repeating the already written text. As this is an ongoing work, omit open-ended conclusions or other rhetorical hooks.\
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

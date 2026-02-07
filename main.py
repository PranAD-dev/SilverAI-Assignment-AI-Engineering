"""Entry point for the Handbook Generator application."""

import asyncio
import gradio as gr
from pathlib import Path

from app import config
from app.pdf_processor import extract_text
from app import rag_engine
from app.llm_client import chat
from app.handbook_generator import generate_handbook


def main():
    # Validate environment
    missing = config.validate()
    if missing:
        print(f"Missing required environment variables: {', '.join(missing)}")
        print("Copy .env.example to .env and fill in your API keys.")
        return

    # ------------------------------------------------------------------ #
    #  Event handlers                                                      #
    # ------------------------------------------------------------------ #

    async def handle_upload(files, progress=gr.Progress()):
        if not files:
            return "No files selected."
        status_parts = []
        for i, f in enumerate(files):
            progress((i, len(files)), desc=f"Indexing {Path(f.name).name}...")
            text = extract_text(f.name)
            word_count = len(text.split())
            await rag_engine.insert_document(text)
            status_parts.append(f"{Path(f.name).name}: {word_count:,} words indexed")
        return "\n".join(status_parts)

    async def handle_chat(message, history):
        if not message or not message.strip():
            yield history, ""
            return

        history = history + [{"role": "user", "content": message}]

        # Detect handbook generation request
        lower = message.lower()
        is_handbook = any(
            kw in lower
            for kw in [
                "generate a handbook",
                "create a handbook",
                "write a handbook",
                "generate handbook",
                "create handbook",
                "write handbook",
            ]
        )

        if is_handbook:
            # Retrieve broad context for handbook generation
            try:
                context = await rag_engine.query(message, mode="hybrid")
            except Exception:
                context = ""

            # Stream handbook generation progress
            history = history + [{"role": "assistant", "content": "Planning handbook structure..."}]
            yield history, ""

            word_count = 0
            for step_num, total_steps, accumulated_text in generate_handbook(
                instruction=message, context=context
            ):
                word_count = len(accumulated_text.split())
                progress_header = (
                    f"**Generating handbook: section {step_num}/{total_steps} "
                    f"| {word_count:,} words so far**\n\n---\n\n"
                )
                history[-1] = {
                    "role": "assistant",
                    "content": progress_header + accumulated_text,
                }
                yield history, ""

            # Final update with completion message
            final_header = f"**Handbook complete: {word_count:,} words | {total_steps} sections**\n\n---\n\n"
            history[-1] = {
                "role": "assistant",
                "content": final_header + accumulated_text,
            }
            yield history, ""

        else:
            # Regular RAG chat
            try:
                context = await rag_engine.query(message, mode="hybrid")
            except Exception:
                context = "(No documents indexed yet. Upload PDFs first.)"

            prompt = (
                f"Context from uploaded documents:\n{context}\n\n"
                f"User question: {message}"
            )
            response = chat(
                prompt,
                system="You are a helpful assistant. Answer based on the provided document context. If the context is insufficient, say so.",
            )
            history = history + [{"role": "assistant", "content": response}]
            yield history, ""

    # ------------------------------------------------------------------ #
    #  Build UI                                                            #
    # ------------------------------------------------------------------ #

    with gr.Blocks(title="Handbook Generator") as app:
        gr.Markdown(
            "# Handbook Generator\n"
            "Upload PDFs, chat about them, or generate a 20,000-word handbook.\n\n"
            '*To generate a handbook, type something like: "Create a handbook on Retrieval-Augmented Generation"*'
        )

        with gr.Row():
            with gr.Column(scale=1):
                pdf_upload = gr.File(
                    label="Upload PDFs",
                    file_types=[".pdf"],
                    file_count="multiple",
                )
                upload_btn = gr.Button("Index PDFs", variant="primary")
                upload_status = gr.Textbox(label="Status", interactive=False, lines=4)

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="Chat", height=550)
                with gr.Row():
                    msg = gr.Textbox(
                        label="Message",
                        placeholder="Ask about your PDFs or request a handbook...",
                        scale=4,
                    )
                    send_btn = gr.Button("Send", variant="primary", scale=1)

        # Wire events
        upload_btn.click(handle_upload, inputs=[pdf_upload], outputs=[upload_status])
        send_btn.click(handle_chat, inputs=[msg, chatbot], outputs=[chatbot, msg])
        msg.submit(handle_chat, inputs=[msg, chatbot], outputs=[chatbot, msg])

    app.launch(theme=gr.themes.Soft())


if __name__ == "__main__":
    main()

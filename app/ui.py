"""Gradio chat interface."""

import gradio as gr


def build_ui() -> gr.Blocks:
    """Build and return the Gradio app (not launched yet)."""
    with gr.Blocks(title="Handbook Generator", theme=gr.themes.Soft()) as app:
        gr.Markdown("# Handbook Generator\nUpload PDFs, chat about them, or generate a 20,000-word handbook.")

        with gr.Row():
            with gr.Column(scale=1):
                pdf_upload = gr.File(
                    label="Upload PDFs",
                    file_types=[".pdf"],
                    file_count="multiple",
                )
                upload_btn = gr.Button("Index PDFs", variant="primary")
                upload_status = gr.Textbox(label="Status", interactive=False)

            with gr.Column(scale=3):
                chatbot = gr.Chatbot(label="Chat", height=500, type="messages")
                msg = gr.Textbox(
                    label="Message",
                    placeholder="Ask about your PDFs or say: 'Generate a handbook on ...'",
                )
                send_btn = gr.Button("Send", variant="primary")

        # --- Event handlers (wired up in main.py) ---
        # Exposed as attributes so main.py can attach callbacks
        app.pdf_upload = pdf_upload
        app.upload_btn = upload_btn
        app.upload_status = upload_status
        app.chatbot = chatbot
        app.msg = msg
        app.send_btn = send_btn

    return app
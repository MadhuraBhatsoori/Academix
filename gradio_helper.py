from typing import Callable, Literal
import gradio as gr

def clear_files():
    return "Vector Store is Not ready"

def handle_user_message(message, history):
    """
    callback function for updating user messages in interface on submit button click

    Params:
      message: current message
      history: conversation history
    Returns:
      None
    """
    # Append the user's message to the conversation history
    return "", history + [[message, ""]]

def make_demo(
    load_doc_fn: Callable,
    run_fn: Callable,
    update_retriever_fn: Callable,
    model_name: str,
    language: Literal["English", "Chinese"] = "English",
):
    # Create a custom maroon theme
    theme = gr.themes.Base(
        primary_hue=gr.themes.Color(
            c50="#FFF5F5",
            c100="#FFE3E3",
            c200="#FFC9C9",
            c300="#FFA8A8",
            c400="#FF8787",
            c500="#800000",  # Main maroon color
            c600="#6B0000",
            c700="#560000",
            c800="#410000",
            c900="#2C0000",
            c950="#1A0000",  # Added the missing c950 value
        ),
        font=["Source Sans Pro", "ui-sans-serif", "system-ui", "sans-serif"],
    )

    with gr.Blocks(
        theme=theme,
        css="""
            .disclaimer {font-variant-caps: all-small-caps;}
            .gradio-container {background-color: #FFF5F5}
            .gr-button {color: white}
            .gr-button-primary {background-color: #800000 !important}
            .gr-button-primary:hover {background-color: #6B0000 !important}
            .gr-box {border-color: #800000}
        """
    ) as demo:
        gr.Markdown("""<h1 style="color: #800000; text-align: center">Academix</h1>""")
    
        with gr.Row():
            with gr.Column(scale=1):
                docs = gr.File(
                    label="Upload files",
                    file_count="multiple",
                    file_types=[
                        ".csv",
                        ".doc",
                        ".docx",
                        ".enex",
                        ".epub",
                        ".html",
                        ".md",
                        ".odt",
                        ".pdf",
                        ".ppt",
                        ".pptx",
                        ".txt",
                    ],
                )
                load_docs = gr.Button("Build Vector Store", variant="primary")
                db_argument = gr.Accordion("Vector Store Configuration", open=False)
                with db_argument:
                    spliter = gr.Dropdown(
                        ["Character", "RecursiveCharacter"],
                        value="RecursiveCharacter",
                        label="Text Spliter",
                        info="Method used to splite the documents",
                        multiselect=False,
                    )

                    chunk_size = gr.Slider(
                        label="Chunk size",
                        value=400,
                        minimum=50,
                        maximum=2000,
                        step=50,
                        interactive=True,
                        info="Size of sentence chunk",
                    )

                    chunk_overlap = gr.Slider(
                        label="Chunk overlap",
                        value=50,
                        minimum=0,
                        maximum=400,
                        step=10,
                        interactive=True,
                        info=("Overlap between 2 chunks"),
                    )

                langchain_status = gr.Textbox(
                    label="Vector Store Status",
                    value="Vector Store is Ready",
                    interactive=False,
                )
                do_rag = gr.Checkbox(
                    value=True,
                    label="RAG is ON",
                    interactive=True,
                    info="Whether to do RAG for generation",
                )
                with gr.Accordion("Generation Configuration", open=False):
                    with gr.Row():
                        with gr.Column():
                            with gr.Row():
                                temperature = gr.Slider(
                                    label="Temperature",
                                    value=0.1,
                                    minimum=0.0,
                                    maximum=1.0,
                                    step=0.1,
                                    interactive=True,
                                )
                        with gr.Column():
                            with gr.Row():
                                top_p = gr.Slider(
                                    label="Top-p (nucleus sampling)",
                                    value=1.0,
                                    minimum=0.0,
                                    maximum=1,
                                    step=0.01,
                                    interactive=True,
                                )
                        with gr.Column():
                            with gr.Row():
                                top_k = gr.Slider(
                                    label="Top-k",
                                    value=50,
                                    minimum=0.0,
                                    maximum=200,
                                    step=1,
                                    interactive=True,
                                )
                        with gr.Column():
                            with gr.Row():
                                repetition_penalty = gr.Slider(
                                    label="Repetition Penalty",
                                    value=1.1,
                                    minimum=1.0,
                                    maximum=2.0,
                                    step=0.1,
                                    interactive=True,
                                )
            with gr.Column(scale=4):
                chatbot = gr.Chatbot(
                    height=600,
                )
                with gr.Row():
                    with gr.Column():
                        with gr.Row():
                            msg = gr.Textbox(
                                label="Academix",
                                placeholder="Enter question here",
                                show_label=False,
                                container=False,
                            )
                    with gr.Column():
                        with gr.Row():
                            submit = gr.Button("Submit", variant="primary")
                retriever_argument = gr.Accordion("Retriever Configuration", open=False)
                with retriever_argument:
                    with gr.Row():
                        with gr.Row():
                            do_rerank = gr.Checkbox(
                                value=True,
                                label="Rerank searching result",
                                interactive=True,
                            )
                            hide_context = gr.Checkbox(
                                value=True,
                                label="Hide searching result in prompt",
                                interactive=True,
                            )
                        with gr.Row():
                            search_method = gr.Dropdown(
                                ["similarity_score_threshold", "similarity", "mmr"],
                                value="similarity_score_threshold",
                                label="Searching Method",
                                info="Method used to search vector store",
                                multiselect=False,
                                interactive=True,
                            )
                        with gr.Row():
                            score_threshold = gr.Slider(
                                0.01,
                                0.99,
                                value=0.5,
                                step=0.01,
                                label="Similarity Threshold",
                                info="Only working for 'similarity score threshold' method",
                                interactive=True,
                            )
                        with gr.Row():
                            vector_rerank_top_n = gr.Slider(
                                1,
                                10,
                                value=2,
                                step=1,
                                label="Rerank top n",
                                info="Number of rerank results",
                                interactive=True,
                            )
                        with gr.Row():
                            vector_search_top_k = gr.Slider(
                                1,
                                50,
                                value=10,
                                step=1,
                                label="Search top k",
                                info="Search top k must >= Rerank top n",
                                interactive=True,
                            )
        docs.clear(clear_files, outputs=[langchain_status], queue=False)
        load_docs.click(
            fn=load_doc_fn,
            inputs=[docs, spliter, chunk_size, chunk_overlap, vector_search_top_k, vector_rerank_top_n, do_rerank],
            outputs=[langchain_status],
            queue=False,
        )
        submit_event = msg.submit(handle_user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
            run_fn,
            [chatbot, temperature, top_p, top_k, repetition_penalty, do_rag],
            chatbot,
            queue=True,
        )
        submit_click_event = submit.click(handle_user_message, [msg, chatbot], [msg, chatbot], queue=False).then(
            run_fn,
            [chatbot, temperature, top_p, top_k, repetition_penalty, do_rag],
            chatbot,
            queue=True,
        )
        vector_rerank_top_n.release(
            update_retriever_fn,
            inputs=[vector_search_top_k, vector_rerank_top_n, do_rerank, search_method, score_threshold],
            outputs=[langchain_status],
        )
        do_rerank.change(
            update_retriever_fn,
            inputs=[vector_search_top_k, vector_rerank_top_n, do_rerank, search_method, score_threshold],
            outputs=[langchain_status],
        )
        search_method.change(
            update_retriever_fn,
            inputs=[vector_search_top_k, vector_rerank_top_n, do_rerank, search_method, score_threshold],
            outputs=[langchain_status],
        )
        score_threshold.change(
            update_retriever_fn,
            inputs=[vector_search_top_k, vector_rerank_top_n, do_rerank, search_method, score_threshold],
            outputs=[langchain_status],
        )
    return demo
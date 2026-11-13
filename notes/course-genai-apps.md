# Course: Building Generative AI-Powered Applications with Python

IBM, Coursera, about 15 h. Task 1.3 in `../../plan.md`.

For each module, 3–5 lines: what it taught, and what I'd use in this project.

## Module 1: image captioning (29/10, about 3 h)

**What it taught.** Generative AI for image captioning. We worked with Hugging Face, an open community platform that lets developers use AI models. We used BLIP, a small vision-language model that generates a caption from an image, and Gradio, a Python library that is easy to connect to an AI model and gives the app a web UI. We also used ResNet-18, a model that classifies a whole image into one of 1,000 fixed categories instead of writing a caption.

**What I'd use.** Not these models: they are not as good as an LLM, and LLMs are not expensive today. But I understand the advantage of a small, specialized model, and in 2026 there are probably better small models that cut costs for specific purposes. (Claude: Gradio itself is worth keeping, for quick client demos.)

**Doubt.** Which famous applications use small models like these today, and why? Answer: photo apps that search your pictures by content (on the phone, private and free per image), content moderation on social networks (billions of images a day, too many for an LLM), phone cameras and live text reading (real time, offline), and self-driving cars (instant, no internet). The reasons: scale, speed, privacy and offline use.

## Module 2: chatbots (1/11, about 2 h)

**What it taught.** How to create a chatbot, both with a non-LLM model and with an LLM. The LLM is way better: its responses are related to your messages most (or all) of the time. The LLM was SmolLM2-360M-Instruct, and the other model was BlenderBot-400M-distill. We learned how to store the history of the conversation, how to wrap the model in a loop to have a conversation, what a token is and why we need tokenization. We also used Flask for the backend server. (Claude: both models are about the same size, so the difference is not size. BlenderBot is a sequence-to-sequence model trained only for chit-chat; SmolLM2 is a causal model that is *instruction-tuned*, trained to follow what the user asks.)

**What I'd use.** The LLM, for conversations with customers, if I accept the risk of the model hallucinating. I also enjoyed developing a server program (`app.py`) and a real-world setup: client, server, server program, chatbot.

**Doubt.** Is an LLM like this worth the risk for companies, on the customer experience side? Answer: a model this small, no; a large LLM with guardrails, yes, and many companies already use one. The known failures: Air Canada's chatbot invented a refund policy and a tribunal made the airline honour it (2024); a Chevrolet dealer's bot agreed to sell a car for USD 1 (2023); DPD's bot swore at a customer (2024). Klarna said its assistant did the work of 700 agents (2024), then hired humans again because quality dropped (2025). What makes it safe enough: a large model, answers grounded in the company's own documents (RAG), a narrow scope, a hand-off to a human when it isn't sure, no promises or payments without a check, and tests and logs of real conversations. That list is most of an FDE's job on a customer-service project.

## Module 3: voice assistant

**What it taught.** How to build a voice assistant; in a more general way, it introduced the deep neural networks that process audio to transcribe spoken words and vice versa: the STT and TTS processes. I also learned about Docker: an open platform that lets you work in isolated workspaces called "containers".

**What I'd use.** I don't like the particular models we used, since they are outdated, but I liked the possibility of talking with an assistant instead of writing. I don't have an application for this right now. (Later the same day I set up Piper, a local TTS voice, to read Claude Code's replies aloud.)

**Doubt.** How important is it for an FDE to understand the different ways we can use AI, and which application should I focus on? Answer: breadth at the level of "what's possible, what it costs and what can go wrong" across text, voice and images, since clients ask for all three. Depth in text LLMs (extraction, RAG, agents, evals), which is what FDE and applied AI openings ask for. Voice is mostly a front end on top of the same LLM (STT → LLM → TTS), so knowing how those pieces fit together is enough for now.

## Module 4: meeting assistant (4/11, about 2 h)

**What it taught.** How to use OpenAI Whisper, a speech recognition system built on a deep learning model, with an LLM (Llama 2) to transcribe and summarize audio files. Also, that there are good solutions for STT, and that combining them with LLMs lets you transcribe, summarize, create subtitles and more.

**What I'd use.** Right now I won't use it for anything.

**Doubt.** What models does Meta have? Order them from the most powerful to the least powerful. Answer: Meta's language models are the Llama family, open-weight (anyone can download and run them), from the strongest to the weakest: Llama 4 Maverick and Llama 4 Scout (April 2025, the strongest open Meta models; a bigger Llama 4 Behemoth was announced but not released), Llama 3.1 405B, Llama 3.3 70B and Llama 3.1 70B, Llama 3 8B, Llama 2 (2023; 70B, 13B and 7B, the one in this module), and Llama 3.2 1B and 3B (small, for phones). The number is the size in billions of parameters: inside a generation, bigger is stronger, but a newer small model often beats an older big one. In April 2026 Meta released a newer frontier model (reported as Muse Spark) as a closed, API-only model for the first time; reports on a Llama 5 conflict, so check Meta's site. Meta also has models that aren't LLMs: BlenderBot (module 2), Segment Anything (images) and Seamless (speech translation).

**Doubt.** What is a Transformer neural network? Is it a kind of generative AI model, or a kind of LLM? Answer: neither; it's an *architecture*, a way to build a neural network, published by Google in 2017 ("Attention Is All You Need"). Its key idea is attention: each word looks at all the other words to decide what matters. Models are built on it: almost every LLM (GPT, Llama, Claude) is a Transformer, and so is Whisper. The order, from general to specific: AI → machine learning → deep learning (neural networks) → the Transformer architecture → LLMs, Transformers trained on large amounts of text. Generative AI is a separate grouping, by what the model does (it creates text, images or audio), so LLMs are generative AI, but so are image models that aren't LLMs.

## Module 5: chatbot for a PDF (LangChain, RAG, LLM) (12/11 about 2 h)

**What it taught.** I learned about embeddings, vector databases and I gained hands-on experience with a project about RAG: I learned the structure needed for the script and the whole process from uploading the PDF, loading it, getting the chunks, embedding them, using the vector database and finally, doing a similar process for the question to augment it with relevant information.

**What I'll use.** I use Claude Code on a daily basis with RAG: I don't have a pipeline, but I ask on each session to load the relevant context, for example a folder that contains the relevant scripts or documents. I don't really have a specific need for developing a RAG pipeline since I don't work with sensitive data or data that have to be sourced. But I understand how useful it can be.

**Doubt.** Should I learn more about vector databases and embeddings? And what happens with the embedding if a user prompt has two questions: does it mix the embedding?
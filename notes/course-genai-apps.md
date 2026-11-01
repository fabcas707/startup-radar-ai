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

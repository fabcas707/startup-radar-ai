# Course: Building Generative AI-Powered Applications with Python

IBM, Coursera, about 15 h. Task 1.3 in `../../plan.md`.

For each module, 3–5 lines: what it taught, and what I'd use in this project.

## Module 1: image captioning (29/10, about 3 h)

**What it taught.** Generative AI for image captioning. We worked with Hugging Face, an open community platform that lets developers use AI models. We used BLIP, a small vision-language model that generates a caption from an image, and Gradio, a Python library that is easy to connect to an AI model and gives the app a web UI. We also used ResNet-18, a model that classifies a whole image into one of 1,000 fixed categories instead of writing a caption.

**What I'd use.** Not these models: they are not as good as an LLM, and LLMs are not expensive today. But I understand the advantage of a small, specialized model, and in 2026 there are probably better small models that cut costs for specific purposes. (Claude: Gradio itself is worth keeping, for quick client demos.)

**Doubt.** Which famous applications use small models like these today, and why? Answer: photo apps that search your pictures by content (on the phone, private and free per image), content moderation on social networks (billions of images a day, too many for an LLM), phone cameras and live text reading (real time, offline), and self-driving cars (instant, no internet). The reasons: scale, speed, privacy and offline use.

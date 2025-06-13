# <a name="xd7db7a7b05d0e9732fe24a84a5793a6bf3e0fb8"></a>Julia‑MPS: Offline Chatbot with MLX‑LM + MLX‑Audio
Assistant that runs **entirely on‑device** on Apple‑silicon Macs (M‑series). Chats with a 4‑bit Llama‑3 model accelerated by **MLX**, and speaks replies through **Kokoro TTS**. 

 Code hands the text to Kokoro, a tiny 82‑M parameter speech model that executes on Apple Silicon’s Metal Performance Shaders (MPS, aka the MPX path MLX uses).  No CPU inference, no Core ML conversion — just straight Metal kernels.

No Ollama, no Docker, no cloud.

-----
## <a name="why-this-repo-exists"></a>1 · Why this repo exists
- **Privacy & Airplane‑mode friendly** – everything happens on your GPU/Neural‑Engine.
- **Metal‑accelerated** – zero CUDA, runs happily on an M2‑Air or M4‑Mini.
- **System Prompt** – Persona is baked in via the system prompt.
-----
## <a name="oneminute-install"></a>2 · One‑minute install
*# Keep the toolchain fresh*\
pip install -U pip setuptools wheel cmake ninja\
\
*# Metal tensor backend*\
pip install -U mlx\
\
*# LLM utilities (quantise / chat / finetune)*\
pip install --no-cache-dir git+https://github.com/ml-explore/mlx-lm.git@main\
\
*# TTS wrapper (Kokoro → Metal)*\
pip install --no-cache-dir git+https://github.com/Blaizzy/mlx-audio.git@main
### <a name="grab-a-ready-mlx-model-no-convert-step"></a>Grab a ready MLX model (no convert step)
*# 4‑bit Meta‑Llama‑3‑8B Instruct – fits in 16 GB*\
mlx\_lm.chat --model mlx-community/Meta-Llama-3-8B-Instruct-4bit

*(First run downloads ≈ 5 GB; subsequent launches are instant.)*

-----
## <a name="quick-smoke-tests"></a>3 · Quick smoke tests
### <a name="tts"></a>TTS
python -m mlx\_audio.tts.generate \\
`  `--text "Hello world" --file\_prefix ok **&&** afplay ok\_000.wav
### <a name="chat-repl"></a>Chat REPL
mlx\_lm.chat --model mlx-community/Meta-Llama-3-8B-Instruct-4bit

-----
## <a name="running-julia-mps"></a>4 · Running Julia MPS
python main.py

You’ll see:

=== Julia MPS – Offline Chat ===\
Type 'exit' to quit.\
You: hi julia

Julia answers in text *and* speaks the reply through your default audio output.

-----
## <a name="project-layout"></a>5 · Project layout

|File|Purpose|
| :- | :- |
|main.py|Loads the 4‑bit Llama‑3 model, wraps chat + TTS, auto‑plays WAVs.|
|requirements.txt|(generate with pip freeze > requirements.txt)|
|README.md|This doc.|

-----
## <a name="how-it-works"></a>6 · How it works
1. **LLM** – JuliaLLM loads mlx-community/Meta-Llama-3-8B-Instruct-4bit. Prompt is:\
   *“You are Julia, User’s sarcastic but caring assistant. Keep replies under 60 words.”*
1. **TTS** – generate\_audio() turns Julia’s text into Kokoro WAV chunks.
1. **Playback** – each chunk is played synchronously with /usr/bin/afplay (macOS) or paplay/aplay on Linux.
1. **Filesystem race‑safe** – waits for each WAV to finish writing before playback.
-----
## <a name="common-issues-fixes"></a>7 · Common issues & fixes

|Symptom|Fix|
| :- | :- |
|metal backend not available|You’re in a Rosetta shell → open a new Terminal (arm64).|
|ValueError: max() arg is empty|TTS didn’t write files → check disk space, retry.|
|Overlapping audio|We now use blocking playback; if still overlapping, confirm afplay exists and isn’t aliased.|
|REPEATED text|Remove manual chunking – already fixed in current main.py.|

-----
## <a name="license"></a>9 · License
MIT for code. Models are released under their respective licenses – check each Hugging‑Face repo.

Happy offline chatting!

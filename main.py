import time
import os
from pathlib import Path
from mlx_audio.tts.generate import generate_audio
from mlx_lm import load as load_mlx, generate as generate_mlx
import subprocess
import platform
import re

MAX_TOKENS = 256

SYSTEM_PROMPT = (
    "You are Julia, User's sarcastic but caring offline assistant. "
    "Keep replies under 60 words, inject dry humor, disagree politely."
    "Give always short replies, never give long replies"
)

class JuliaLLM:
    def __init__(self):
        model_id = "mlx-community/Meta-Llama-3-8B-Instruct-4bit"
        self.model, self.tokenizer = load_mlx(model_id)

    def chat(self, user_input: str) -> str:
        """
        Build a single‑string prompt (system + user) because the current
        mlx_lm.generate() version does not accept a `system_prompt` kwarg.
        """
        full_prompt = (
            f"{SYSTEM_PROMPT}\n\n"
            f"User: {user_input}\n"
            f"Assistant:"
        )
        response = generate_mlx(
            model=self.model,
            tokenizer=self.tokenizer,
            prompt=full_prompt,
            max_tokens=MAX_TOKENS,
        )
        # --- strip special chat template markers like <|eot_id|> etc. ---
        response = re.sub(r"<\|[^>]+\|>", "", response)
        return response.strip()

class JuliaMPS:
    def __init__(self):
        self.llm = JuliaLLM()

    # ------------------------------------------------------------------
    def _play_audio(self, path: Path):
        """Auto‑play a WAV file cross‑platform with basic fallbacks."""
        system = platform.system()
        try:
            if system == "Darwin":  # macOS
                afplay_path = "/usr/bin/afplay"
                if Path(afplay_path).exists():
                    print(f"[DEBUG] Playing via afplay: {path}")
                    subprocess.run([afplay_path, str(path)], check=False)
                else:
                    print("[WARN] afplay not found, using 'open' fallback")
                    subprocess.run(["open", str(path)], check=False)
            elif system == "Linux":
                for player in ("paplay", "aplay", "ffplay", "play"):
                    if subprocess.run(["which", player], capture_output=True).returncode == 0:
                        subprocess.run([player, str(path)], check=False)
                        break
            elif system == "Windows":
                os.startfile(path)  # type: ignore
        except FileNotFoundError:
            print("[WARN] No suitable audio player found; please install 'afplay' or configure another CLI player.")
        except Exception as exc:
            print(f"[WARN] Could not auto‑play audio: {exc}")

    def ask(self, user_input):
        reply_text = self.llm.chat(user_input)

        output_dir = Path.home() / ".mlx_audio" / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        # --- single TTS call for the whole reply ---
        prefix = f"reply_{int(time.time()*1000)}"
        wav_ret = generate_audio(
            reply_text,
            language="es",
            file_prefix=prefix,
            output_dir=str(output_dir),
        )

        time.sleep(0.2)  # let file system settle

        # collect files from output_dir first
        chunks = list(output_dir.glob(f"{prefix}_*.wav"))

        # if none found there, try current working directory
        if not chunks:
            chunks = list(Path.cwd().glob(f"{prefix}_*.wav"))

        if not chunks:
            print("[WARN] No WAV created for reply.")
            return

        # sort chronologically
        chunks.sort(key=lambda p: p.stat().st_mtime)

        for wav in chunks:
            # wait until the file’s size stops growing (max 1 s)
            for _ in range(10):
                size_before = wav.stat().st_size
                time.sleep(0.1)
                if wav.stat().st_size == size_before and size_before > 0:
                    break
            print(f"[DEBUG] Playing {wav}")
            self._play_audio(wav)

    def cli(self):
        print("=== Julia MPS – Offline Chat ===")
        print("Type 'exit' to quit.")
        while True:
            user = input("You: ")
            if user.lower() == "exit":
                break
            self.ask(user)  # audio auto‑played

if __name__ == "__main__":
    JuliaMPS().cli()

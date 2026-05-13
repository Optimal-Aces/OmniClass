import anthropic
from app.config import ANTHROPIC_API_KEY

_client = None

def get_client() -> anthropic.Anthropic:
    global _client
    if _client is None and ANTHROPIC_API_KEY:
        _client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    return _client

def generate(system: str, prompt: str, max_tokens: int = 2048) -> str:
    """Call Claude API and return text response"""
    client = get_client()
    if not client:
        raise RuntimeError("ANTHROPIC_API_KEY not configured in .env")
    msg = client.messages.create(
        model="claude-opus-4-6",
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": prompt}]
    )
    return msg.content[0].text

def generate_json(system: str, prompt: str, max_tokens: int = 2048) -> str:
    """Call Claude API expecting JSON — strips markdown fences"""
    raw = generate(
        system + "\n\nRespond ONLY with valid JSON. No markdown, no explanation.",
        prompt,
        max_tokens
    )
    return raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
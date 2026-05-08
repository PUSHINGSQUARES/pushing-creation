from .gemini import GeminiProvider
from .openai import OpenAIProvider
from .openrouter import OpenRouterProvider
from .kling import KlingProvider
from .seedream import SeedreamProvider
from .seedance import SeedanceProvider
from .imagen import ImagenProvider

REGISTRY: dict[str, type] = {
    "gemini": GeminiProvider,
    "openai": OpenAIProvider,
    "openrouter": OpenRouterProvider,
    "kling": KlingProvider,
    "seedream": SeedreamProvider,
    "seedance": SeedanceProvider,
    "imagen": ImagenProvider,
}


def get_provider(name: str):
    cls = REGISTRY.get(name)
    if cls is None:
        raise ValueError(f"Unknown provider '{name}'. Available: {', '.join(REGISTRY)}")
    return cls()

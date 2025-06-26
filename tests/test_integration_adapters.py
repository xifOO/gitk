import os
import pytest
from core.adapters import OpenRouterAdapter
from core.models import ModelConfig

@pytest.mark.integration
def test_openrouter_generate_commit_message_real_api():
    api_key = os.getenv("GITK_OPENROUTER_TEST_API_KEY")
    if not api_key:
        pytest.skip("No API key set for integration test")

    config = ModelConfig(
        name="real-model",
        provider="openrouter",
        api_base="https://openrouter.ai/api/v1",
        model_id="qwen/qwen-2.5-72b-instruct:free", 
        is_free=False,
        max_tokens=150,
        temperature=0.7
    )

    os.environ["GITK_OPENROUTER_API_KEY"] = api_key

    adapter = OpenRouterAdapter(config)

    diff_text = "diff --git a/file.py b/file.py\nindex 83db48f..f7353d7 100644\n--- a/file.py\n+++ b/file.py\n@@ -1,4 +1,4 @@\n-print('Hello World')\n+print('Hello my friend')\n"
    commit_template = None
    instruction = None

    result = adapter.generate_commit_message(
        diff=diff_text,
        detailed=False,
        commit_template=commit_template,
        instruction=instruction
    )

    print("Generated commit message:", result)

    assert isinstance(result, str)
    assert len(result) > 0

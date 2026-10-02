import os

BASE = "/home/wslinux/nllb-env/lib/python3.12/site-packages"
INIT = BASE + "/TTS/__init__.py"
AUTO = BASE + "/TTS/tts/layers/tortoise/autoregressive.py"
DATASET = BASE + "/TTS/tts/datasets/dataset.py"
GPT_INF = BASE + "/TTS/tts/layers/xtts/gpt_inference.py"

# --- patch __init__.py ---
with open(INIT) as f:
    content = f.read()

stubs = "def is_torchcodec_available(): return True\ndef is_torch_greater_or_equal(v): return True\n"
content = content.replace("def is_torchcodec_available(): return False\n", "")
content = content.replace("def is_torchcodec_available(): return True\n", "")
content = content.replace("def is_torch_greater_or_equal(v): return True\n", "")
content = stubs + content
content = content.replace("    is_torchcodec_available,\n", "")
content = content.replace("    is_torch_greater_or_equal,\n", "")
content = content.replace(
    "raise ImportError(TORCHCODEC_IMPORT_ERROR)",
    "pass  # torchcodec not required for XTTS-v2"
)
with open(INIT, "w") as f:
    f.write(content)
print("patched __init__.py")

# --- patch autoregressive.py ---
with open(AUTO) as f:
    content = f.read()
old = "from transformers.pytorch_utils import isin_mps_friendly as isin"
if old in content:
    content = content.replace(old, "isin = torch.isin")
    with open(AUTO, "w") as f:
        f.write(content)
    print("patched autoregressive.py")
else:
    print("autoregressive.py: already patched")

# --- patch dataset.py ---
with open(DATASET) as f:
    content = f.read()
old = "from transformers.utils.import_utils import is_torch_greater_or_equal"
if old in content:
    content = content.replace(old, "def is_torch_greater_or_equal(v): return True")
    with open(DATASET, "w") as f:
        f.write(content)
    print("patched dataset.py")
else:
    print("dataset.py: already patched")

# --- patch generation/utils.py: guard None generation_config ---
GEN = BASE + "/transformers/generation/utils.py"
with open(GEN) as f:
    lines = f.readlines()

changed = False
for i, line in enumerate(lines):
    if 'self.generation_config._from_model_config' in line and 'is not None' not in line:
        lines[i] = line.replace(
            'self.generation_config._from_model_config',
            '(self.generation_config is not None and self.generation_config._from_model_config)'
        )
        changed = True
        print(f"fixed generation_config line {i+1}")
    if '    def _validate_model_class(self):' in line:
        next_i = i + 1
        if next_i < len(lines) and 'return' not in lines[next_i]:
            lines.insert(next_i, '        return  # patched\n')
            changed = True
            print(f"fixed _validate_model_class at line {i+1}")

with open(GEN, 'w') as f:
    f.writelines(lines)
print("generation/utils.py done" if changed else "generation/utils.py: already patched")

# --- ROOT FIX: give GPT2InferenceModel a non-None generation_config ---
with open(GPT_INF) as f:
    content = f.read()

# Fix getter to never return None (parent may set it to None via setter)
old_getter = "        if not hasattr(self, '_gen_cfg'): self._gen_cfg = _GenCfg()\n        return self._gen_cfg\n"
new_getter = "        if not hasattr(self, '_gen_cfg') or self._gen_cfg is None: self._gen_cfg = _GenCfg()\n        return self._gen_cfg\n"

old_class = "class GPT2InferenceModel(GPT2PreTrainedModel, GenerationMixin):"
new_class = (
    "from transformers import GenerationConfig as _GenCfg\n"
    "class GPT2InferenceModel(GPT2PreTrainedModel, GenerationMixin):\n"
    "    @property\n"
    "    def generation_config(self):\n"
    "        if not hasattr(self, '_gen_cfg') or self._gen_cfg is None: self._gen_cfg = _GenCfg()\n"
    "        return self._gen_cfg\n"
    "    @generation_config.setter\n"
    "    def generation_config(self, v): self._gen_cfg = v\n"
    "    def _validate_model_class(self): return\n"
)

changed_gpt = False
if old_getter in content:
    content = content.replace(old_getter, new_getter)
    changed_gpt = True
    print("fixed gpt_inference.py getter (never returns None)")
elif old_class in content and "_gen_cfg" not in content:
    content = content.replace(old_class, new_class)
    changed_gpt = True
    print("patched gpt_inference.py (root fix)")

# --- add prepare_inputs_for_generation if missing ---
if "prepare_inputs_for_generation" not in content:
    prep_method = (
        "    def prepare_inputs_for_generation(self, input_ids, past_key_values=None, **kwargs):\n"
        "        if past_key_values is not None:\n"
        "            input_ids = input_ids[:, -1:]\n"
        "        return {\"input_ids\": input_ids, \"past_key_values\": past_key_values,\n"
        "                \"attention_mask\": kwargs.get(\"attention_mask\"),\n"
        "                \"use_cache\": kwargs.get(\"use_cache\")}\n"
    )
    insert_after = "    def _validate_model_class(self): return\n"
    if insert_after in content:
        content = content.replace(insert_after, insert_after + prep_method)
        changed_gpt = True
        print("added prepare_inputs_for_generation to GPT2InferenceModel")
    else:
        print("WARNING: could not find _validate_model_class anchor — add prepare_inputs_for_generation manually")

if changed_gpt:
    with open(GPT_INF, "w") as f:
        f.write(content)
elif "prepare_inputs_for_generation" in content:
    print("gpt_inference.py: already fully patched")

import json
from pathlib import Path
from pydantic import BaseModel
from llama_index.core.program import LLMTextCompletionProgram
from llama_index.core import Settings
from global_settings import llm


# ---------- Schema ----------

class Decision(BaseModel):
    id: str
    title: str
    summary: str
    tags: list[str]
    source_file: str


class Rule(BaseModel):
    id: str
    rule: str
    scope: str
    notes: str
    source_file: str


class Warning(BaseModel):
    id: str
    area: str
    message: str
    severity: str
    source_file: str


class Dependency(BaseModel):
    id: str
    name: str
    description: str
    related_component: str
    source_file: str


class ExtractedData(BaseModel):
    decisions: list[Decision]
    rules: list[Rule]
    warnings: list[Warning]
    dependencies: list[Dependency]


# ---------- Structured Extraction ----------

extract_program = LLMTextCompletionProgram.from_defaults(
    output_cls=ExtractedData,
    prompt_template_str="""
Extract structured project information from the following documentation.

Return JSON with:

- decisions
- rules
- warnings
- dependencies

Text:
{context}
""",
    llm=llm,
)


# ---------- Extraction Loop ----------

docs_path = Path("docs")

result = {
    "decisions": [],
    "rules": [],
    "warnings": [],
    "dependencies": []
}

for file in docs_path.glob("*.md"):

    text = file.read_text()

    extracted = extract_program(context=text)

    for d in extracted.decisions:
        result["decisions"].append(d.model_dump())

    for r in extracted.rules:
        result["rules"].append(r.model_dump())

    for w in extracted.warnings:
        result["warnings"].append(w.model_dump())

    for dep in extracted.dependencies:
        result["dependencies"].append(dep.model_dump())


# ---------- Save JSON ----------

with open("structured_data.json", "w", encoding="utf-8") as f:
    json.dump(result, f, indent=2, ensure_ascii=False)


print("Structured data saved to structured_data.json")
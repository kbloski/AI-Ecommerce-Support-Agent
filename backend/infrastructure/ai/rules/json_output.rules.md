# JSON OUTPUT RULES

- Follow the JSON format required by the task.
- Return only valid JSON, without markdown, code blocks, explanations, or text outside the JSON.
- The JSON must be directly parseable by a standard JSON parser.
- Follow the provided JSON schema exactly.
- Do not add, remove, rename, or translate fields unless the task explicitly allows it.
- Keep technical names, identifiers, variable names, property names, field names, and schema keys unchanged.
- Preserve the data type of every field. Arrays must remain arrays, and objects must remain objects.
- Do not use null unless the task explicitly allows it.
- Use an empty string only when the task explicitly allows or requires it.
- Handle missing or unavailable values according to the task instructions.

# Ralph prompts

`PROMPT.md` is the default prompt file referenced by `event_loop.prompt_file`.

Override it per run with `ralph run -p "..."` or `-P path/to/prompt.md`.

## Notes

- Keep prompts short; put durable rules in `AGENTS.md` and project config.
- Do not paste whole files into the prompt. Reference paths.
- Put acceptance criteria in the prompt; Ralph gates on evidence.

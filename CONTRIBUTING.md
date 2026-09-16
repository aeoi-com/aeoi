# Contributing

Thank you for looking at aeoi. Rules of the road:

## Sources first

Every rule the toolkit enforces is traced to a primary source: the OECD XSDs and user guides
pinned in `docs/sources/manifest.json`, the ESTV Technische Wegleitung (section numbers in the
code and in `docs/ESTV-RULES.md`), the SIF partner-state list. A change to a rule comes with the
citation; a rule without a source is a bug.

## Developer Certificate of Origin

Contributions are accepted under the [Developer Certificate of Origin 1.1](https://developercertificate.org/).
Sign every commit (`git commit -s`), which adds

    Signed-off-by: Your Name <you@example.com>

and certifies that you wrote the change or have the right to submit it under the Apache-2.0
licence. CI refuses pull requests with unsigned commits. No CLA.

## Working on the code

```bash
python -m venv .venv
.venv/bin/python -m pip install -e ".[dev]"
.venv/bin/python -m pytest
.venv/bin/ruff check src tests tools && .venv/bin/ruff format src/aeoi/crs src/aeoi/estv tests tools
```

- Generated models (`src/aeoi/schemas/`) are not edited by hand: `python tools/generate_models.py`.
- The flat-format contract (`docs/FLAT-FORMAT.md`) and the rules catalogue
  (`docs/ESTV-RULES.md`) are rendered from the code: `python tools/render_flat_format.py`,
  `python tools/build_rules_catalogue.py`.
- The partner-state list is refreshed with `python tools/partner_states.py` (pins the SIF page).
- Tests are the specification: a scenario from the Wegleitung (e.g. 6.4.5) gets a test named after it.

## Data

Never commit real reporting data, keys, portal downloads or registries (`.gitignore` covers the
usual names). Test data is invented, like the examples of the Wegleitung.

## Reporting a portal rejection

`aeoi estv status outcome.txt` explains every code. If a code concerns a rule the toolkit claims to
enforce (the output says so), open an issue with the code, the section and the message text - never
with the file: it contains account-holder data.

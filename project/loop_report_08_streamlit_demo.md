# Loop Report

## Objective

Add a Japanese-first, English-switchable Streamlit demo that compares Naive RAG, Hybrid RAG, and HandoverGap RAG.

## Winning Gate

This improves demo clarity and article evidence by making the central claim visible in one screen: Naive RAG answers, while HandoverGap RAG blocks unsafe transfer and asks clarification questions.

## Files Changed

- `src/handovergap/demo_app.py`
- `examples/streamlit_app.py`
- `src/handovergap/cli.py`
- `tests/test_demo_app.py`
- `tests/test_serve_command.py`
- `docs/assets/demo-ja.png`
- `design-qa.md`

## Validation

- [x] `.venv/bin/handovergap serve --help`
- [x] Streamlit AppTest renders Japanese default
- [x] Streamlit AppTest switches to English
- [x] Browser renders `http://127.0.0.1:8501`
- [x] `design-qa.md` final result is `passed`

## Observations

- The selected three-lane comparison direction communicates the method difference faster than a trace-first layout.
- Generated mock metrics and document metadata were replaced with package-backed values.
- The demo remains optional and does not change CLI-first installation.

## Failures

- Browser automation did not reliably click Streamlit's segmented language control after rerender, although the same interaction passes Streamlit AppTest.

## Context Updates

- Japanese is the demo default.
- English is the primary package and PyPI documentation language.

## Next Recommended Loop

Loop 09: implementation-backed article draft and results.

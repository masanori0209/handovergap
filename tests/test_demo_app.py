from streamlit.testing.v1 import AppTest


def test_demo_renders_japanese_default_and_three_method_comparison() -> None:
    app = AppTest.from_file("examples/streamlit_app.py")

    app.run(timeout=30)

    assert not app.exception
    markdown = "\n".join(item.value for item in app.markdown)
    assert "正しい記憶でも、引き継げるとは限らない。" in markdown
    assert "Naive RAG" in markdown
    assert "Hybrid RAG" in markdown
    assert "HandoverGap RAG" in markdown
    assert "BLOCKED" in markdown


def test_demo_language_switch_renders_english_thesis() -> None:
    app = AppTest.from_file("examples/streamlit_app.py")
    app.run(timeout=30)

    app.button_group[0].set_value("English").run(timeout=30)

    markdown = "\n".join(item.value for item in app.markdown)
    assert "Correct memories are not always transferable." in markdown

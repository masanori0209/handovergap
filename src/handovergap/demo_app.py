from __future__ import annotations

import html

import streamlit as st

from handovergap.core.baselines import HybridRAGBaseline, NaiveRAGBaseline
from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.slot_rules import ROLE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore

COPY = {
    "日本語": {
        "thesis": "正しい記憶でも、引き継げるとは限らない。",
        "language": "言語",
        "scenario": "シナリオ",
        "role": "引き継ぎ先の役割",
        "memory": "記憶",
        "task": "引き継ぎタスク",
        "direct_answer": "記憶をそのまま根拠として回答します。",
        "evidence_answer": "関連する証拠を添えて回答します。",
        "blocked_answer": "重要な前提が不足しているため、回答を保留します。",
        "answer": "回答",
        "evidence": "関連証拠",
        "warning": "警告",
        "status": "転送可否",
        "blocked": "BLOCKED / 回答保留",
        "transferable": "TRANSFERABLE",
        "score": "転送可能性スコア",
        "gaps": "検出されたギャップ",
        "questions": "確認質問",
        "slot_audit": "役割条件付きスロット監査",
        "slot": "スロット",
        "slot_status": "状態",
        "filled": "充足",
        "missing": "不足",
        "comparison": "評価比較",
        "method": "手法",
        "scenarios": "シナリオ数",
        "tgr": "暗黙ギャップ検出率",
        "utp": "不適切転送の防止率",
        "coverage": "質問カバレッジ",
        "naive_warning": "転送可能性を検査せず、安全と仮定します。",
        "hybrid_warning": "証拠は増えますが、役割ごとの不足前提は網羅しません。",
        "no_gaps": "重要な不足スロットはありません。",
        "no_questions": "追加の確認質問はありません。",
    },
    "English": {
        "thesis": "Correct memories are not always transferable.",
        "language": "Language",
        "scenario": "Scenario",
        "role": "Successor role",
        "memory": "Memory",
        "task": "Handover task",
        "direct_answer": "Answers directly from the retrieved memory.",
        "evidence_answer": "Answers with related evidence attached.",
        "blocked_answer": "Withholds the answer because critical context is missing.",
        "answer": "Answer",
        "evidence": "Related evidence",
        "warning": "Warning",
        "status": "Transferability",
        "blocked": "BLOCKED / ANSWER WITHHELD",
        "transferable": "TRANSFERABLE",
        "score": "Transferability score",
        "gaps": "Detected gaps",
        "questions": "Clarification questions",
        "slot_audit": "Role-conditioned slot audit",
        "slot": "Slot",
        "slot_status": "Status",
        "filled": "Filled",
        "missing": "Missing",
        "comparison": "Evaluation comparison",
        "method": "Method",
        "scenarios": "Scenarios",
        "tgr": "Tacit Gap Recall",
        "utp": "Unsafe Transfer Prevention",
        "coverage": "Question Coverage",
        "naive_warning": "Assumes the memory is safe without testing transferability.",
        "hybrid_warning": "Adds evidence but does not exhaust role-specific missing context.",
        "no_gaps": "No critical missing slots.",
        "no_questions": "No clarification questions are required.",
    },
}


def render_app() -> None:
    st.set_page_config(page_title="HandoverGap RAG", page_icon="HG", layout="wide")
    _inject_css()

    store = InMemoryStore.from_builtin_dataset()
    scenarios = store.list_scenarios()

    header_left, header_right = st.columns([5, 1])
    with header_right:
        language = st.segmented_control(
            "Language / 言語",
            options=["日本語", "English"],
            default="日本語",
            label_visibility="collapsed",
        )
    language = language or "日本語"
    copy = COPY[language]

    with header_left:
        st.markdown(
            f'<div class="app-title">HandoverGap RAG <span>{html.escape(copy["thesis"])}</span></div>',
            unsafe_allow_html=True,
        )

    controls_left, controls_right = st.columns([2, 3])
    scenario_options = [f"{item.scenario_id} · {item.handover_task}" for item in scenarios]
    with controls_left:
        selected_label = st.selectbox(copy["scenario"], scenario_options, index=0)
    selected_id = selected_label.split(" · ", 1)[0]
    source_scenario = next(item for item in scenarios if item.scenario_id == selected_id)
    with controls_right:
        role = st.segmented_control(copy["role"], ["CS", "Engineer", "Sales"], default=source_scenario.successor_role)
    role = role or source_scenario.successor_role
    scenario = source_scenario.model_copy(update={"successor_role": role})

    st.markdown(
        f"""
        <section class="memory-band">
          <div><small>{html.escape(copy["memory"])}</small><strong>{html.escape(scenario.memory)}</strong></div>
          <div><small>{html.escape(copy["task"])}</small><strong>{html.escape(scenario.handover_task)}</strong></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    demo_store = InMemoryStore([scenario])
    detector = HandoverGapDetector(store=demo_store)
    result = detector.detect(scenario.scenario_id, scenario.successor_role)
    naive = NaiveRAGBaseline().predict(scenario)
    hybrid = HybridRAGBaseline().predict(scenario)

    naive_col, hybrid_col, gap_col = st.columns(3, gap="small")
    with naive_col:
        _method_header("Naive RAG")
        _answer_block(copy["answer"], scenario.memory, copy["direct_answer"])
        st.markdown(f'<div class="safe-tag">SAFE ASSUMPTION</div><p>{copy["naive_warning"]}</p>', unsafe_allow_html=True)
    with hybrid_col:
        _method_header("Hybrid RAG")
        _answer_block(copy["answer"], scenario.memory, copy["evidence_answer"])
        st.markdown(f'<div class="section-label">{copy["evidence"]}</div>', unsafe_allow_html=True)
        for event in scenario.evidence_events[:2]:
            st.markdown(
                f'<div class="evidence-row"><b>{html.escape(event.source_type)}</b><span>{html.escape(event.content)}</span></div>',
                unsafe_allow_html=True,
            )
        st.warning(copy["hybrid_warning"])
    with gap_col:
        _method_header("HandoverGap RAG", accent=True)
        blocked = result.transferability_status == "blocked"
        status = copy["blocked"] if blocked else copy["transferable"]
        st.markdown(
            f'<div class="status-line {"blocked" if blocked else "ok"}">{html.escape(status)}</div>'
            f'<div class="score-line"><span>{copy["score"]}</span><strong>{result.transferability_score:.2f}</strong></div>',
            unsafe_allow_html=True,
        )
        st.markdown(f'<div class="section-label">{copy["gaps"]}</div>', unsafe_allow_html=True)
        if result.gaps:
            for gap in result.gaps:
                st.markdown(
                    f'<div class="gap-row"><b>{html.escape(gap.severity)}</b><span>{html.escape(gap.gap_type)}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success(copy["no_gaps"])
        st.markdown(f'<div class="section-label">{copy["questions"]}</div>', unsafe_allow_html=True)
        if result.questions:
            for index, question in enumerate(result.questions, start=1):
                st.markdown(
                    f'<div class="question-row"><b>{index}</b><span>{html.escape(question.question)}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success(copy["no_questions"])

    st.markdown(f'<h2 class="section-title">{copy["slot_audit"]}</h2>', unsafe_allow_html=True)
    required_slots = ROLE_REQUIRED_SLOTS[scenario.successor_role]
    slot_rows = [
        {
            copy["slot"]: slot,
            copy["slot_status"]: copy["filled"] if slot in scenario.provided_slots else copy["missing"],
        }
        for slot in required_slots
    ]
    st.dataframe(slot_rows, width="stretch", hide_index=True)

    evaluator = HandoverGapEvaluator(store=store)
    st.markdown(f'<h2 class="section-title">{copy["comparison"]}</h2>', unsafe_allow_html=True)
    metric_rows = [
        {
            copy["method"]: metric.method,
            copy["scenarios"]: metric.scenarios,
            copy["tgr"]: f"{metric.tacit_gap_recall:.2f}",
            copy["utp"]: f"{metric.unsafe_transfer_prevention:.2f}",
            copy["coverage"]: f"{metric.question_coverage:.2f}",
        }
        for metric in evaluator.compare()
    ]
    st.dataframe(metric_rows, width="stretch", hide_index=True)

    st.caption(
        f"naive gaps={len(naive.gap_slots)} · hybrid gaps={len(hybrid.gap_slots)} · "
        f"handovergap gaps={len(result.gaps)} · HandoverGapBench mini v0.1"
    )


def _method_header(title: str, accent: bool = False) -> None:
    css_class = "method-header accent" if accent else "method-header"
    st.markdown(f'<div class="{css_class}">{html.escape(title)}</div>', unsafe_allow_html=True)


def _answer_block(label: str, memory: str, description: str) -> None:
    st.markdown(
        f'<div class="section-label">{html.escape(label)}</div>'
        f'<p class="answer-copy">{html.escape(memory)}</p>'
        f'<p class="muted">{html.escape(description)}</p>',
        unsafe_allow_html=True,
    )


def _inject_css() -> None:
    st.markdown(
        """
        <style>
          [data-testid="stHeader"],
          [data-testid="stToolbar"],
          [data-testid="stDecoration"] { display: none; }
          .stApp { background: #fbfbfa; color: #1e2428; }
          .block-container { max-width: 1440px; padding: 1.2rem 1.5rem 2.5rem; }
          .app-title { font-size: 1.7rem; font-weight: 750; padding: .35rem 0 1rem; border-bottom: 1px solid #d8dcde; }
          .app-title span { font-size: .92rem; font-weight: 450; color: #5b6368; margin-left: 1rem; }
          .memory-band { display: grid; grid-template-columns: 1fr 1fr; border: 1px solid #d8dcde; margin: .35rem 0 .75rem; }
          .memory-band div { padding: .8rem 1rem; min-width: 0; }
          .memory-band div + div { border-left: 1px solid #d8dcde; }
          .memory-band small { display: block; color: #697177; font-size: .72rem; text-transform: uppercase; margin-bottom: .25rem; }
          .memory-band strong { display: block; font-size: 1rem; overflow-wrap: anywhere; }
          [data-testid="stColumn"] { min-width: 0; }
          .method-header { border: 1px solid #d8dcde; border-bottom: 3px solid #1d7f73; padding: .65rem .8rem; font-size: 1.08rem; font-weight: 750; }
          .method-header.accent { color: #bd2329; border-bottom-color: #bd2329; }
          .section-label { font-size: .74rem; font-weight: 750; text-transform: uppercase; color: #687178; margin-top: .85rem; margin-bottom: .3rem; }
          .answer-copy { min-height: 3.5rem; font-weight: 650; border-bottom: 1px solid #e1e4e5; padding-bottom: .65rem; overflow-wrap: anywhere; }
          .muted { color: #687178; min-height: 2.5rem; font-size: .88rem; }
          .safe-tag { display: inline-block; border: 1px solid #1d8b7d; color: #146a60; padding: .15rem .4rem; font-size: .74rem; font-weight: 750; }
          .evidence-row, .gap-row, .question-row { display: grid; grid-template-columns: 5.5rem 1fr; gap: .45rem; border-top: 1px solid #e1e4e5; padding: .4rem 0; font-size: .84rem; overflow-wrap: anywhere; }
          .evidence-row b { color: #235ba8; }
          .gap-row b { color: #bd2329; }
          .question-row { grid-template-columns: 1.5rem 1fr; }
          .question-row b { color: #bd2329; }
          .status-line { margin-top: .8rem; padding: .5rem .65rem; font-weight: 800; border: 1px solid; }
          .status-line.blocked { color: #bd2329; border-color: #e6a7aa; background: #fff7f7; }
          .status-line.ok { color: #156b55; border-color: #9bcbbb; background: #f4fbf8; }
          .score-line { display: flex; justify-content: space-between; align-items: baseline; border-bottom: 1px solid #d8dcde; padding: .6rem 0; }
          .score-line span { color: #687178; font-size: .82rem; }
          .score-line strong { color: #bd2329; font-size: 1.55rem; }
          .section-title { font-size: 1rem; margin: 1.25rem 0 .35rem; padding-top: .6rem; border-top: 1px solid #cfd4d6; }
          div[data-testid="stDataFrame"] { border: 1px solid #d8dcde; }
          div[data-testid="stAlert"] { border-radius: 2px; }
          button, [data-baseweb="select"] > div { border-radius: 3px !important; }
          @media (max-width: 760px) {
            .block-container { padding: 1rem .75rem 1.5rem; }
            .app-title span { display: block; margin: .25rem 0 0; }
            .memory-band { grid-template-columns: 1fr; }
            .memory-band div + div { border-left: 0; border-top: 1px solid #d8dcde; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render_app()

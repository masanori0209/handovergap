from __future__ import annotations

import hashlib
import html
import json
import os
from typing import Any

import streamlit as st

from handovergap.core.baselines import HybridRAGBaseline, NaiveRAGBaseline
from handovergap.core.detector import HandoverGapDetector
from handovergap.core.evaluator import HandoverGapEvaluator
from handovergap.schemas import EvidenceEvent, HandoverScenario
from handovergap.semantic_slot_filling import fill_slots_with_openai, usage_summary
from handovergap.slot_rules import PROFILE_REQUIRED_SLOTS
from handovergap.store import InMemoryStore

COPY = {
    "日本語": {
        "thesis": "正しい記憶を、特定プロファイルが安全に使える形へ検査する。",
        "scenario": "ケース",
        "role": "プロファイル",
        "role_note": "CS/技術/商談はデモ用プリセットです。特定業界ではなく、プロファイルごとに必要な前提を変える例です。",
        "mode": "実行モード",
        "model": "OpenAIモデル",
        "prompt_profile": "プロンプト設定",
        "local": "ローカルサンプル",
        "live": "実LLM + TiDB",
        "run_live": "実LLMでスロット抽出してTiDBへ保存",
        "memory": "取得された記憶",
        "task": "タスク文脈",
        "pipeline": "RAG準備度チェック",
        "retrieved": "記憶の取得",
        "slot_fill": "意味的スロット抽出",
        "gap_check": "役割別ギャップ検査",
        "persist": "TiDB監査保存",
        "direct_answer": "取得記憶だけで回答すると、欠けた前提を見落とします。",
        "evidence_answer": "関連証拠を添えても、プロファイルごとの必須スロットは残ります。",
        "handover_answer": "プロファイルに必要なスロットを検査し、不足があれば回答を止めます。",
        "answer": "処理結果",
        "evidence": "検索された証拠",
        "status": "転送可否",
        "score": "転送可能性",
        "gaps": "不足スロット",
        "questions": "確認質問",
        "slot_audit": "スロット抽出の監査",
        "slot": "スロット",
        "slot_status": "状態",
        "filled": "充足",
        "missing": "不足",
        "rationale": "判定理由",
        "comparison": "ベンチマーク概要",
        "method": "手法",
        "scenarios": "件数",
        "tgr": "ギャップ検出率",
        "utp": "不安全転送の防止率",
        "coverage": "質問カバレッジ",
        "no_gaps": "必須スロットは充足しています。",
        "no_questions": "追加確認は不要です。",
        "live_hint": "OPENAI_API_KEY と TiDB接続情報がある場合だけ実行します。未設定ならローカルサンプルで動きます。",
        "live_success": "実LLMのスロット抽出結果を使って検出しました。",
        "tidb_success": "TiDBへ監査行を保存しました。",
        "tidb_skip": "TiDB接続情報がないため、永続化はスキップしました。",
        "local_detail": "ローカル / 同梱スロット",
        "retrieved_detail": "記憶 + 証拠",
        "gap_check_detail": "プロファイル別の必須スロット",
        "local_status": "ローカル",
        "live_status": "実行済み",
        "deterministic_detail": "決定的ルール / 同梱スロット",
        "optional_detail": "任意",
        "safe_assumption": "安全と仮定",
        "evidence_added": "証拠を追加",
        "blocked": "回答保留",
        "caption": "naive不足={naive} · hybrid不足={hybrid} · handovergap不足={handovergap} · 実行={mode}",
        "local_mode": "ローカル",
        "live_mode": "実LLM",
        "local_filled": "ローカルサンプルで充足",
        "local_missing": "ローカルサンプルでは不足",
    },
    "English": {
        "thesis": "Checks whether correct memory is safe for a specific profile to use.",
        "scenario": "Case",
        "role": "Profile",
        "role_note": "Support, engineering, and sales are demo presets. They are examples of profile-specific readiness checks, not a fixed industry taxonomy.",
        "mode": "Run mode",
        "model": "OpenAI model",
        "prompt_profile": "Prompt profile",
        "local": "Local sample",
        "live": "Live OpenAI + TiDB",
        "run_live": "Run live slot filling and persist to TiDB",
        "memory": "Retrieved memory",
        "task": "Task context",
        "pipeline": "RAG readiness pipeline",
        "retrieved": "Retrieved memory",
        "slot_fill": "Semantic slot filling",
        "gap_check": "Profile gap check",
        "persist": "TiDB audit store",
        "direct_answer": "Answering from retrieved memory alone misses tacit prerequisites.",
        "evidence_answer": "Adding evidence still does not exhaust profile-required slots.",
        "handover_answer": "Checks profile-required slots and withholds unsafe answers.",
        "answer": "Result",
        "evidence": "Retrieved evidence",
        "status": "Transferability",
        "score": "Transferability",
        "gaps": "Missing slots",
        "questions": "Clarification questions",
        "slot_audit": "Slot filling audit",
        "slot": "slot",
        "slot_status": "status",
        "filled": "filled",
        "missing": "missing",
        "rationale": "rationale",
        "comparison": "Benchmark snapshot",
        "method": "Method",
        "scenarios": "Cases",
        "tgr": "Gap Recall",
        "utp": "Unsafe Prevention",
        "coverage": "Question Coverage",
        "no_gaps": "Required slots are filled.",
        "no_questions": "No extra questions are required.",
        "live_hint": "Runs only when OPENAI_API_KEY and TiDB connection settings are present. Local sample works offline.",
        "live_success": "Detected gaps from live LLM slot filling.",
        "tidb_success": "Persisted audit rows to TiDB.",
        "tidb_skip": "Skipped persistence because TiDB connection settings were not found.",
        "local_detail": "local / bundled slots",
        "retrieved_detail": "memory + evidence",
        "gap_check_detail": "profile-required slots",
        "local_status": "local",
        "live_status": "live",
        "deterministic_detail": "deterministic / bundled slots",
        "optional_detail": "optional",
        "safe_assumption": "SAFE ASSUMPTION",
        "evidence_added": "EVIDENCE ADDED",
        "blocked": "BLOCKED",
        "caption": "naive gaps={naive} · hybrid gaps={hybrid} · handovergap gaps={handovergap} · mode={mode}",
        "local_mode": "local",
        "live_mode": "live",
        "local_filled": "provided by local sample",
        "local_missing": "missing in local sample",
    },
}

ROLE_LABELS = {
    "日本語": {
        "CS": "サポート対応",
        "Engineer": "技術運用",
        "Sales": "商談レビュー",
    },
    "English": {
        "CS": "Support response",
        "Engineer": "Engineering operations",
        "Sales": "Deal review",
    },
}

SOURCE_TYPE_LABELS = {
    "日本語": {
        "crm_note": "CRMメモ",
        "incident_note": "障害メモ",
        "support_macro": "サポート文面案",
        "runbook": "運用手順書",
        "pull_request": "プルリクエスト",
        "planning_note": "計画メモ",
        "email_summary": "メール要約",
        "legal_note": "法務メモ",
    },
    "English": {},
}

LOCALIZED_SCENARIO_TEXT = {
    "日本語": {
        "D-CS-01": {
            "memory": "架空テナント Northstar Retail は6月請求だけCSV出力で回避する。API修正は四半期締め後の予定だが確定ではない。",
            "task_context": "回答権限を守りながら、請求CSV回避策への追加問い合わせに対応する",
            "evidence": [
                "CS記録では、財務管理者は6月のみCSV出力になることを把握済み。ただしAPI時期について承認済みの外部向け文面は記録されていない。",
                "技術側はAPI不具合が調査中であることを確認。CSV出力に失敗した場合、サポートは請求IDを集めて請求オンコールへエスカレーションする。",
                "文面案: 「6月分はCSVで提供し、API問題は技術チームが調査中です」。",
            ],
        },
        "D-ENG-01": {
            "memory": "架空プロジェクト Partner Sync では、プレミアムテナント向けwebhook再試行を有効化した。ただしエラー分類が安定するまでAPI backfillは手動で行う。",
            "task_context": "夜間当番がwebhook失敗を復旧し、API backfillへ進める条件を判断する",
            "evidence": [
                "運用手順書PS-42には、再試行上限、タイムアウト挙動、重複イベントの既知症状、partner-sync-oncallへのエスカレーション先がある。",
                "PR #1842 はプレミアムテナントのwebhookだけに再試行の冪等性を追加。ロールバックコマンドとダッシュボードリンクも含まれる。",
                "重複イベント率が2週間0.1%未満で安定したら、backfill自動化を再検討する。",
            ],
        },
        "D-SALES-01": {
            "memory": "架空アカウント ElmWorks には更新時に旧analytics価格を提示できる可能性がある。ただしデータ保持の覚書を法務が確認した場合に限る。",
            "task_context": "更新見積の商談を引き継ぎ、顧客へ約束できる範囲を判断する",
            "evidence": [
                "顧客は今週中の更新見積を期待している。旧単価は社内希望だが、データ保持の覚書はまだ法務承認されていない。",
                "顧客には見積を準備中とだけ伝えており、価格例外はまだ約束していない。",
                "承認は保留中。Salesは覚書がクリアされるまで旧価格を約束してはいけない。",
            ],
        },
    },
    "English": {
        "D-CS-01": {
            "task_context": "Respond to follow-up questions about the invoice CSV workaround without overstepping support authority",
        },
        "D-ENG-01": {
            "task_context": "Recover webhook failures during on-call and decide when API backfill can move forward",
        },
        "D-SALES-01": {
            "task_context": "Take over a renewal quote and decide what can safely be promised to the customer",
        },
    },
}


DEMO_SCENARIOS = [
    HandoverScenario(
        scenario_id="D-CS-01",
        memory=(
            "Fictional tenant Northstar Retail will use a CSV export workaround for the June invoice run; "
            "the API fix is tentatively planned after the quarter close."
        ),
        evidence_events=[
            EvidenceEvent(
                source_type="crm_note",
                content=(
                    "Customer success logged that the finance admin knows a CSV export will be used for June only. "
                    "No approved wording for API timing is recorded."
                ),
            ),
            EvidenceEvent(
                source_type="incident_note",
                content=(
                    "Engineering confirmed the API defect is still under investigation. If the CSV export fails, "
                    "support should collect the invoice id and escalate to the billing on-call channel."
                ),
            ),
            EvidenceEvent(
                source_type="support_macro",
                content="Draft macro says: 'We will provide the June export via CSV while Engineering investigates the API issue.'",
            ),
        ],
        profile="CS",
        memory_type="decision",
        task_context="回答権限を守りながら、請求CSV回避策への追加問い合わせに対応する",
        provided_slots=["communication_status", "scope", "fallback_plan", "escalation_path", "customer_facing_wording"],
        evidence_slots=["communication_status", "scope", "fallback_plan", "escalation_path", "customer_facing_wording"],
        gold_gaps=[],
        gold_questions=[],
        unsafe_transfer_label=False,
    ),
    HandoverScenario(
        scenario_id="D-ENG-01",
        memory=(
            "For the fictional Partner Sync project, webhook retries are enabled for premium tenants, "
            "but API backfill remains manual until error classification is stable."
        ),
        evidence_events=[
            EvidenceEvent(
                source_type="runbook",
                content=(
                    "Runbook PS-42 covers retry limits, timeout behavior, known duplicate-event symptoms, "
                    "and the partner-sync-oncall escalation path."
                ),
            ),
            EvidenceEvent(
                source_type="pull_request",
                content=(
                    "PR #1842 enables retry idempotency for premium tenant webhooks only. "
                    "The rollback command and dashboard link are included."
                ),
            ),
            EvidenceEvent(
                source_type="planning_note",
                content="Backfill automation should be reconsidered after duplicate-event rate stays below 0.1% for two weeks.",
            ),
        ],
        profile="Engineer",
        memory_type="procedure",
        task_context="夜間当番がwebhook失敗を復旧し、API backfillへ進める条件を判断する",
        provided_slots=[
            "rationale",
            "technical_constraint",
            "implementation_scope",
            "trigger_for_reconsideration",
            "related_issue",
            "failure_modes",
        ],
        evidence_slots=[
            "technical_constraint",
            "implementation_scope",
            "trigger_for_reconsideration",
            "related_issue",
            "failure_modes",
        ],
        gold_gaps=[],
        gold_questions=[],
        unsafe_transfer_label=False,
    ),
    HandoverScenario(
        scenario_id="D-SALES-01",
        memory=(
            "Fictional account ElmWorks can receive the legacy analytics price for renewal, "
            "but only if Legal confirms the data-retention addendum."
        ),
        evidence_events=[
            EvidenceEvent(
                source_type="crm_note",
                content=(
                    "Customer expects a renewal quote this week. The old unit price is internally preferred, "
                    "but Legal has not approved the data-retention addendum."
                ),
            ),
            EvidenceEvent(
                source_type="email_summary",
                content="The customer has only been told that a quote is coming; no pricing exception has been promised.",
            ),
            EvidenceEvent(
                source_type="legal_note",
                content="Approval is pending. Sales must not promise the legacy price until the addendum is cleared.",
            ),
        ],
        profile="Sales",
        memory_type="risk",
        task_context="更新見積の商談を引き継ぎ、顧客へ約束できる範囲を判断する",
        provided_slots=["customer_expectation", "timeline_confidence"],
        evidence_slots=["customer_expectation", "timeline_confidence"],
        gold_gaps=[],
        gold_questions=[],
        unsafe_transfer_label=True,
    ),
]


def render_app() -> None:
    st.set_page_config(page_title="HandoverGap RAG", page_icon="HG", layout="wide")
    _load_dotenv()
    _inject_css()

    language = st.sidebar.segmented_control("Language / 言語", ["日本語", "English"], default="日本語")
    language = language or "日本語"
    copy = COPY[language]
    st.sidebar.caption(copy["live_hint"])

    store = InMemoryStore(DEMO_SCENARIOS)
    scenarios = store.list_scenarios()
    localized_scenarios = [_localized_scenario(s, language) for s in scenarios]
    selected_label = st.sidebar.selectbox(
        copy["scenario"],
        [f"{s.scenario_id} · {s.task_context}" for s in localized_scenarios],
    )
    selected_id = selected_label.split(" · ", 1)[0]
    source_scenario = next(item for item in localized_scenarios if item.scenario_id == selected_id)
    profile_labels = ROLE_LABELS[language]
    profile_options = list(profile_labels.values())
    default_profile_label = profile_labels[source_scenario.profile]
    selected_profile_label = st.sidebar.segmented_control(copy["role"], profile_options, default=default_profile_label)
    st.sidebar.caption(copy["role_note"])
    profile = _profile_from_label(selected_profile_label or default_profile_label, language)
    run_mode = st.sidebar.radio(copy["mode"], [copy["local"], copy["live"]], index=0)
    model = st.sidebar.text_input(copy["model"], value=os.getenv("OPENAI_SLOT_MODEL", "gpt-5-mini"))
    prompt_profile = st.sidebar.selectbox(copy["prompt_profile"], ["auto", "baseline", "gpt5_strict"], index=0)

    scenario = source_scenario.model_copy(update={"profile": profile or source_scenario.profile})
    live_requested = run_mode == copy["live"]

    st.markdown(
        f'<div class="app-title">HandoverGap RAG <span>{html.escape(copy["thesis"])}</span></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f"""
        <section class="memory-band">
          <div><small>{html.escape(copy["memory"])}</small><strong>{html.escape(scenario.memory)}</strong></div>
          <div><small>{html.escape(copy["task"])}</small><strong>{html.escape(scenario.task_context)}</strong></div>
        </section>
        """,
        unsafe_allow_html=True,
    )

    live_state = None
    if live_requested:
        if st.sidebar.button(copy["run_live"], type="primary", use_container_width=True):
            live_state = _run_live_pipeline(scenario, model, None if prompt_profile == "auto" else prompt_profile)
            st.session_state["live_state"] = live_state
        live_state = st.session_state.get("live_state")

    detector_input = scenario
    if live_state and live_state.get("status") == "ok":
        detector_input = scenario.model_copy(update={"provided_slots": live_state["filled_slots"]})
        st.success(copy["live_success"])
        if live_state.get("tidb_rows"):
            st.success(f'{copy["tidb_success"]} {live_state["tidb_rows"]}')
        elif live_state.get("tidb_message"):
            st.info(copy["tidb_skip"])
    elif live_requested:
        if live_state and live_state.get("status") == "error":
            st.error(live_state["message"])
        st.info(copy["live_hint"])

    demo_store = InMemoryStore([detector_input])
    detector = HandoverGapDetector(store=demo_store)
    result = detector.detect(detector_input.scenario_id, detector_input.profile)
    naive = NaiveRAGBaseline().predict(detector_input)
    hybrid = HybridRAGBaseline().predict(detector_input)

    _render_pipeline(copy, live_state)
    _render_method_comparison(copy, detector_input, result)
    _render_evidence(copy, detector_input)
    _render_slot_audit(copy, detector_input, live_state)
    _render_questions(copy, result)
    _render_benchmark(copy)

    st.caption(
        copy["caption"].format(
            naive=len(naive.gap_slots),
            hybrid=len(hybrid.gap_slots),
            handovergap=len(result.gaps),
            mode=copy["live_mode"] if live_state else copy["local_mode"],
        )
    )


def _run_live_pipeline(scenario: HandoverScenario, model: str, prompt_profile: str | None) -> dict[str, Any]:
    _load_dotenv()
    try:
        from openai import OpenAI
    except ImportError as exc:
        return {"status": "error", "message": 'Install live dependencies with: pip install "handovergap[live]"', "error": str(exc)}

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        return {"status": "error", "message": "Missing OPENAI_API_KEY"}

    with st.spinner("Running semantic slot filling..."):
        fill = fill_slots_with_openai(OpenAI(api_key=api_key), model, scenario, prompt_profile=prompt_profile)

    profiled = scenario.model_copy(update={"provided_slots": fill["filled_slots"]})
    result = HandoverGapDetector(InMemoryStore([profiled])).detect_scenario(profiled)
    payload = {
        "status": "ok",
        "model": model,
        "prompt_profile": fill["prompt_profile"],
        "filled_slots": fill["filled_slots"],
        "slot_rationales": fill["slot_rationales"],
        "usage": usage_summary(fill["usage"]),
        "transferability_status": result.transferability_status,
    }
    payload.update(_persist_live_result(scenario, result, fill))
    return payload


def _persist_live_result(scenario: HandoverScenario, result: Any, fill: dict[str, Any]) -> dict[str, Any]:
    database_url = _database_url()
    if not database_url:
        return {"tidb_rows": 0, "tidb_message": "missing_tidb_env"}
    try:
        from handovergap import TiDBStore

        store = TiDBStore(database_url)
        engine = store.create_engine(pool_recycle=300)
        store.create_schema(engine)
        memory_item_id = _memory_item_id(scenario.scenario_id)
        attempt_rows = [
            {
                "memory_item_id": memory_item_id,
                "profile": scenario.profile,
                "slot_name": item["slot_name"],
                "query_text": scenario.task_context,
                "retrieved_event_ids": json.dumps(list(range(len(scenario.evidence_events)))),
                "selected_event_id": None,
                "fill_result": json.dumps(item, ensure_ascii=False),
                "confidence": 0.8 if item["filled"] else 0.35,
                "status": "filled" if item["filled"] else "missing",
            }
            for item in fill["slot_rationales"]
        ]
        gap_rows = [
            {
                "memory_item_id": memory_item_id,
                "profile": scenario.profile,
                "task_context": scenario.task_context,
                "gap_type": gap.gap_type,
                "slot_name": gap.slot_name,
                "description": gap.description,
                "severity": gap.severity,
                "required_evidence_type": gap.slot_name,
                "status": "open",
            }
            for gap in result.gaps
        ]
        assessment_rows = [
            {
                "memory_item_id": memory_item_id,
                "profile": scenario.profile,
                "task_context": scenario.task_context,
                "transferability_score": result.transferability_score,
                "unsafe_reason": ", ".join(gap.slot_name for gap in result.gaps),
                "required_gaps_count": len(result.gaps),
                "status": result.transferability_status,
            }
        ]
        rows = (
            store.persist_slot_fill_attempts(attempt_rows, engine)
            + store.persist_context_gaps(gap_rows, engine)
            + store.persist_transfer_assessments(assessment_rows, engine)
        )
        return {"tidb_rows": rows}
    except Exception as exc:
        return {"tidb_rows": 0, "tidb_message": str(exc)}


def _database_url() -> Any | None:
    if os.getenv("HANDOVERGAP_TIDB_URL"):
        return os.getenv("HANDOVERGAP_TIDB_URL")
    required = ["TIDB_USER", "TIDB_PASSWORD", "TIDB_HOST"]
    if not all(os.getenv(name) for name in required):
        return None
    try:
        from sqlalchemy import URL
    except ImportError:
        return None
    return URL.create(
        drivername="mysql+pymysql",
        username=os.getenv("TIDB_USER"),
        password=os.getenv("TIDB_PASSWORD"),
        host=os.getenv("TIDB_HOST"),
        port=int(os.getenv("TIDB_PORT", "4000")),
        database=os.getenv("TIDB_DB_NAME", "test"),
    )


def _memory_item_id(scenario_id: str) -> int:
    return int(hashlib.sha256(scenario_id.encode()).hexdigest()[:12], 16)


def _localized_scenario(scenario: HandoverScenario, language: str) -> HandoverScenario:
    localized = LOCALIZED_SCENARIO_TEXT.get(language, {}).get(scenario.scenario_id, {})
    evidence_texts = localized.get("evidence")
    evidence_events = scenario.evidence_events
    if evidence_texts:
        source_labels = SOURCE_TYPE_LABELS.get(language, {})
        evidence_events = [
            EvidenceEvent(
                source_type=source_labels.get(event.source_type, event.source_type),
                content=evidence_texts[index],
            )
            for index, event in enumerate(scenario.evidence_events)
        ]
    return scenario.model_copy(
        update={
            "memory": localized.get("memory", scenario.memory),
            "task_context": localized.get("task_context", scenario.task_context),
            "evidence_events": evidence_events,
        }
    )


def _profile_from_label(label: str, language: str) -> str:
    for profile, display_label in ROLE_LABELS[language].items():
        if label == display_label:
            return profile
    return "CS"


def _render_pipeline(copy: dict[str, str], live_state: dict[str, Any] | None) -> None:
    status = copy["live_status"] if live_state and live_state.get("status") == "ok" else copy["local_status"]
    model = live_state.get("model", "deterministic") if live_state else "deterministic"
    usage = live_state.get("usage", {}) if live_state else {}
    st.markdown(f'<h2 class="section-title">{copy["pipeline"]}</h2>', unsafe_allow_html=True)
    cols = st.columns(4, gap="small")
    steps = [
        (copy["retrieved"], copy["retrieved_detail"]),
        (
            copy["slot_fill"],
            f"{model} / {live_state.get('prompt_profile', 'provided_slots')}"
            if live_state
            else copy["deterministic_detail"],
        ),
        (copy["gap_check"], copy["gap_check_detail"]),
        (copy["persist"], f"{live_state.get('tidb_rows', 0)} rows" if live_state else copy["optional_detail"]),
    ]
    for col, (title, detail) in zip(cols, steps, strict=True):
        col.markdown(
            f'<div class="pipeline-step"><small>{html.escape(status)}</small><b>{html.escape(title)}</b><span>{html.escape(detail)}</span></div>',
            unsafe_allow_html=True,
        )
    if usage:
        st.caption(
            f"tokens input={usage.get('input_tokens', 0)} output={usage.get('output_tokens', 0)} "
            f"reasoning={usage.get('reasoning_tokens', 0)} total={usage.get('total_tokens', 0)}"
        )


def _render_method_comparison(copy: dict[str, str], scenario: HandoverScenario, result: Any) -> None:
    st.markdown('<div class="method-grid">', unsafe_allow_html=True)
    naive_col, hybrid_col, gap_col = st.columns(3, gap="small")
    with naive_col:
        _method_card("Naive RAG", scenario.memory, copy["direct_answer"], copy["safe_assumption"], danger=False)
    with hybrid_col:
        evidence = " / ".join(event.source_type for event in scenario.evidence_events[:3])
        _method_card("Hybrid RAG", evidence, copy["evidence_answer"], copy["evidence_added"], danger=False)
    with gap_col:
        blocked = result.transferability_status == "blocked"
        status = copy["blocked"] if blocked else result.transferability_status.upper()
        _method_card("HandoverGap RAG", status, copy["handover_answer"], f'{copy["score"]}: {result.transferability_score:.2f}', danger=blocked)
    st.markdown("</div>", unsafe_allow_html=True)


def _render_evidence(copy: dict[str, str], scenario: HandoverScenario) -> None:
    st.markdown(f'<h2 class="section-title">{copy["evidence"]}</h2>', unsafe_allow_html=True)
    for event in scenario.evidence_events:
        st.markdown(
            f'<div class="evidence-row"><b>{html.escape(event.source_type)}</b><span>{html.escape(event.content)}</span></div>',
            unsafe_allow_html=True,
        )


def _render_slot_audit(copy: dict[str, str], scenario: HandoverScenario, live_state: dict[str, Any] | None) -> None:
    st.markdown(f'<h2 class="section-title">{copy["slot_audit"]}</h2>', unsafe_allow_html=True)
    rationales = {item["slot_name"]: item for item in live_state.get("slot_rationales", [])} if live_state else {}
    rows = []
    for slot in PROFILE_REQUIRED_SLOTS[scenario.profile]:
        filled = slot in scenario.provided_slots
        rationale = ""
        if slot in rationales:
            filled = rationales[slot]["filled"]
            rationale = rationales[slot]["reason"]
        rows.append(
            {
                copy["slot"]: slot,
                copy["slot_status"]: copy["filled"] if filled else copy["missing"],
                copy["rationale"]: rationale or (copy["local_filled"] if filled else copy["local_missing"]),
            }
        )
    st.dataframe(rows, width="stretch", hide_index=True)


def _render_questions(copy: dict[str, str], result: Any) -> None:
    left, right = st.columns([1, 1], gap="medium")
    with left:
        st.markdown(f'<h2 class="section-title">{copy["gaps"]}</h2>', unsafe_allow_html=True)
        if result.gaps:
            for gap in result.gaps:
                st.markdown(
                    f'<div class="gap-row"><b>{html.escape(gap.severity)}</b><span>{html.escape(gap.slot_name)} · {html.escape(gap.description)}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success(copy["no_gaps"])
    with right:
        st.markdown(f'<h2 class="section-title">{copy["questions"]}</h2>', unsafe_allow_html=True)
        if result.questions:
            for index, question in enumerate(result.questions, start=1):
                st.markdown(
                    f'<div class="question-row"><b>{index}</b><span>{html.escape(question.question)}</span></div>',
                    unsafe_allow_html=True,
                )
        else:
            st.success(copy["no_questions"])


def _render_benchmark(copy: dict[str, str]) -> None:
    evaluator = HandoverGapEvaluator(store=InMemoryStore.from_builtin_dataset())
    st.markdown(f'<h2 class="section-title">{copy["comparison"]}</h2>', unsafe_allow_html=True)
    rows = [
        {
            copy["method"]: metric.method,
            copy["scenarios"]: metric.scenarios,
            copy["tgr"]: f"{metric.tacit_gap_recall:.2f}",
            copy["utp"]: f"{metric.unsafe_transfer_prevention:.2f}",
            copy["coverage"]: f"{metric.question_coverage:.2f}",
        }
        for metric in evaluator.compare()
    ]
    st.dataframe(rows, width="stretch", hide_index=True)


def _method_card(title: str, headline: str, body: str, badge: str, danger: bool) -> None:
    klass = "method-card danger" if danger else "method-card"
    st.markdown(
        f"""
        <section class="{klass}">
          <div class="method-title">{html.escape(title)}</div>
          <strong>{html.escape(headline)}</strong>
          <p>{html.escape(body)}</p>
          <small>{html.escape(badge)}</small>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _load_dotenv() -> None:
    try:
        from dotenv import load_dotenv
    except ImportError:
        return
    load_dotenv(".env")


def _inject_css() -> None:
    st.markdown(
        """
        <style>
          html, body, [data-testid="stAppViewContainer"], .stApp {
            background: #f7f8f8 !important;
            color: #172026 !important;
          }
          [data-testid="stHeader"] {
            display: none !important;
          }
          [data-testid="stToolbar"], [data-testid="stDecoration"] { display: none !important; }
          [data-testid="stSidebar"] { background: #ffffff !important; border-right: 1px solid #d9dee2; }
          [data-testid="stSidebar"] p,
          [data-testid="stSidebar"] label,
          [data-testid="stSidebar"] span {
            color: #172026 !important;
          }
          [data-testid="stSidebar"] button,
          [data-testid="stSidebar"] [data-baseweb="select"] > div,
          [data-testid="stSidebar"] [data-baseweb="input"] > div {
            background: #ffffff !important;
            color: #172026 !important;
            border-color: #b9c4ca !important;
          }
          [data-testid="stSidebar"] input {
            color: #172026 !important;
            -webkit-text-fill-color: #172026 !important;
          }
          [data-testid="stSidebar"] [aria-checked="true"],
          [data-testid="stSidebar"] [aria-pressed="true"] {
            background: #fff7f7 !important;
            border-color: #bd2d32 !important;
          }
          .block-container { max-width: 1480px; padding: 2.1rem 1.5rem 2.5rem; }
          .app-title { font-size: 1.65rem; font-weight: 760; padding: .25rem 0 1rem; border-bottom: 1px solid #d5dade; }
          .app-title span { display: block; color: #56636b; font-size: .9rem; font-weight: 470; margin-top: .2rem; }
          .memory-band { display: grid; grid-template-columns: minmax(0, 1.35fr) minmax(0, .85fr); border: 1px solid #d5dade; background: #ffffff; margin: .8rem 0 1rem; }
          .memory-band div { padding: .85rem 1rem; min-width: 0; }
          .memory-band div + div { border-left: 1px solid #d5dade; }
          .memory-band small { display: block; color: #66747d; font-size: .72rem; text-transform: uppercase; margin-bottom: .28rem; }
          .memory-band strong { display: block; font-size: .98rem; overflow-wrap: anywhere; line-height: 1.45; }
          .pipeline-step, .method-card { background: #ffffff; border: 1px solid #d5dade; min-height: 8.2rem; padding: .8rem .9rem; }
          .pipeline-step small { display: block; color: #7a858c; font-size: .7rem; text-transform: uppercase; }
          .pipeline-step b { display: block; margin: .45rem 0 .25rem; font-size: .94rem; }
          .pipeline-step span { color: #3d4a52; font-size: .86rem; overflow-wrap: anywhere; }
          .method-card { min-height: 11rem; border-top: 4px solid #1d756c; }
          .method-card.danger { border-top-color: #bd2d32; }
          .method-card .method-title { font-weight: 800; margin-bottom: .55rem; }
          .method-card strong { display: block; min-height: 2.8rem; overflow-wrap: anywhere; line-height: 1.35; }
          .method-card p { color: #56636b; min-height: 3.2rem; margin: .65rem 0; font-size: .88rem; }
          .method-card small { border: 1px solid #c8d1d6; padding: .18rem .45rem; font-weight: 760; color: #2e3a41; }
          .method-card.danger small { color: #bd2d32; border-color: #e2a7aa; }
          .section-title { font-size: 1rem; margin: 1.3rem 0 .45rem; padding-top: .65rem; border-top: 1px solid #d5dade; }
          .evidence-row, .gap-row, .question-row { display: grid; grid-template-columns: 8.5rem minmax(0, 1fr); gap: .55rem; border-top: 1px solid #e3e7e9; padding: .48rem 0; font-size: .86rem; overflow-wrap: anywhere; }
          .evidence-row b { color: #235c9e; }
          .gap-row b, .question-row b { color: #bd2d32; }
          .question-row { grid-template-columns: 1.8rem minmax(0, 1fr); }
          div[data-testid="stDataFrame"] { border: 1px solid #d5dade; background: #ffffff; }
          button, [data-baseweb="select"] > div, [data-baseweb="input"] > div { border-radius: 4px !important; }
          @media (max-width: 780px) {
            .block-container { padding: 1rem .75rem 1.5rem; }
            .memory-band { grid-template-columns: 1fr; }
            .memory-band div + div { border-left: 0; border-top: 1px solid #d5dade; }
            .evidence-row, .gap-row { grid-template-columns: 1fr; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )


if __name__ == "__main__":
    render_app()

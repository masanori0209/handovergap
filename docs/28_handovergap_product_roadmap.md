# HandoverGap RAG PyPI実用化ロードマップ

作成日: 2026-06-15  
対象: Zennfes Spring 2026「TiDBで作るAI時代のデータ基盤」投稿記事 / `handovergap` GitHub・PyPI

---

## 1. エグゼクティブサマリ

HandoverGap RAG の勝ち筋は、単なる「TiDBでRAGを作った」ではなく、**RAGが答える直前に、その記憶を後任者へ渡してよいかを検査する Transferability Gate** として位置づけることにある。

核となるメッセージは次の一文に集約する。

> RAGの失敗は、間違った記憶を返すことだけではない。正しい記憶を、責任範囲の違う後任者に渡してしまうことでも起きる。

記事本文をさらに長くするより、GitHub / PyPI 側で次の3つを明確にするのが効く。

1. **TiDB実利用の証拠を増やす**  
   Vector Search / Full-text Search / SQL / JSON / Transaction を、説明ではなく実行パスに入れる。
2. **PyPIライブラリとして既存RAGに挟める形にする**  
   `TransferabilityGate` API を公開し、LangChain / LlamaIndex への組み込み例を用意する。
3. **評価基盤として継続利用できる仕組みにする**  
   評価split、質問品質、TiDB監査SQL、レポート生成をCLIとCIで再現可能にする。

短期的には、**TransferabilityGate API + TiDB Vector evidence retrieval + Full-text evidence retrieval + reproducible report** が最重要である。

---

## 2. コンテスト上の評価前提

公式テーマは「TiDBで作るAI時代のデータ基盤」。対象は、AIでの情報検索、RAG、AIエージェントのメモリ機能に関する実装知見であり、TiDB Cloud / mem9 利用は加点要素である。

そのため、HandoverGap は以下の見せ方が強い。

- RAGそのものを置き換えるものではなく、**回答前に挟む安全ゲート**である。
- TiDBは単なるVector Storeではなく、**なぜ回答を止めたかを説明できる監査ストア**である。
- SQL、Vector Search、Full-text Search、JSON、Transaction を同一基盤で扱うことで、判断過程を1つのDBから追える。
- PyPI公開済みで、記事だけではなく実装物として持ち帰れる。

---

## 3. 現在の強み

### 3.1 アイデアの強み

HandoverGap のアイデアは、既存RAG評価の「関連するか」「正しいか」から一段ずらし、**Correctness と Transferability を分離**している点が強い。

- Naive RAG: 関連する記憶を返す
- Hybrid RAG: 関連証拠やリスク警告を足す
- HandoverGap RAG: プロファイルと作業文脈ごとの必須スロットを検査し、不足があれば回答を保留する

特に「正しい記憶でも、後任者の責任範囲によっては危ない」という切り口は、AIメモリ運用の事故に踏み込んでいる。

### 3.2 実装・再現性の強み

現時点で次の要素が揃っている。

- Zenn記事
- GitHubリポジトリ
- PyPIパッケージ
- CLI
- Streamlitデモ
- TiDB optional dependency
- 同梱データセット
- mini / adversarial / sanitized / holdout などの評価split
- TiDB監査SQL

この時点で「記事だけ」ではなく、触れる成果物になっている。

### 3.3 TiDB活用の強み

記事上では、TiDBの用途を以下のように整理できている。

| TiDB機能 | HandoverGapでの用途 |
|---|---|
| SQL | profile、slot、状態、スコア、assessmentの管理 |
| Vector Search | slotごとの関連証拠検索 |
| Full-text Search | 顧客名、Issue ID、Runbook、固有名詞検索 |
| JSON | Slack、Issue、議事録、CRMなどのメタデータ保持 |
| Transaction | gap、質問、assessmentの一貫更新 |

次に必要なのは、この整理を実装・CLI・READMEでも確認できる形にすること。

---

## 4. 残っている弱点

### 4.1 TiDB Vector / Full-text が実行パスとして弱く見える

記事ではVector Search / Full-text Searchの意味が説明されているが、審査員がGitHubを見ると、実際にslot evidence retrievalとして動いている証拠がもっと欲しくなる。

改善方針:

- `memory_chunks.embedding` にembeddingを保存する
- slotごとの検索意図を生成する
- TiDB Vector Searchでtop-k evidenceを取る
- Full-text Searchで顧客名・Issue ID・Runbookなどを拾う
- merge / rerank した結果を `slot_fill_attempts` に保存する
- 最後に `transfer_assessments` から監査SQLで追えるようにする

### 4.2 PyPIライブラリとしての入口がまだ「検出器を呼ぶ」寄り

実利用者が欲しいのは、既存RAGに挟める小さなAPIである。

改善方針:

```python
from handovergap import TransferabilityGate, TiDBAuditStore

gate = TransferabilityGate(
    profile="support",
    audit_store=TiDBAuditStore.from_env(),
)

result = gate.check(
    memory="A社は今回だけCSVで対応し、APIは次フェーズにする",
    profile="CS",
    evidence=[
        {"title": "Slack: CSV fallback agreement", "text": "..."},
        {"title": "Issue: API integration postponed", "text": "..."},
    ],
)

if result.transferability_status != "transferable":
    return {
        "status": "needs_clarification",
        "questions": result.questions,
    }

return rag.generate_answer(memory)
```

これにより、HandoverGapは「RAGを置き換えるもの」ではなく、**RAG回答前のTransferability Gate**として説明できる。

### 4.3 質問品質の評価が弱い

HandoverGapの一番おいしい価値は「答えずに聞き返す」こと。したがって、質問品質を測る指標が必要。

追加すべき指標:

| 指標 | 意味 |
|---|---|
| Question Slot Coverage | 必要slotに質問できたか |
| Question Semantic Coverage | gold questionと意味的に対応しているか |
| Question Actionability | 誰が何を答えればよいか明確か |
| Redundancy Rate | 同じ意味の質問を重複していないか |
| False Clarification Rate | 不要な質問を出していないか |

---

## 5. 受賞確率を最大化するP0打ち手

### P0-1. `TransferabilityGate` API を公開する

目的:

- 既存RAGに挟める形を明確にする
- PyPIライブラリとしての実用感を上げる
- README冒頭で価値を一瞬で伝える

最小API:

```python
from handovergap import TransferabilityGate

gate = TransferabilityGate()
result = gate.check(
    memory=memory,
    profile="CS",
    task_context="Answer customer questions about the workaround.",
    evidence=evidence,
    provided_slots=["scope"],
    evidence_slots=["scope"],
)
```

Done条件:

- `TransferabilityGate` がpublic APIとしてimportできる
- `result.transferability_status`, `result.questions`, `result.gaps` が使える
- READMEに10行以内の利用例がある
- テストがある

---

### P0-2. TiDB Vector Search evidence retrieval を実装する

目的:

- 「TiDBを使っただけ」批判を潰す
- slot単位の証拠検索というHandoverGap固有の価値を見せる

実装済みCLI:

```bash
handovergap retrieve-evidence \
  --scenario S001 \
  --profile CS \
  --slot communication_status \
  --top-k 3
```

このCLIは初回利用向けのdeterministic local vector pathです。Live TiDB pathは `TiDBStore.persist_memory_chunks(...)` と `TiDBStore.retrieve_memory_chunks_by_vector(...)` で提供する。

出力イメージ:

```text
Slot: communication_status
Search hints:
- 顧客に説明済み
- 合意済み
- API延期
- CSV暫定対応

Top evidence:
1. Slack: CSV fallback agreement        score=0.86
2. CRM: Customer notification memo      score=0.81
3. Issue: API integration postponed     score=0.74

Selected evidence:
- CRM: Customer notification memo

Audit:
slot_fill_attempt_id=...
selected_event_id=...
```

Done条件:

- [x] `memory_chunks.embedding VECTOR(1536)` に保存できる
- [x] TiDB Vector Search SQLでtop-k evidenceを取れる
- [x] local dry-run CLIでslot-level retrievalを確認できる
- [x] `slot_fill_attempts.retrieved_event_ids` に保存するIDをCLIで確認できる
- [x] 監査SQLからslot-fill evidenceを参照できる
- [ ] Live TiDBでp50 / p95 latencyを出せる

---

### P0-3. Full-text Search evidence retrieval を実装する

目的:

- 顧客名、Issue ID、Runbook、固有名詞を拾う
- Vector Searchだけでは拾いづらい業務引き継ぎ情報を補完する

実装済みCLI:

```bash
handovergap retrieve-evidence \
  --scenario S002 \
  --profile Engineer \
  --slot related_issue \
  --mode hybrid
```

Done条件:

- [x] Vector candidates と Full-text candidates を別々に取得できる
- [x] RRFで統合できる
- [x] TiDB Full-text SQL pathを実装した
- [x] local dry-run CLIで `--mode vector/fulltext/hybrid` を確認できる
- [ ] Live TiDB audit trailへhybrid結果を永続化してp50/p95を出す

---

### P0-4. 再現可能な評価レポートを生成する

目的:

- 記事本文の評価をGitHub上で再現可能にする
- 審査員に「評価基盤」として見せる

実装済みCLI:

```bash
handovergap report --dataset all --output reports/evaluation-latest.md
```

レポートに含めるもの:

- mini / adversarial / sanitized / holdout の結果
- Naive / Hybrid / HandoverGap 比較
- Question Coverage
- TiDB audit query latency（live検証時）
- TiDB Vector / Full-text retrieval latency（live検証時）
- limitations

Done条件:

- [x] markdown report CLIがある
- [x] mini / adversarial / sanitized / holdout の結果を生成できる
- [x] Naive / Hybrid / HandoverGap 比較を含む
- [x] Evaluation Integrity sectionを含む
- [x] READMEに生成コマンドがある
- [ ] `reports/evaluation-latest.md` をCIで生成または検証する
- [ ] live TiDB latencyを任意セクションとして取り込む

---

## 6. 実用ライブラリとしての仕組み

### 6.1 全体アーキテクチャ

```text
Connectors / JSONL / Manual input
        ↓
SourceEvent normalization
        ↓
PII redaction / metadata normalization
        ↓
Chunking + Embedding
        ↓
TiDB source_events / memory_chunks
        ↓
Slot-level evidence retrieval
  - Vector Search
  - Full-text Search
  - SQL filters
        ↓
Slot Filling
  - Rule-based
  - LLM-based
  - Hybrid
        ↓
Transferability Policy
        ↓
Clarification Questions
        ↓
Audit Trail in TiDB
```

### 6.2 Ingest

まずはJSONLでよい。Slack / GitHub Issues / Notion / CRM はあとでAdapterにする。

```json
{
  "source_type": "slack",
  "title": "A社 API延期の説明",
  "content": "顧客にはCSV暫定対応を説明済み...",
  "actor_name": "support-lead",
  "project_name": "fictional-support",
  "occurred_at": "2026-06-01T09:00:00Z",
  "metadata": {
    "channel": "customer-support",
    "thread_ts": "..."
  }
}
```

CLI:

```bash
handovergap ingest examples/source_events/customer_escalation.jsonl \
  --memory "Use CSV for this release; API support is deferred." \
  --profile CS \
  --task-context "Answer customer questions about the workaround."
```

Done:

- [x] JSONL source event schema
- [x] Slack / Issue / CRM-style synthetic example
- [x] CLI ingest command
- [x] direct integrations deferred

### 6.3 Evidence Retrieval

通常のRAGは質問全体で検索する。HandoverGapは **slot単位で検索する**。

```text
required_slot = communication_status
  ↓
slot search hints生成
  ↓
Vector Search
  ↓
Full-text Search
  ↓
SQL metadata filters
  ↓
merge / rerank
  ↓
selected evidence
```

### 6.4 Slot Filling

```python
SlotFillResult(
    slot_name="communication_status",
    status="filled",
    confidence=0.84,
    value="顧客にはAPI延期を説明済み",
    evidence_ids=["evt_001", "evt_009"],
)
```

Rule-based / LLM-based / Hybrid の3系統を用意する。

### 6.5 Transferability Policy

YAMLで業務ルールを外出しする。

```yaml
name: support_handover
required_slots:
  communication_status:
    severity: high
    question: 顧客にはこの方針を説明済みですか？
  authority:
    severity: high
    question: このプロファイルが顧客向けに回答してよい範囲はどこまでですか？
  fallback_plan:
    severity: medium
    question: 失敗時の代替手段は何ですか？

blocking_policy:
  block_if_missing:
    - communication_status
    - authority
```

### 6.6 Question Generation

```python
ClarificationQuestion(
    slot_name="authority",
    question="このプロファイルが顧客向けに次フェーズ時期を回答してよい範囲はどこまでですか？",
    ask_to="project_owner",
    priority="high",
)
```

---

## 7. PyPIライブラリとしてのロードマップ

### v0.2: Contest Edition

目的: 受賞確率を最大化する。

入れるもの:

- `TransferabilityGate`
- TiDB Vector evidence retrieval
- TiDB Full-text evidence retrieval
- `handovergap retrieve-evidence`
- `handovergap report`
- README冒頭の比較GIFまたは比較表
- `examples/langchain_gate.py`
- GitHub Issues roadmap

READMEの看板文句:

> HandoverGap is not another RAG retriever. It is a transferability gate you can place before your RAG answer.

### v0.3: Usable Library Edition

目的: 既存RAGに組み込める状態にする。

入れるもの:

- YAML RoleProfile
- JSONL ingest
- SQLite / JSONL audit store
- TiDBAuditStore安定化
- OpenAI slot filler
- RuleBased slot filler
- LangChain integration
- LlamaIndex integration
- evaluation report JSON / Markdown

### v0.4: Practical Handover Evaluation Edition

目的: 評価基盤として使える状態にする。

入れるもの:

- question semantic evaluator
- independent annotation workflow
- Label Studio export/import
- inter-annotator agreement
- false clarification analysis
- dashboard
- CI evaluation regression

CLI例:

```bash
handovergap annotate export --dataset sanitized
handovergap annotate import labels.jsonl
handovergap evaluate --with-labels labels.jsonl
handovergap report --format html
```

### v1.0: Production Gate Edition

目的: 実運用導入できる品質にする。

必要条件:

- Stable public API
- SemVer運用
- migration管理
- async対応
- structured logging
- OpenTelemetry
- PII redaction
- secrets handling
- retry / timeout
- security policy
- changelog
- PyPI Trusted Publishing

---

## 8. GitHub Issuesとして作るべきバックログ

そのままIssue化できるタイトル:

1. `[Contest] Add TransferabilityGate public API`
2. `[Contest] Add TiDB vector evidence retrieval for slot-level search`
3. `[Contest] Add TiDB full-text evidence lookup for IDs and named entities`
4. `[Contest] Add reproducible evaluation report generator`
5. `[Contest] Add LangChain integration example`
6. `[Contest] Add README comparison GIF: Naive answers vs HandoverGap asks`
7. `[Library] Add YAML-based custom profile presets`
8. `[Library] Add JSONL ingest format for Slack/Issue/CRM-style records` `[implemented]`
9. `[Library] Add semantic question quality evaluator` `[implemented deterministic rubric]`
10. `[Library] Add TiDB benchmark with generated 1k scenario dataset`
11. `[Ops] Enable PyPI Trusted Publishing`
12. `[Docs] Add production adoption guide and limitations`

Issueテンプレート:

```md
## Goal

Make HandoverGap usable as a transferability gate in existing RAG systems.

## Why

The Zenn article argues that correct memories are not always transferable.
This issue turns that thesis into a reusable library feature.

## Scope

- ...

## Done

- [x] CLI added
- [x] Python API added
- [x] Test added
- [x] README example added
- [ ] Article note updated if needed
```

---

## 9. README / 記事で改善すべき見せ方

### 9.1 README冒頭

最初の5秒で次を見せる。

```md
## Naive RAG answers. HandoverGap asks first.

| Naive RAG | HandoverGap RAG |
|---|---|
| A社はCSV対応、APIは次フェーズです | 顧客説明済みか不明です。回答前に確認してください |
```

可能ならGIFを置く。

- 左: Naive RAGが即答
- 右: HandoverGapが不足slotを出して質問
- 下: TiDB audit SQLで「なぜ止めたか」を表示

### 9.2 記事末尾に足す短い追記

記事を長くしすぎない。末尾にこれだけ足す。

```md
## ライブラリとして実利用へ寄せるために

記事公開後、リポジトリ側では HandoverGap を既存RAGの前段に挟める `TransferabilityGate` として整理し始めています。

今後は、slotごとの証拠検索をTiDB Vector Search / Full-text Searchで実行し、取得した証拠、slot filling、gap、確認質問、transfer assessmentを同じTiDB上で追える形へ広げます。

つまり、HandoverGapはRAG本体を置き換えるものではなく、RAGが答える直前に「この記憶を特定プロファイルと作業文脈で使ってよいか」を検査する小さなゲートとして使う想定です。
```

---

## 10. 最短実行順序

まずは次の順番。

1. `TransferabilityGate` API
2. TiDB Vector Searchでslot evidence retrieval
3. TiDB Full-text Searchで固有名詞 evidence retrieval
4. 評価レポート自動生成
5. README冒頭比較GIF / 比較表
6. LangChain example
7. YAML profile
8. semantic question evaluator
9. TiDB大きめベンチ
10. Trusted Publishing / docs / changelog

### 48時間以内にやるなら

| 優先 | 作業 | 成果物 |
|---|---|---|
| S | TransferabilityGate API | READMEに10行利用例 |
| S | TiDB retrieve-evidence CLI | Vector / Full-text の実行結果 |
| S | report generator | `reports/evaluation-latest.md` |
| A | README比較表 | 価値が一瞬で伝わる |
| A | GitHub Issues作成 | 継続開発ロードマップ |

---

## 11. 最終メッセージ

HandoverGap の勝ち筋は、**「RAGに検索精度ではなく、プロファイル条件付きの文脈準備度判定を足した」**こと。

さらによくするために、記事をさらに説明過多にするのではなく、GitHub / PyPIで次を証明する。

- 既存RAGに挟める
- TiDB Vector / Full-text / SQL / JSON / Transaction を実行パスとして使っている
- なぜ回答を止めたかを監査できる
- 評価レポートを再現できる
- PyPIライブラリとしてロードマップがある

最終的に目指す説明はこれ。

> これは単なるTiDBデモではない。既存RAGに組み込める「文脈準備度ゲート」であり、TiDBはその判断過程を検索・保存・監査するAIデータ基盤である。

---

## 参考リンク

- Zenn記事: https://zenn.dev/m2lab/articles/handovergap-rag-tidb
- GitHub: https://github.com/masanori0209/handovergap
- PyPI: https://pypi.org/project/handovergap/
- Zennfes TiDBコンテスト: https://zenn.dev/contests/zennfes-spring-2026-tidb

# 記事の推敲に yomiyasu を使う

記事の新規作成と大きな改稿では、下書きができた後に [.agents/skills/yomiyasu/SKILL.md](../.agents/skills/yomiyasu/SKILL.md) を読み、技術記事用の [tech.md](../.agents/skills/yomiyasu/references/domains/tech.md) を参照して推敲する。既存の記事を一括で書き換えず、今回依頼された原稿を対象にする。日常の会話やすべての応答への自動適用はしない。その他の文章には本人が推敲を求めた場合に使う。

## 下書きから検証まで

1. 推敲前の原稿を作業環境の一時ディレクトリに UTF-8 で保存する。Git に未保存の下書きも含め、推敲の直前の版を比較元にする。公開リポジトリに私的原稿・推敲前コピー・検査レポートを追加しない。
2. スキルの意味保持の原則に従って推敲する。文書の目的と段落の論点を確認し、専門用語、引用、本人の語り口を文脈に合わせて残す。元にない体験・結果・理由・責任主体を補わない。
3. 同梱 lint を通常モードで実行し、見直し候補を判断する。スコアは正しさや意味保持の保証ではない。100 点や指摘ゼロを必須にせず、通常の執筆フローでは `--strict` を使わない。警告を消すためだけに書き換えない。
4. 同梱 diff と通常の差分で推敲前後を読み比べる。diff は候補を絞るための補助であり、数字だけの変更やコードの変更を必ず検出するものではない。コード・コマンド・識別子・URL、YAML と front matter、数値と単位、前提・条件・例外・否定、責任主体、時制、断定・推量の強さ、主張の比重を原文と直接照合する。意味を変える修正が必要なら、推敲とは区別して根拠と変更意図を確認する。
5. 原稿には本文だけを保存し、スキルが提示する変更理由や確認事項は作業報告へ置く。既存の Zenn プレビュー、差分、出典、公開範囲の確認を終える。未解決の候補と未実施の検査は報告する。

推敲の際は上流の実行回数の制限も守る。lint の修正試行は最大 2 回、diff に基づく修正は 1 回とし、スコアを理由に往復し続けない。Python が使えない環境では、同じ観点で原文と目視照合し、スクリプトを実行できなかったことを報告する。

## 実行コマンド

Python 3.10 以上を使う。以下はリポジトリのルートからの例。Linux / Codex Cloud では `python3`、Windows でその名前が使えない場合は `python` を使う。スキルの相対参照はスキルディレクトリを基準に読み、別ディレクトリから実行する場合はスクリプトと原稿の絶対パスを渡す。

```bash
python3 -B .agents/skills/yomiyasu/scripts/yomiyasu_lint.py articles/<slug>.md
python3 -B .agents/skills/yomiyasu/scripts/yomiyasu_diff.py <推敲前原稿のパス> articles/<slug>.md --stance=説明
```

`--stance` は原稿の主たる立場に合わせて `勧め`・`決まり`・`説明` から選び、決めきれなければ省略する。必要なら `--json` で候補を構造化して確認できる。これらは原稿を読み、標準出力へ結果を出す。原稿への自動修正や外部 API の呼び出しは行わない。

## 固定版と配布元

[nanaism/yomiyasu v1.1.1](https://github.com/nanaism/yomiyasu/tree/373356eb874af5184962c88e925ea7eb58450318)（2026-10-09、commit `373356eb874af5184962c88e925ea7eb58450318`）の `skills/yomiyasu` を、公式 skill-installer の `--ref` と `--dest .agents/skills` で取得した。

配布スキルの 14 ファイルは改変せず、上流の 3 回帰テストをスキル配下の `tests/` に追加した。スキル、参照資料、Python 検査、画像、[MIT LICENSE](../.agents/skills/yomiyasu/LICENSE)、[Unicode License V3](../.agents/skills/yomiyasu/UNICODE-LICENSE.txt) を同梱している。[配布元・版・各ファイルの Git blob SHA-1](../.agents/yomiyasu-upstream.json) を記録した。`.gitattributes` で同梱ファイルのバイト列を保つ。

Codex はリポジトリ内の `.agents/skills` からスキルを読み込む。Codex Cloud でもこのブランチを checkout すれば同じファイルを使える。実行時の download、latest の追従、グローバルスキル、新しい認証、pip install は不要。更新時は明示的に版を選び、配布元・差分・ライセンスと検証結果を見直す。

## 導入のオフライン検証

```bash
python3 -B scripts/verify_yomiyasu.py
python3 -B .agents/skills/yomiyasu/scripts/yomiyasu_lint.py tests/yomiyasu/before.md --json
python3 -B .agents/skills/yomiyasu/scripts/yomiyasu_diff.py tests/yomiyasu/before.md tests/yomiyasu/after.md --stance=説明 --json
git diff --check
```

`verify_yomiyasu.py` は固定版のバイト列、相対参照、依存、別の作業ディレクトリと空白を含むパスでの CLI、日本語入出力、上流の Markdown・入出力・ダッシュ回帰テストを確認する。スコアを合否基準にはしない。サンプルは公開可能な架空の原稿で、`articles/`・`books/` の外に置いている。検証成功は配布物と検査ツールの動作確認であり、実際の記事の内容・意味保持・Zenn 表示の保証ではない。

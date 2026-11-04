# 記事ストック自動補充 手順書（REFILL）

ブログ下書き在庫（JA: `blog/_drafts/`, EN: `en/blog/_drafts/`）が少なくなったら、
この手順で**実記事**を補充する。公開パイプライン（1日3本・キャッチアップ）は既存のまま。
テンプレ量産ではなく、毎回ちゃんと役立つ本文を書くこと。

## 0. 前提
- repo: `jplabdiamond-jpg/free-bizdocs`（Mac: `~/seikyu-hub-demo`）
- 本文の体裁・OG・公開は自動。**本文の執筆だけ**が人（Claude）の仕事。
- まず `git pull --ff-only origin main`。

## 1. 在庫チェック
```
ls blog/_drafts/*.html 2>/dev/null | wc -l          # JA 残り
ls en/blog/_drafts/*.html 2>/dev/null | wc -l        # EN 残り
```
目安: どちらかが **9本（3日分）未満**なら、約1週間分（各15〜20本）まで補充。
十分あれば何もしない。

## 2. 日本語の補充
CSV `blog/eyecatch_titles.csv` に未執筆の見出しが計画済み（status=未 かつ `_drafts` に本文なしの行）。
次に書くべきslugを確認:
```
awk -F',' 'NR>1 && $6=="未"{print $1"|"$2"|"$4}' blog/eyecatch_titles.csv | while IFS='|' read p c s; do [ -f blog/_drafts/$s.html ] || echo "$p $c $s"; done | head -20
```
- 各記事を `scripts/content/ja_partX.py` の `ARTICLES` リスト形式で執筆（下の「記事データ形式」参照）。
- `scripts/content/ja_data.py` で各 part を集約（`ARTICLES = ja_part1.ARTICLES + ...`）。
- 生成: `cd scripts/content && python3 gen_ja.py ../../blog/_drafts`
  - CSVのcategory文字列を `cat` に正確に入れる（アイキャッチのPRESET/背景に使う）。
  - アイキャッチ画像は**公開時に自動生成**されるので下書き段階では不要。
- 新カテゴリが出たら `scripts/gen-eyecatch.py` の PRESET / SUBJECT に1行追加。

## 3. 英語の補充
ENにはCSV計画がないので、**6カテゴリ**（Invoicing / Getting paid / Quoting / Tax / Purchasing / Industries）
をバランスよく、既存slugと重複しない話題を選ぶ。既存一覧:
```
ls en/blog/*.html en/blog/_drafts/*.html | xargs -n1 basename | sed 's/\.html//' | sort
```
- 各記事を `scripts/content/en_partX.py` に執筆、`en_data.py` で集約。
- 下書き生成: `cd scripts/content && python3 gen_en.py ../../en/blog/_drafts`
- OG画像生成: `cd scripts/content && python3 gen_en_og.py ../../en/blog/og`
  - Pollinations（無料・キーなし）でハイパーリアル写真を取得。稀に402（レート制限）が出るが、
    その場合は合成背景にフォールバックするか、少し待って未生成slugだけ再実行する。
  - **EN記事はOG画像必須**（一覧カード・OGに使用）。12本なら12枚そろえること。
- `tag=` は必ず上記6カテゴリのいずれか（publish-en.mjs の輪番がこの名前を使う）。

## 4. 検証 → commit → push
```
# JAドラフトにCSVの未行が対応しているか / ENタグが6カテゴリか / JSON-LDが壊れてないか を確認
git add -A
git commit  # 末尾に下記フッターを付ける
git push origin main
```
コミットのフッター（必須）:
```
Co-Authored-By: Claude Opus 4.8 <noreply@anthropic.com>
```
変更するのは `_drafts/` と `en/blog/og/*.jpg` と（必要時）`gen-eyecatch.py` のみ。
`blog.html` / `sitemap.xml` / CSVのstatusは**公開時に**自動更新されるので触らない。

## 記事データ形式（JA）
```python
{
 "slug":"...", "tag":"退職", "cat":"退職",         # cat=CSVのcategory
 "title":"フルタイトル｜サブ",                      # h1・titleタグ
 "cardh2":"一覧カード用の短いタイトル",
 "carddesc":"カード/OG用の短い要約（〜60字）",
 "metadesc":"meta description（やや長め）",
 "emph":"強調語", "emphcolor":"#ff5a78", "en":"English subtitle",  # アイキャッチ装飾（任意）
 "font":"serif",                                    # 任意（履歴書系はserif）
 "lead":"リード文（HTML可、<strong>可）",
 "sections":[{"h2":"見出し","html":"<p>...</p>"}, ...],
 "faq":[{"q":"質問","a":"回答（プレーン文）"}, ...],
 "related":[{"href":"/taishoku","label":"退職届を無料作成"}, ...],
 "cta_href":"/taishoku", "cta_label":"無料で作成する（登録不要）",
 "tool_line":"末尾CTAセクションの説明文（任意）",
}
```
## 記事データ形式（EN）
JAとほぼ同じ＋OG画像用フィールド:
```python
{
 "slug":"...", "tag":"Quoting",                      # 6カテゴリのいずれか
 "c1":"#3730a3", "c2":"#6366f1",                     # OGの配色（ラベル/アクセント）
 "oglabel":"Quoting", "ogline1":"What to Include", "ogline2":"in a Quote",
 "ogtag":"free quotes, no sign-up", "subject":"OG背景のPollinationsプロンプト",
 "title":"...", "ogtitle":"短縮タイトル", "cardh2":"...", "carddesc":"...", "desc":"meta",
 "lead":"...", "sections":[...], "faq":[...], "related":[...],
 "cta_href":"/en/estimate", "cta_label":"Create a quote free",
 "note":"任意の注意書き（税務免責など）",
}
```
カテゴリ別のOG配色の目安: Invoicing=#0e7490/#2bb3c0, Getting paid=#15803d/#22c55e,
Quoting=#3730a3/#6366f1, Tax=#b45309/#f59e0b, Purchasing=#6d28d9/#a78bfa, Industries=#9f1239/#fb7185。

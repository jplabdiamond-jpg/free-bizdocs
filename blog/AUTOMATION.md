# Free BizDoc ブログ 運用手順（画像バンク事前取得＋1日3記事公開）

このファイルは運用手順書。スケジュール実行時も手動実行時も、この手順に従う。
作業ディレクトリ: ~/seikyu-hub-demo（device_bash/Desktop Commander の認証済みシェル）。

## 基本方針（2つのプロセスに分離）

運用は「画像ストック（事前・ユーザー提供）」と「記事公開」の2プロセスに分ける。

- **プロセスA：画像ストック（事前）** … 画像は**ユーザーがまとめてzipで提供**する（番号＋英語名、2560×1440 PNG）。これを**スラッグ名で `blog/img-src/<slug>.png` に原本保存**する（`blog/img-src/` は .assetsignore で非公開）。※Manus生成は使わない（必要時のフォールバックのみ）。
- **プロセスB：記事公開** … 1日3記事。**公開時刻はランダム分散・各2時間以上あける**。公開時に `blog/img-src/<slug>.png` を **webp変換**して `blog/img/<slug>.webp` を生成し、記事はこれを参照する（`cwebp -q 82 in.png -o out.webp`）。公開する記事は**必ず img-src に原本があること**。
  - 画像参照はすべて **`/blog/img/<slug>.webp`**（本文アイキャッチ・og:image・twitter:image・一覧カード）。
  - **注意**：デプロイ直後に素の webp URL を curl で叩かない（伝播前だと404(HTML)がエッジに30日キャッシュされる）。確認は `?v=` 付きで行うか、万一キャッシュされたら参照URLに `?v=1` を付けて再デプロイして回避する。

## 鉄則

- **画像なし公開は禁止。** 公開対象を選ぶ前に、必ず `blog/img/<slug>.png` の存在を確認する。画像が無い記事は公開しない（画像バンク待ちにする）。
- **公開は1日3記事まで。** 3記事の公開時刻はバラす（ランダム。例: 午前・午後・夜など重ならないように）。
- **画像は先行してまとめて貯める。** クレジットは毎日回復するので、Mac起動中に先行取得しておけば、公開時にクレジット不足で詰まらない。
- ファイル作成・編集はMacのマウントに Edit/Write で書けないため、必ず device_bash 経由（cat> / sed -i / python / cp）で行う。

---

# プロセスA：画像バンク（事前取得）

### 対象の選び方
- `blog/eyecatch_titles.csv` の status が「未」**かつ** `blog/img/<slug>.png` が**まだ存在しない**行を、priority 昇順で選ぶ。
- 既に `blog/img/<slug>.png` がある行は生成しない（再利用＝二重生成しない）。

### Manus操作ルール（重要）
- Manus操作には **ユーザーのChromeでManus(https://manus.im)にログイン済み＋そのタブに接続できること** が必須。
- **【必須】プロンプト入力前に、必ずManusのページを一度リロードする**（`https://manus.im/app` に移動）。リロードせず送信すると「インターネット接続を確認してから、もう一度お試しください。」のエラーで止まり、再試行しても繰り返し失敗する。リロード直後に新規タスクへ貼り付けると安定して開始できる。
- 番号は**全角（１．２．３．…）**で入力する。半角「1. 」はManusの自動リスト整形で番号が二重化（例: 2. 2.）するため避ける。
- **1会話で最大10タイトル**までまとめてOK（コスト目安 ≒ 15クレジット/枚。Manusが文字欠け等を自動で再生成することがあり、その分も消費する）。残クレジットに応じて枚数を決める。
- **クレジットが尽きるまで**バッチを繰り返してよい。

### プロンプト（全角番号で列挙＋共通指示）
```
１．<TITLE1>
２．<TITLE2>
…（最大10件）

上記◯個のブログ記事タイトルについて、アイキャッチ画像を1枚ずつ合計◯枚、2560×1440px（16:9横長）で作成してください。各タイトルの文言はそのまま画像内に正確な日本語で大きく入れてください（文字化け厳禁）。右下に小さく free-bizdocs.com。背景はタイトル内容を連想させるハイパーリアルで明るい写真調。note記事のサムネイルのように派手で目を引くデザイン。文字の配置・サイズ・色などの細かい指定はせずお任せします。過去に生成した画像とは必ず異なる描写・構図・配色・レイアウトにしてください。
```

### ダウンロード→配置
- 生成完了（「タスクが完了しました」）まで待つ。複数枚のときは **ZIP一括ダウンロード**が速い（無ければ「7枚をZIPにまとめて」等と依頼するとZIP化してくれる。ファイル名は 01〜 連番＋英語名を指定）。
- ZIPを `~/Downloads` に落とし、専用ディレクトリに展開 → 各PNGを `cp` で `~/seikyu-hub-demo/blog/img/<slug>.png` に配置。**番号順＝送信したタイトル順**なので取り違えないこと。
- 各画像の寸法が **2560×1440** であることを `sips -g pixelWidth -g pixelHeight` で確認。
- 配置した時点では CSV は **「未」のまま**（まだ公開していないため status は変えない）。公開可否は「画像が存在するか」で判断する。

---

# プロセスB：記事公開（1日3記事・ランダム時刻）

### 実行方式（確定：方式A＋2時間間隔）
- **セッションが接続中（Mac接続あり）に公開する**（事前の時刻固定スケジュールはしない）。
- **絶対に3記事をまとめて公開しない。1記事ずつ公開する。**
- **各公開の間隔は必ず2時間以上あける**（1本公開 → 2時間以上あけて次の1本 → さらに2時間以上あけて3本目）。間隔は send_later / ScheduleWakeup で自分を起こして確保する。
- 起床時にMac未接続なら公開を保留し、次に接続できた時に公開する（**直前の公開から2時間以上**あいていることを確認してから）。画像なし・Mac未接続での公開はしない。
- 1日の公開上限は3記事。その日3本公開済みなら、その日はそれ以上公開しない。

### 公開対象の選び方
- `blog/eyecatch_titles.csv` の status「未」**かつ** `blog/img/<slug>.png` が**存在する**行（＝画像バンク済み）を、priority 昇順で**3件**。
- 画像が無い行は**スキップ**（公開しない）。画像のある行だけを公開対象にする。
- **1日3記事まで**。上の実行方式のとおり1記事ずつ・各2時間以上あけて公開する（まとめて3本は禁止）。

### 1. SEO/AEO記事HTMLの作成
- テンプレートは最新記事（例 blog/invoice-send-manner.html）を読み、同じ構成に倣う:
  `/landing.css?v=...` 読み込み、ヘッダー、パンくず、見出し（h1/h2）、本文、FAQ、関連リンク、フッター。
  構造化データ JSON-LD は Article / BreadcrumbList / HowTo（手順系の場合）/ FAQPage を入れる（可視HTMLの質問文とFAQPageのnameを完全一致させる）。
- 本文は検索意図に答える本格的な日本語（2000〜3500字目安）。断定しすぎず正確に。税・法律は一般論として書き、最終判断は専門家/公式へ誘導。
- 冒頭（h1直後）にアイキャッチを挿入:
  `<figure class="eyecatch"><img src="/blog/img/<slug>.png" alt="<TITLE>" width="1200" height="675" loading="eager"></figure>`
- 内部リンク: 対応ツールページ(tool_page列)と関連既存記事へ発リンク。canonical/og:url は拡張子なし実URL（https://free-bizdocs.com/blog/<slug>）。
- 保存先: blog/<slug>.html

### 2. 一覧・サイトマップ登録
- blog.html の記事一覧の**先頭**に新カードを追加（最新が上）。カードは**必ず先頭にサムネイル画像**を入れる（画像なしカードは作らない）:
```
<a class="bcard" href="/blog/<slug>"><img class="th" src="/blog/img/<slug>.png" alt="" loading="lazy" width="400" height="225"><span class="tag"><カテゴリ></span><h2><一覧用タイトル></h2><p><要約1〜2文>…</p></a>
```
  - サムネは必ず `/blog/img/<slug>.png`。CSSは blog.html に導入済み（`.bcard{overflow:hidden}` と `.bcard .th{…}`）。
- sitemap.xml に `<url><loc>https://free-bizdocs.com/blog/<slug></loc><lastmod>YYYY-MM-DD</lastmod><changefreq>monthly</changefreq><priority>0.7</priority></url>` を追加。

### 3. デプロイ
- `cd ~/seikyu-hub-demo && npx wrangler pages deploy . --project-name=seikyu-hub-demo --commit-dirty=true`
- 本番 https://free-bizdocs.com/blog/<slug> で表示・アイキャッチ・構造化データを確認。
- ※ landing.css / suite.css / promo.js を変更した場合は、全HTMLの `?v=` を新しい値に上げてキャッシュを破棄する（記事公開だけなら不要）。

### 4. IndexNow送信
- キー: a443fe2d01c64cdaa0d1e4a37a44edb3aac13d4e7e36461ab60734c6ac1bb773（キーファイルは公開済み）
```
python3 - <<'PY'
import json,urllib.request
key="a443fe2d01c64cdaa0d1e4a37a44edb3aac13d4e7e36461ab60734c6ac1bb773"
urls=["https://free-bizdocs.com/blog/<slug>","https://free-bizdocs.com/blog"]
p={"host":"free-bizdocs.com","key":key,"keyLocation":f"https://free-bizdocs.com/{key}.txt","urlList":urls}
req=urllib.request.Request("https://api.indexnow.org/indexnow",data=json.dumps(p).encode(),headers={"Content-Type":"application/json; charset=utf-8"})
print(urllib.request.urlopen(req,timeout=30).status)
PY
```

### 5. 後処理
- `blog/eyecatch_titles.csv` の公開した行の status を「未」→「済」に更新（sed等でin-place）。
- 必要ならGSCでURL検査→インデックス登録リクエスト（freebizdoc@gmail.comアカウント。任意）。

---

## 状態の見分け方（まとめ）
- **画像バンク済み・未公開** … status「未」＋ `blog/img/<slug>.png` 存在 → **公開対象**（プロセスB）。
- **画像なし・未公開** … status「未」＋ 画像なし → **画像バンク対象**（プロセスA）。公開はしない。
- **公開済み** … status「済」。

## メモ
- 既存の手書き記事（invoice-how-to, receipt-how-to, taishoku-how-to, rirekisho-motivation, quote-how-to, genzei-keisan, shokumu-how-to）は作成済みで、サムネは /og/*.png を使用。CSVの60本はSEO用の新規記事。
- バンク済み（画像あり・未公開）: 優先度7〜23（invoice-freelance〜quote-discount の17本）。優先度24(quote-document-flow)は画像生成済みだがクレジット枯渇でDL未取得＝再取得待ち。

---

# 【確定】クラウド自動公開（GitHub Actions・Mac非依存）2026-10-19〜

公開はMac・Claudeセッションに非依存で、GitHub Actionsが自動実行する。プロセスBの手動運用は原則不要。

- **リポジトリ**: https://github.com/jplabdiamond-jpg/free-bizdocs （private、ホスティングはCloudflare Pagesに直接デプロイ。GitHubは恒久ソース＋CI）
- **ワークフロー**: `.github/workflows/auto-publish.yml`（cron `*/30 0-13 * * *` = JST 9:00-22:30 / 手動 `workflow_dispatch` mode=force でテスト公開）
- **公開ロジック**: `scripts/publish.mjs`（1回最大1本／1日3本／各2時間以上／ランダム時刻スロットを `blog/publish-state.json` で管理）
- **公開対象**: CSV status「未」 かつ `blog/img-src/<slug>.png` あり かつ `blog/_drafts/<slug>.html` あり。いずれか欠ければスキップ（画像なし・本文なし公開は不可）。
- **公開処理**: cwebp で `img-src/<slug>.png`→`img/<slug>.webp`、本文を `blog/<slug>.html` へ移動（`__PUBDATE__`/`__PUBDATE_JP__` を当日に置換）、blog.html 先頭にカード、sitemap 追加、CSV 済化、状態更新 → Cloudflare本番デプロイ → GitHubへcommit/push → IndexNow送信。
- **Secrets/設定**: `CLOUDFLARE_API_TOKEN`（Pages:Edit）はGitHub Secret。Account ID `7969ecaa0a1b9bacae1861547c2ec3fe` はワークフローに直書き。
- **デプロイ**: `npx wrangler@3 pages deploy . --project-name=seikyu-hub-demo --branch=main`（main=本番）。
- **記事ドラフトの用意（唯一の手作業）**: `blog/_drafts/<slug>.html` を事前作成しておく。先頭に `<!--CARD tag=.. | h2=.. | desc=..-->`、日付は `__PUBDATE__`（YYYY-MM-DD）/`__PUBDATE_JP__`（○年○月○日）プレースホルダ、画像参照は `/blog/img/<slug>.webp`。テンプレは blog/invoice-send-manner.html 等に倣う。
- **画像**: ユーザー提供のPNGを `blog/img-src/<slug>.png`（2560×1440）に置きpush。webp化は公開時に自動。
- **手動テスト**: `gh workflow run auto-publish.yml -f mode=force`。

---

# 【確定】英語ブログ（/en/blog）自動公開 2026-10-19〜

方針: **日本語記事の直訳はしない**。英語圏（米英豪加）向けのトピックで Claude が書き下ろす（例: JA「請求書の書き方」→ EN "How to write an invoice (US/UK/AU/CA)"）。日本固有テーマ（インボイス制度・源泉徴収・履歴書等）は英語側ではスキップ。

- **EN記事は画像不要**。各記事はインラインのグラデーション・ヒーロー（カテゴリ色）。`suite.css` ＋ 共通ヘッダー `en/siteheader-en.js` でENサイトと一体化。
- **一覧**: `/en/blog`（`en/blog.html`）。記事: `/en/blog/<slug>`（`en/blog/<slug>.html`）。
- **生成元**: `build-en-blog.py`。`ARTICLES` に公開済み記事、`DRAFTS` にこれから自動公開する記事を定義。
  - `python3 build-en-blog.py` で ARTICLES の記事HTMLを生成し、`DRAFTS` の各記事を **`en/blog/_drafts/<slug>.html`**（`__PUBDATE__`/`__PUBDATE_EN__` プレースホルダ＋先頭に `<!--ENCARD tag=|h2=|desc=|c1=|c2=-->`）として書き出す。
  - **`en/blog.html`（一覧）は初回のみ生成**。以後は自動公開パイプラインがカードを挿入して維持するので通常は上書きしない（デザイン変更時のみ `python3 build-en-blog.py --force-index`。その場合 ARTICLES に公開済み全記事が入っていること）。
- **自動公開**: `scripts/publish-en.mjs`（JAの `publish.mjs` と独立）。`en/blog/_drafts/` のドラフトを slug 昇順で1本、1日最大3本・各2時間以上・ランダム時刻スロット（状態 `blog/publish-state-en.json`）で公開。公開処理＝日付置換→`en/blog/<slug>.html` へ移動→`en/blog.html` の `#blist` 先頭にカード挿入→sitemap追加。
- **ワークフロー**: `auto-publish.yml` が JA(`publish.mjs`)＋EN(`publish-en.mjs`)を両方実行し、**どちらかが公開したら** Cloudflareデプロイ＋commit/push＋IndexNow（JA/EN両URL）。
- **運用ルール（Claude）**: JA記事を作る／公開運用する際、対応する英語圏向けEN記事を `build-en-blog.py` の `DRAFTS` に追加して `python3 build-en-blog.py` を実行し、`en/blog/_drafts/` にドラフトを用意しておく。あとはパイプラインが自動公開する（＝JA投稿に続いてENも自動で公開される）。公開済みにしたENトピックは次回以降 `ARTICLES` 側へ移してもよい（--force-index で一覧を再生成する場合は必須）。
- **シード済み(2026-10-19)**: how-to-write-an-invoice / estimate-vs-quote / payment-terms-explained / receipt-vs-invoice の4本。

---

# 【追加】JA画像の自動生成（2026-10-23〜）

JAも英語ブログ同様、画像を自動生成して完全自動公開できるようにした。手動バンク画像が無い記事は、公開時に写真調アイキャッチを自動生成する。

- **生成器**: `scripts/gen-eyecatch.py <slug> <title> <category> <out.webp>`。Pollinations(Flux/Turbo・無料APIキー不要)で写真調背景を生成→下部をクロップして透かし除去→日本語タイトル＋カテゴリピル＋free-bizdocs.com を合成→2560×1440 webp出力。失敗時はカテゴリ色グラデにフォールバック。
- **公開ロジック**(`scripts/publish.mjs`): `blog/img-src/<slug>.png` があればそれをwebp化（従来どおり）、無ければ `gen-eyecatch.py` で自動生成。→ **画像は常に用意されるので在庫切れでも画像なし公開にならない**。公開可否は「本文ドラフトの有無」だけで判定。
- **workflow**: `setup-python` ＋ `fonts-noto-cjk` ＋ `pip install pillow` を導入済み。生成は1枚あたり概ね30〜90秒。
- **テスト**: `.github/workflows/test-eyecatch.yml`（手動）でサンプルを生成しartifactに出力。
- 既存の手動バンク画像（〜No.44）はそのまま優先使用される。No.45以降は本文ドラフトを置けば画像も自動で付く。

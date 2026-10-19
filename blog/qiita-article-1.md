## やりたかったこと

個人開発している書類作成ツール [Free BizDoc](https://free-bizdocs.com) で、「作った請求書を相手にURLで共有したい」という機能を足しました。

普通に考えるとサーバーにデータを保存して `example.com/share/{id}` のようなURLを発行する作りになりますが、請求書には取引先名・金額・振込先といった機微な情報が入ります。これをDBに溜めたくなかったので、**サーバーに一切保存せず、URLそのものにデータを載せて共有する**方式にしました。その実装メモです。

## 方針: データは URL のハッシュ部分に載せる

ポイントは URL の **ハッシュ（`#` 以降）はサーバーに送信されない** という性質です。

```
https://free-bizdocs.com/invoice#s=eyJjbGllbnQiOiLmoKrlvI8...
                                 ↑ ここはサーバーに届かない
```

クエリ文字列（`?s=...`）だとアクセスログやリファラに残りますが、ハッシュはブラウザ内で完結します。ここに書類データを base64 で載せれば、サーバーは中身を一切知らないまま共有が成立します。

## 書き出し側

書類オブジェクトを JSON 化 → UTF-8 を保ったまま base64 化します。日本語が入るので `btoa` に直接通すと化けるため、`encodeURIComponent` を一度挟むのが定番です。

```js
function encodeDoc(doc) {
  const json = JSON.stringify(doc);
  // 日本語を含むUTF-8文字列を安全にbase64化
  return btoa(unescape(encodeURIComponent(json)));
}

function createShareUrl(doc) {
  const payload = encodeDoc(doc);
  return `${location.origin}/invoice#s=${payload}`;
}
```

共有リンクに含めないものを決めておくのも大事です。ロゴ画像や印影（dataURL）をそのまま載せると URL が数十KBに膨らむので、共有データからは除外しました。

```js
function toShareDoc(doc) {
  const { logo, stamp, ...rest } = doc; // 画像系は落とす
  return rest;
}
```

## 読み取り側

ページ読み込み時にハッシュを見て、`#s=` があれば共有ビューとして描画します。

```js
function decodeDoc(payload) {
  const json = decodeURIComponent(escape(atob(payload)));
  return JSON.parse(json);
}

window.addEventListener('DOMContentLoaded', () => {
  const m = location.hash.match(/^#s=(.+)$/);
  if (!m) return; // 通常の作成画面

  let doc;
  try {
    doc = decodeDoc(m[1]);
  } catch (e) {
    return; // 壊れたリンクは通常画面にフォールバック
  }
  renderSharedView(doc);
});
```

`renderSharedView` では、
- 編集UIを隠して読み取り専用にする
- 上部に「金額・振込先・支払期限」の入金導線パネルを出す
- PDFダウンロードと「自分も無料で作る」CTAだけ残す

という最小構成にしています。受け取った人はログインも登録も不要で、開いた瞬間に中身が見えます。

## この方式のメリット・デメリット

### メリット

- **サーバーにデータを保存しない**。漏洩リスクの対象がそもそも存在しない
- **DBもストレージも不要**。共有機能のためのインフラコストがゼロ
- **リンクが失効しない**。保存期限の管理が要らず、相手がいつ開いても見られる
- アクセスログやリファラに書類内容が残らない

### デメリット

- **URL が長い**。明細が増えるほど伸びる。QRコードにするなら明細数に上限を設けるなどの工夫が要る
- **後から中身を更新できない**。URL＝データなので、修正したら新しいリンクを発行する前提になる
- **閲覧数などの計測ができない**。サーバーを経由しないので当然ログも取れない
- URLを知っている人は誰でも見られる（限定共有には不向き。社外秘の強い書類には使わない）

用途が「請求書を相手に1回送って見てもらう」なら、デメリットはほぼ問題になりませんでした。逆に「社内で長期管理する」「アクセス制御したい」なら素直にサーバー保存にすべきです。

## 補足: URLが長すぎる場合

base64 は元データの約1.33倍になります。明細が多い請求書だとURLが数KBになり、一部のチャットツールやメーラーで途中で切れることがあります。対策として：

- 共有データのキー名を短縮する（`clientName` → `cn` などの圧縮辞書を持つ）
- `JSON` を圧縮してから base64 化する（`pako` で deflate するなど）

Free BizDoc では現状、画像を除外＋キー短縮で実用上問題ない長さに収まっています。圧縮まで入れるとさらに縮みます。

## まとめ

- 共有データを **URLハッシュ（`#`以降）** に base64 で載せると、サーバー保存ゼロで共有機能が作れる
- 日本語は `encodeURIComponent` → `btoa`、復号は `atob` → `decodeURIComponent` の対で扱う
- 画像除外・キー短縮・圧縮で URL 長を現実的に抑える
- 向くのは「1回きりの共有」、向かないのは「長期管理・アクセス制御」

同じように機微な情報を扱う小さなツールを作る人の参考になれば。実際に動いているものは [Free BizDoc](https://free-bizdocs.com) の請求書作成で「共有リンクを作成」から試せます。

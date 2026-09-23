# Zenn contents (public source)

Zenn の記事・本を管理する公開リポジトリです。ここに置いた原稿や画像は、Zenn での `published` 設定に関係なく GitHub で誰でも読めます。非公開の原稿や、有料の本などソースを公開したくないものは、別の private リポジトリで扱います。

## ローカルで使う

Node.js 22.13 以上と pnpm 11.19 以上（11 系）を用意し、リポジトリのルートで実行します。Zenn CLI と `articles/`・`books/` はセットアップ済みです。

```powershell
pnpm install --frozen-lockfile
pnpm exec zenn preview
```

プレビューは通常 <http://localhost:8000> で開けます。

## 原稿を作る

```powershell
pnpm exec zenn new:article --slug public-example-article
pnpm exec zenn new:book --slug public-example-book
```

記事は `articles/<slug>.md`、本は `books/<slug>/config.yaml` とチャプターの Markdown で管理します。記事・本の slug は 12〜50 文字の英小文字・数字・`-`・`_` を使います。記事の front matter と本の `config.yaml` にある `published` が Zenn での公開状態を決めます。CLI が作った値を、最初の push 前に確認してください。

公開前でも GitHub に置いてよい内容なら `published: false` で Zenn 上の下書きとして管理できます。ただし GitHub 上の原稿は公開されたままです。機密情報、他者の非公開情報、認証情報は含めません。

## 更新・公開する

1. 原稿と画像を編集し、`pnpm exec zenn preview` で表示を確認します。
2. タイトル、リンク、画像、公開してよい内容、`published` の値を確認します。本は `config.yaml` のチャプター一覧と順序も確認します。
3. `git diff --check` と差分を確認してコミットし、`main` へ push します。Zenn の[リポジトリ設定](https://zenn.dev/dashboard/deploys?tab=repo_settings)で、デプロイ対象が `main` であることを確認済みです（2026-09-23）。設定を変えた場合は push 先も合わせてください。
4. Zenn の[デプロイ履歴](https://zenn.dev/dashboard/deploys)で同期結果を確認します。`published: true` の記事・本は公開対象です。

ファイル名や本のディレクトリ名に使う slug を変えると、別の投稿として扱われます。Zenn の投稿を削除するときは、GitHub のファイルを消すだけでは足りません。Zenn の投稿管理画面でも削除してください。

現在、PR での下書きデプロイは無効です（2026-09-23）。PR 上の変更はローカルでプレビューし、`main` に反映した後に Zenn のデプロイ結果を確認します。

## 参考

- [Zenn と GitHub の連携・デプロイ](https://zenn.dev/zenn/articles/connect-to-github)
- [Zenn CLI の使い方](https://zenn.dev/zenn/articles/zenn-cli-guide)

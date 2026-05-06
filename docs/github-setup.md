# GitHub セットアップ

ローカルリポジトリは GitHub へ push できる状態です。

## 推奨リポジトリ設定

- Repository name: `cross-subscription-music-timeline`
- Visibility: ポートフォリオ目的なら public。Provider key や app ID の分離が終わるまでは private でもよい。
- Default branch: `main`
- Issues を有効化
- Projects を有効化
- 初回 push 後は PR 経由で merge する運用にする

## リモート設定

```bash
git remote add origin https://github.com/<owner>/cross-subscription-music-timeline.git
git push -u origin main
```

現在の想定リモート:

```bash
https://github.com/shinkai23/cross-subscription-music-timeline.git
```

## 推奨ラベル

- `feature`
- `bug`
- `ios`
- `android`
- `backend`
- `apple-music`
- `spotify`
- `matching`
- `moderation`
- `ai`
- `legal-risk`
- `research`

## 最初に作る Issue

[GitHub バックログ](github-backlog.md) の内容を初期 Issue として登録します。

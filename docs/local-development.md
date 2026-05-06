# ローカル開発

## リポジトリ

標準ブランチは `main` です。

```bash
git status
```

## Backend

Backend には Node.js 22、npm、Docker が必要です。

```bash
docker compose up -d postgres
cd backend/api
cp .env.example .env
npm install
npm run typecheck
npm test
npm run dev
```

ヘルスチェック:

```bash
curl http://127.0.0.1:4000/health
```

## iOS

iOS のソース骨格は `apps/ios/MusicTimelineApp` にあります。

この workspace は Windows 上にあるため、実際の Xcode プロジェクト作成とビルドは macOS で行います。

1. Xcode で新規 iOS App プロジェクトを作成する。
2. target 名を `MusicTimelineApp` にする。
3. `apps/ios/MusicTimelineApp` から Swift ファイルをコピーする。
4. MusicKit capability を追加する。
5. Apple Music 利用目的の説明文を追加する。
6. MusicKit 認可は実機 iPhone で確認する。

## GitHub

GitHub CLI がある環境では CLI から作成できます。ない場合は GitHub Web 上でリポジトリを作成してから push します。

```bash
git remote add origin https://github.com/<owner>/cross-subscription-music-timeline.git
git push -u origin main
```


# ローカル開発手順

## Backend

PostgreSQLを起動する。

```bash
docker compose up -d postgres
```

Backend依存関係を準備する。

```bash
cd backend/api
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

必要に応じて `.env.example` を `.env` にコピーする。`TOKEN_ENCRYPTION_KEY` はローカルMVP用のサンプル値を置いているため、本番や共有環境では必ず差し替える。

migrationを適用する。

```bash
alembic upgrade head
```

APIを起動する。

```bash
uvicorn app.main:app --host 0.0.0.0 --port 4000 --reload
```

確認する。

```bash
curl http://127.0.0.1:4000/health
```

## iOS

Simulatorでは `AppEnvironment` が `http://localhost:4000` を使う。

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineApp \
  -sdk iphonesimulator \
  -quiet build
```

実機では以下のどちらかでAPI base URLを切り替える。

- `apps/ios/MusicTimelineApp/Support/AppEnvironment.swift` の `physicalDeviceAPIBaseURL`
- Xcode Schemeの環境変数 `API_BASE_URL`

### xcodebuild troubleshooting

このリポジトリでは、CLI確認には `-target MusicTimelineApp -sdk iphonesimulator` を使う。ローカルXcode環境によっては、`-scheme MusicTimelineApp -destination 'generic/platform=iOS Simulator'` が以下のようなdestination解決エラーになる場合がある。

```text
Found no destinations for the scheme 'MusicTimelineApp' and action build.
```

その場合も、上記のtarget指定コマンドでSimulator SDK向けのビルド確認は可能。

Unit/UI test targetをCLIでビルド確認する場合は、`@testable import` のためDebug構成を使う。

```bash
DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineAppTests \
  -configuration Debug \
  -sdk iphonesimulator \
  -quiet build

DEVELOPER_DIR=/Applications/Xcode.app/Contents/Developer \
xcodebuild -project apps/ios/MusicTimelineApp.xcodeproj \
  -target MusicTimelineAppUITests \
  -configuration Debug \
  -sdk iphonesimulator \
  -quiet build
```

## Checks

```bash
cd backend/api
ruff check .
pytest
```

現在の確認結果:

- `ruff check .`: passed
- `pytest`: 150 passed
- `xcodebuild` app target: passed
- `xcodebuild` unit/UI test targets with Debug configuration: passed

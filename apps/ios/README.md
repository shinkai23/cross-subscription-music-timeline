# iOS プロトタイプ

このフォルダには、iOS 優先プロトタイプ用の SwiftUI ソース骨格を置いています。

現在の作業環境は Windows のため、Xcode でのビルドや MusicKit の実機検証は行っていません。`apps/ios/MusicTimelineApp` 以下のファイルは、macOS 上で作成した Xcode プロジェクトへ取り込む前提です。

## 最初の実装対象

- SwiftUI アプリの基本構成
- Apple Music / Spotify のサービス選択
- モックタイムライン
- 投稿作成画面の骨格
- プレイリスト変換レビュー画面
- Apple Music 認可処理の境界
- Apple Music カタログ検索の骨格

## Xcode での取り込み手順

1. Xcode で新規 iOS App プロジェクトを作成する。
2. プロジェクト名を `MusicTimelineApp` にする。
3. `apps/ios/MusicTimelineApp` 以下の Swift ファイルを追加する。
4. MusicKit capability を有効にする。
5. Apple Music 利用目的の説明文を `Info.plist` に追加する。
6. MusicKit 認可は実機 iPhone で確認する。


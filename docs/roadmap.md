# ロードマップ

## Phase 0: 調査とプロジェクト初期化

- [x] プロダクトコンセプト分析
- [x] 法務・Provider リスク整理
- [x] 初期アーキテクチャ
- [x] GitHub テンプレート
- [x] GitHub Actions draft
- [x] GitHub セットアップガイド
- [x] GitHub リモートリポジトリ作成
- [ ] GitHub Project board 作成
- [ ] ロードマップから初期 Issue を作成

## Phase 1: iOS Apple Music プロトタイプ

- [x] iOS SwiftUI アプリ骨格を作成
- [x] MusicKit 認可の骨格を追加
- [x] Apple Music カタログ検索の骨格を追加
- [ ] 曲・アルバムカードを実機で表示確認
- [x] 投稿詳細から Provider リンクを開く
- [x] ローカルモックタイムラインを作成

## Phase 2: Backend MVP

- [x] TypeScript API サービス骨格を作成
- [x] PostgreSQL スキーマ draft を追加
- [x] ローカル PostgreSQL docker compose を追加
- [x] auth/session 骨格を追加
- [ ] 投稿 CRUD を DB に接続
- [x] モックタイムライン endpoint を追加
- [x] Provider adapter interface を追加
- [x] マッチング単体テストを追加

## Phase 3: Spotify 連携

- [ ] Spotify app を登録
- [x] OAuth PKCE authorize URL 骨格を追加
- [ ] ユーザーが選んだプレイリストを import
- [ ] 正規化したプレイリストメタデータを保存
- [ ] Spotify deep link を開く

## Phase 4: サービス間マッチング

- [ ] ISRC マッチングを本実装
- [ ] 曲名・アーティスト fallback を本実装
- [ ] confidence と reason を保存
- [ ] プレイリスト変換レビュー UI を実機で確認
- [ ] Spotify プレイリストメタデータから Apple Music プレイリストを作成

## Phase 5: コンプライアンスとモデレーション

- [ ] 通報フロー
- [ ] ユーザーブロック
- [ ] 投稿削除
- [ ] 管理者向けモデレーション画面
- [ ] Provider 連携解除
- [ ] データ削除リクエスト導線

## Phase 6: Android

- [ ] Android アプリ shell を作成
- [ ] タイムラインを実装
- [ ] サービス連携を実装
- [ ] プレイリストレビューを実装

## Phase 7: ポートフォリオ仕上げ

- [ ] アーキテクチャ図
- [ ] デモ動画
- [ ] スクリーンショット
- [ ] API ドキュメント
- [ ] CI status badge
- [ ] デプロイ手順

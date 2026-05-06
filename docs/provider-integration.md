# Provider 連携設計

## Apple Music

iOS を最優先にするため、Apple Music 連携は MusicKit から始めます。

初期フロー:

1. iOS アプリで MusicKit 認可を要求する。
2. Apple Music サブスクリプション状態を確認する。
3. Apple Music カタログを検索する。
4. 曲、アルバム、プレイリストの Apple Music URL を開く。
5. ユーザーが明示的に確認した場合だけ、ライブラリ内にプレイリストを作成する。

サーバー側の責務:

- Apple Music developer token をサーバー側で生成する。
- Apple の秘密鍵をモバイルアプリに含めない。
- マッチングと変換に必要な最小限のデータだけ保存する。

## Spotify

モバイルクライアントでは OAuth Authorization Code with PKCE を使います。

初期 scope:

- `playlist-read-private`
- `playlist-modify-private`
- `playlist-modify-public`

具体的な機能が必要になるまで、より広い scope は追加しません。

初期フロー:

1. モバイルクライアントが PKCE code verifier と S256 code challenge を生成する。
2. Backend が code challenge を含む Spotify 認可 URL を生成する。
3. ユーザーが Spotify で認可する。
4. アプリが redirect URI 経由で authorization code を受け取る。
5. code verifier を使って token exchange を実装する。
6. Backend が長時間の処理を担当する場合、refresh token を暗号化して保存する。

## サービス間マッチング

マッチングはメタデータベースにします。

1. ISRC
2. 曲名 + アーティスト + アルバム
3. 曲名 + アーティスト + 再生時間
4. ユーザー確認

新規機能で Spotify audio analysis や audio features を使いません。生音源の分析や保存もしません。

## 再生

再生は Provider 所有の体験として扱います。

- Apple Music は許可される範囲で MusicKit を使う。
- Spotify は公式アプリリンクまたは SDK の挙動を使う。

インライン音声は任意機能であり、Provider に依存します。preview が存在しなくてもプロダクトが成立する設計にします。

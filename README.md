上方向にドーナツを撃つ。相手に着弾すればライフポイントが減る。WASDで動くプレイヤーは”G”で撃つ。矢印で動くプレイヤーはRIGHTBRACKETで撃つ。
# ケーキ泥棒

## 実装環境の必要条件
* python >= 3.10
* pygame >= 2.1

## ゲームの概要
ドーナツを投げ合いゲーム

## ゲームの実装
### 共通基本機能
* 背景画像とキャラクターの描画
* キャラクターの基本操作

### 担当追加機能
①ヘルスバー（担当：あゆと）：キャラクターのヘルス状態を表す
②爆弾撃つ（担当：アム）：ドーナツをキャラクターから撃つ
③加速する（担当：パトリック）：特定のキーを押したらキャラクターの速度をアップする
④燃料補充（担当：ハルト）：燃料を補充する
⑤シールド（担当：かい）：ドーナツからキャラクターの身を守る

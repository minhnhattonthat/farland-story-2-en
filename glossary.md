# Glossary - Farland Story 2

Binding for every translator and reviewer. Agents propose additions in reports; only the controller edits this file.
`tools/batches.py check` enforces the Characters and Places rows exactly (case-sensitive) and the other rows
case-insensitively, wherever the JP term occurs (katakana terms only as a whole katakana run).

## Rulings (asked of the user once; options and reasons in docs/decisions.md)
- Honorifics: kept, hyphenated (Ark-sama, Riad-san). Name order: Western (given name first).
- Romanisation source (D2): official English (none exists for this game), else the earlier fan script by
  Eien Ni Hen (chapters 1-10: Serena, Cifil, Quirinus, Docaty, Ligito, Wace, Taricalla, Kentoone, Lodoss...),
  else Hepburn without macrons (a katakana rendering of a Western name takes that name: Eleanor, Paris).
- Credits: English.
- Register: modern natural fantasy English, light and earnest; villains grandiose, comic monsters comic (D9).
  Sound effects and cries: English onomatopoeia ("Grrr...", "Woof!"), not romaji; character tics that are part
  of a voice stay as sounds (Gibogera's "Gebohahaha!", Klaus's "Rawr!") (D9).
- Abbreviations: full names and terms everywhere; prefer engine changes over shortening (D4).
- Graphics text: translate all of it (titles, menus, banners); keep the Japanese logo only if no official English logo exists.

## Style rules
- Punctuation map: 「」 -> "...", 『』 -> '...', ・・・ -> ..., ！？ -> ?!, full-width digits/letters -> ASCII.
- Voices: docs/style-reference.md (per character, with approved pairs). Who is who: docs/synopsis.md.
- Neiful is a girl (boyish speech). Circlus is a woman. Rigit's しぇーぎ is baby talk for 正義 "justice" ("jushtish").

## Characters
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| リアド | Riad | | hero, second prince of Valdes | Riado |
| サリーナ | Serena | | heroine, Kentoone clan dancer | Salina, Sarina |
| クラウス | Klaus | | wolf, calls Riad アニキ "Big Bro" | |
| ヴァラカナ | Valakana | | demon swordsman, Riad's friend | |
| アルタバ | Altaba | | sailor of Lodoss, captain of the Silent Moon | |
| カイ | Kai | | mounted knight of Felsaria | |
| エリア | Eria | | healer, Docaty's adopted daughter | Elia, Area |
| シフィル | Cifil | | Prince of Felsaria, Ark's son | Sifil, Shifiru |
| ネイフル | Neiful | | girl, Eleanor's daughter, boyish | |
| ケイリナス | Quirinus | | self-styled genius, Lantia's son | Kaylinus, Keirinas |
| リギット | Ligito | | young White Dragon, baby talk | Rigit |
| ドリス | Doris | | summoner, Kansai dialect | |
| シュナリー | Shunari | | guardian of the Kentoone | Shunary |
| サークルス | Circlus | | woman, harpist | |
| アルデナーラ | Ardenara | | legendary summoner | Aldenara |
| おゆきちゃん | Oyuki-chan | | snow spirit (also お雪ちゃん) | O-Yuki |
| アーク | Ark | | King of Felsaria, hero of the first game | Arc |
| ドカティ | Docaty | | Eria's adoptive father | Dokati |
| フェリオ | Ferio | | Queen of Felsaria | |
| エレノア | Eleanor | | knight commander, Neiful's mother | |
| ランティア | Lantia | | knight, Quirinus's father | |
| ディーノ | Dino | | | |
| ルシーダ | Lushida | | | Lucida |
| ゴダール | Godal | | | Godar |
| アリシア | Alicia | | castle aide | |
| ネレイド | Nereid | | Emperor of Valdes, Riad's father | |
| ギボゲラ | Gibogera | | imperial adviser | |
| タリカーラ | Taricalla | | crown prince, Riad's elder brother | Talikara |
| ゾルディン | Zordin | | imperial general, Riad's master | Zoldin |
| ウェイス | Wace | | sea commander, Zordin's senior pupil | Weiss |
| バーナサス | Barnassus | | Gibogera's henchman | Bernasas |
| サイトス | Saitos | | | |
| スラミ | Surami | | | |
| ライナス | Linus | | Kentoone elder | |
| パリス | Paris | | King of Troia | |
| ニセリアド | Fake Riad | | impostor | |

## Places
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| フェルサリア | Felsaria | | | |
| イオニア | Ionia | | イオニア大陸 the Ionian continent | |
| ヴァルデス | Valdes | | ヴァルデス帝国 the Valdes Empire | |
| ヴァン・パレス | Van Palace | | the imperial capital | |
| パラケル | Paracel | | kingdom of magic | |
| ケントゥーネ | Kentoone | | clan | Kentune |
| サンデッド | Sundead | | volcano | |
| ルイドック | Ruidock | | port | |
| ロードス | Lodoss | | Altaba's island | Rhodes |
| テーバイム | Tebaim | | | |
| キンドア | Kindoa | | | |
| トロイヤ | Troia | | | |
| ギネビア | Guinevia | | snow country | |
| モンダニア | Mondania | | | |
| ファーランド | Farland | | the world | |
| サイレントムーン | Silent Moon | | Altaba's magic ship | |
| 自由の港 | Free Port | | | |

## Items / skills / terms
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| 破亡の舞 | Dance of Ruin | | also はぼうのまい | Dance of Death |
| はぼうのまい | Dance of Ruin | | | |
| 心の舞 | Dance of the Heart | | Serena's healing dance in dialogue | |
| かいふくのまい | Healing Dance | | system message | |
| ブレイクストーム | Break Storm | | Riad's technique | |
| がろうけん | Wolf Fang Fist | | Klaus's technique (牙狼拳) | |
| マジックシップ | magic ship | | | |
| 魔法の鏡 | Magic Mirror | | | |
| 聖剣 | holy sword | | | |
| デーモン族 | demon | | the demon race | |
| 魔王 | Demon Lord | | | |
| ホワイトドラゴン | White Dragon | | | |
| グリーンドラゴン | Green Dragon | | | |
| ドラゴンライダー | Dragon Rider | | | |
| 帝国 | Empire / Imperial | | the Empire, the Imperial army | |
| ＨＰ | HP | | | |
| こうげきりょく | Attack | | also Ｐこうげきりょく | |
| 攻撃力 | Attack | | 間せつ攻撃力 Ranged Attack | |
| まほうこうげきりょく | Magic | | level-up message | |
| まほうりょく | Magic | | | |
| 魔法力 | Magic | | | |
| ぼうぎょりょく | Defense | | also Ｐぼうぎょりょく | |
| まほうぼうぎょりょく | Resistance | | magic defence | |
| Ｍぼうぎょりょく | Resistance | | magic defence | |
| Ｍぼうぎょ | Resistance | | | |
| Ｐぼうぎょ | Defense | | | |
| すばやさ | Speed | | | |
| 素早さ | Speed | | | |
| いどうりょく | Move | | | |
| 移動力 | Move | | | |
| 最大体力 | Max HP | | | |
| ゴールド | Gold | | | |
| ＥＸＰ | EXP | | | |

## Summons (rods), items with names
| JP | EN | max | notes | Avoid |
|---|---|---|---|---|
| ライジングドッグ | Rising Dog | | | |
| ソードマン | Swordsman | | | |
| サラマンダー | Salamander | | | |
| ゴーレム | Golem | | | |
| ポレポレ | Pole-Pole | | | |
| ウオーターガール | Water Girl | | | |

## Decisions from earlier batches
- Item, unit and class names: `script/items.json`, `units.json`, `classes.json` (controller-translated, b002).
- Address terms: 父上 Father, 父さん Dad (Cifil to Ark), 兄上/兄さん Brother, 師匠 Master (Master Zordin),
  先生 for Ardenara "Master Ardenara" (b010 used -sensei; unified), アーク王 King Ark, リアド王 King Riad,
  アークおじ様 Uncle Ark, ドカティおじさん Uncle Docaty, リアドにいちゃん (Ligito) Big Brother Riad.
- Titles of stage cards in `<...>`: ＜帝国脱出＞ <Escape from the Empire>, ＜船出＞ <Setting Sail>, ＜出立＞ <Departure>,
  ＜奪取＞ <Seizure>, ＜海戦＞ <Sea Battle>.
- かぐや姫作戦 Operation Kaguya-hime; 東洋 the Orient; アンデッド使い necromancer; かくれショップ hidden shop;
  間せつ魔法力 Ranged Magic; 直間魔法力 Direct/Ranged Magic; サメやろう "that shark creep".
- Ligito's lisp may touch honorifics ("Serena-shan") but never the glossary name itself.
- American spelling.

## Menu labels (graphics text, drawn by tools/gfx.py; batches.py does not check these)
- Title: はじめから New Game, つづきから Continue, 環境設定 Settings.
- Unit menu (48 px): 移動 Move, ワープ Warp, 攻／回 Action (attack or heal), 必殺 Special, 買物 Shop, 武器 Weapons,
  アイテム Items, 交換 Trade, 集合 Rally, 待機 Wait.
- Map menu (80 px): ターン終了 End Turn, 全体マップ Full Map, ユニット一覧 Unit List, 状況 Objective, セーブ Save,
  ロード Load, 環境設定 Settings.

# Farland Story 2 - synopsis for translators

Source: `script/ch00.json` .. `ch38.json` (jp), `units.json`, `classes.json`, `objectives.json`, `items.json`, `battle.json`.
All English names here are PROVISIONAL. Binding spellings live in `glossary.md` (controller only).
"fan" = spelling in the old partial fan translation of ch01-10 (untrusted, cross-check only).

Speaker boxes: the script has no speaker tags. `box` upper/lower mostly alternates with each change of speaker, so the same
character can be upper in one exchange and lower in the next. Work out the speaker from voice (pronoun, endings, laugh) and
context, not from the box. Lines with no box are narration (`{full}` captions) or townsfolk (`町人`) signs.

## 1. Cast

### Riad's party (playable)
- **リアド Riad** (fan Riad). Hero. Second prince of the Valdes Empire (ヴァルデス帝国第二皇子), son of Emperor Nereid, younger
  brother of Talikara. Left the palace to live as a hunter in a village; hates war because his mother died in one.
  俺; キミ to Salina; polite 私 / です・ます with kings and elders ("初めてお目にかかります"). Blunt, quick-tempered, idealistic, kind
  ("リアド殿の口の悪いのには" - known for his sharp tongue). Calls Nereid 父上, Talikara 兄上 (兄さん once, ch27), Zoldin 師匠.
  Signature technique ブレイクストーム Break Storm (taught by Zoldin). Briefly loses his memory (ch14). Becomes ruler of Valdes
  and marries Salina (ch37).
- **サリーナ Salina** (fan Serena). Heroine, Riad's childhood friend and love interest. A dancer; 私, soft feminine わ/ね/のよ.
  Gentle, empathic; her 心の舞 "heart dance" heals (system: かいふくのまい). Last of the Kentune clan (ケントゥーネ), born in Paracel.
  REVEAL ch20: she is the Kentune chief's daughter; the clan took her memories 14 years ago and hid her in an imperial
  village. She learns the 破亡の舞 in ch20. Queen at the end.
- **クラウス Klaus** (fan Klaus). A wolf (おおかみ; class ワーウルフ werewolf), former pet of Prince Talikara whom Riad freed.
  おいら; calls Riad アニキ; tics ガオ / ガルル / グルル, ends sentences with ガオ. Childish, always hungry, cheeky.
  Skill がろうけん (garoken, wolf fist) likely his.
- **ヴァラカナ Valakana** (fan Valakana). Riad's friend; a demon (デーモン族, ch17). Cool loner, フッ, 俺 (私 in his
  flashback). Was a bandit who tried to rob Riad and Salina; Salina's dance made him cry - that is the "debt" (借り) he repays
  in ch02 (told in ch17). Ends up with Shunary (ch36).
- **アルタバ Altaba** (fan Altaba). Sailor from Rhodes, captain of the magic ship Silent Moon. ワス; endings ッス / ダス.
  Manly at sea, turns weepy and camp on land (切ないわ, お・ね・が・い, まっ、失礼ね！, uses わ/のよ) and clings to Riad.
  Becomes a fisherman in Rhodes (ch34).
- **カイ Kai** (fan Kai). Knight of Felsaria, rides a horse everywhere ("私と馬は一心同体"). 私; polite, earnest, easily
  fooled at first. Friend of Docaty; fought beside King Ark 20 years ago. Separated ch13-17.
- **エリア Elia** (fan Eria). Docaty's adopted daughter (found as a baby abandoned in a forest). Healer (回復魔法). 私
  (あたし once, ch32); polite but spirited, scolds Neiful's language ("お・下・品よ"), プンプン. Friend of Sifil and Neiful.
- **シフィル Sifil** (fan Cifil). King Ark's son, Felsaria's prince. ボク/ぼく; whiny, timid ("もうかえろうよ"), blames others,
  calls Ark 父さん (父上 once). Grows brave; becomes a Dragon Rider on Rigit (ch18). Two unit entries (foot / rider).
- **ネイフル Neiful** (fan Neiful). A GIRL: daughter of knight commander Eleanor (ch06 "娘さん"). Tomboy: ボク, rough boyish
  speech (だろっ, よぉ, それでも男かよ), bossy toward Sifil. Use she/her.
- **ケイリナス Kaylinus** (fan Quirinus). Son of knight Lantia. Self-styled "Felsaria's greatest genius" (フェルサリア一の知恵者,
  天才ケイリナス); 私; pompous (はっはっは, しっけいな, コホン); flirts with every woman. His gambles: burn the forest (ch08),
  board the enemy ship (ch12), gift-horse trick at Troia (ch16), flood the siege (ch18), fill the sea (ch22).
- **リギット Rigit** (fan Ligito). Young White Dragon guarding east Felsaria by a promise his mother made to King Ark. ぼく;
  baby talk: っちゃ / でちゅ / ちゃ / でしゅ, し→しぇ ("しぇーぎ" = 正義 justice, NOT a name), あんちゃ. Fooled by Bernasas (ch10).
  Hidden power when ridden by a compatible human (ch14, ch18).
- **ドリス Doris** (fan Doris). Summoner (召喚士), Kansai-ben (うち, や, やねん, へん, めっちゃ). 16 but looks about 8 (ch11).
  "正義の美少女召喚士". Admires Aldenara. Summons: サラマンダー, ゴーレム, ポレポレ, ポレポレグレート. Travels with
  Kaylinus at the end, bickering (ch33).
- **シュナリー Shunary**. Guardian of the Kentune clan (ch19). 私/わたし; stiff, earnest (〜のだ, ではないのだな), cries easily
  when rebuffed. Sole survivor of the clan's massacre. Falls for Valakana (ch36).
- **サークルス Circlus**. Found collapsed in Guinevia (ch17). Vamp: うふン, endings with ン, ス・テ・キ, clings to Riad, wants to
  stay out of fights. REVEAL ch27: Gibogera's spy and Prince Talikara's lover; dies stepping between the brothers.
- **アルデナーラ Aldenara**. Legendary summoner sleeping in Paracel; sleeps 12-year cycles, was woken after 8 so has only
  half her/his power (ch18). わし/私, じゃ endings; falls asleep mid-sentence (グー). Summons ライジングドッグ, ソードマン, ドラゴン.
  REVEAL ch29: of the same first-human kin as Gibogera; the gods charged Aldenara with destroying him.
- **おゆきちゃん / お雪ちゃん O-Yuki-chan**. Snow spirit (class ゆきのせいれい), Kai's comrade from 20 years ago; Doris summons
  her by accident (ch17). アタシ, katakana endings ヨ / ネ, calls Kai カイちゃん.
- **アーク Ark** (glossary ruling may use Arc). King of Felsaria, hero of Farland Story 1 who drove back the demon lord 20 years
  ago. 私 now (ぼく in the 15-years-ago flashback, ch10). Warm, joking. Holy sword (聖剣). Captured off-screen, cursed and fought
  in ch24 (stage 19 boss, second unit entry). Joins briefly at the end.
- **ドカティ Docaty** (fan Docaty). Elia's adoptive father, Felsarian veteran. わし, じゃ / のう; stubborn (ガンコオヤジ), doting
  dad. Fought as a stage boss (ch04), then ally. Weeps that Elia no longer needs him (ch32).

### Felsaria (non-party)
- **フェリオ Ferio** - Queen of Felsaria (王妃), Ark's wife, Sifil's mother. Polite, firm, motherly.
- **エレノア Eleanor** - knight commander (騎士団長), Neiful's mother. Captive with Ark; rescued ch24; "don't lose to men" (ch26).
- **ランティア Lantia** - knight, Kaylinus's father. わし-ish, gruff (ch24, ch26).
- **ディーノ Dino**, **ルシーダ Lucida** (fan Lushida), **ゴダール Godar** (fan Godal) - Ark's veteran escorts (ch05), captive with him.
- **アリシア Alicia** - castle aide; scolds Kai to dismount before the king (ch05).
- Neiful's father appears ch24/26 (父様; unnamed in lines; maybe Dino - unconfirmed).

### Valdes Empire / villains
- **ネレイド Nereid** (fan Nereid). Emperor of Valdes, Riad's father. 余 / わし; imperious (〜のだ, 〜い). Once fought to protect
  little Val after losing his wife, wanting to end war; Gibogera's influence turned him into a conqueror (ch27). Transforms into a
  monster (ch28), regains himself dying and asks Riad to make the peaceful country his wife wished for.
- **ギボゲラ Gibogera** (fan Gibogera). Imperial adviser. Laugh ゲボハハハ, grunt ゲボッ; obsequious 私 / ございます to the
  emperor, mocking-polite to Riad. Behind everything. REVEAL ch29: one of the first humans the gods made and gave divine power;
  fled when they tried to take it back. Final battles inside his body (ch30). Mini clones ミニギボゲラ.
- **タリカーラ Talikara** (fan Taricalla). Crown prince, Riad's elder brother; 私; sickly (ゴホゴホ). Cold in ch00 ("ばかなやつだ").
  REVEAL ch27: he envied Riad's freedom, tried and failed to sway their father, loved Circlus, begs Riad to kill Nereid to save
  his soul; dies.
- **ゾルディン Zoldin** (fan Zordin/Zoldin). Imperial general, Riad's sword master. 私; terse, proud warrior. Holds Tebaim (ch14).
  REVEAL ch25: loyal but grieved by the emperor's change; taught Riad Break Storm on purpose; dies warning about Gibogera.
- **ウェイス Weiss** (fan Wace). Zoldin's senior pupil (Riad's 兄弟子), now an imperial sea commander; 私/俺, sneering クックク.
  Strong at sea. Wrecks the party (ch13); dies with respect for Riad (ch23, "〜だ・ぜ・・・").
- **バーナサス Bernasas** (fan Barnassus). Gibogera's henchman; laugh クキキッ / クキックキッ; fake-polite (〜ですよ, 〜下さいな),
  welcomes the party "〇〇さんでかんげいしますよ" with penguins, cats, elephants. Frames Riad (ch03), tricks Docaty and Rigit,
  always flees. Goaded into rage and killed (ch21).
- **サイトス Saitos** - stage 21 boss (Van Palace) per objectives; no named dialogue found.
- **スラミ Surami** - stage 16 boss per objectives; probably the chimera (キメラ) of ch20.
- **ニセリアド** fake Riad - impostor leading the monster raid (ch06).
- **パラケル王** King of Paracel (わし, じゃ), **パリス Paris** King of Troia (わし; art fanatic, cowardly then won over). Both
  bring troops in ch26.
- **ライナス Linus** - Kentune spirit/elder who waited 500 years in the tree to teach Salina; わし, じゃ. REVEAL ch20: the
  chimera she fought turns out to be him. Dies after passing on the dance.
- White Dragon (Rigit's mother, female) and Green Dragon (servant of darkness, hereditary foe) in the ch10 flashback; the Green
  Dragon reappears ch26.
- Generic units: ジェネラル, グリーン/ブルー/レッドキャット, カイザーペンギン, エレファント (war elephants), てつたろう (mecha),
  カメナイト, ザニガニンガー, the shark guy サメやろう (Rhodes occupier).

## 2. Places, factions, terms
- イオニア大陸 Ionia (continent). ヴァル Val (small country that became) ヴァルデス帝国 Valdes Empire. Capital/palace city
  ヴァン・パレス Van Palace (stage 21 title; "never breached").
- フェルサリア王国 Felsaria (Ark's kingdom, across the sea; did not know other continents existed). フェルサリア城 castle.
  サンデッド Sundead (volcano in the east, White Dragon lair). ルイドック Ruidock (western port).
- 自由の港 / 自由都市国家 the Free Port (free city-state; pays tribute, so the army stays out - until ch02).
- ロードス Rhodes (fan Lodoss; Altaba's island homeland, conquered; ロードス島).
- パラケル王国 Paracel (magic kingdom; Salina's birthplace; fell in ch00, rebels ch17). 北の谷 northern valley = Kentune village.
- テーバイム Tebaim (coast; Zoldin's new conquest, ch14). キンドア Kindoa (merchant nation; child-slave market, ch15).
  トロイヤ Troia (largest southern nation, King Paris). ギネビア Guinevia (snow country, 雪の国). モンダニア Mondania (rebels).
- ファーランド Farland (the world). 東洋 the Orient (Kaguya-hime story, かぐや姫作戦).
- ケントゥーネ一族 Kentune clan (fan Kentoone): keeps the balance between good and evil; their dances are contracts with the gods.
- 破亡の舞 Dance of Ruin (fan "Dance of Death"; habou no mai, system はぼうのまい): returns everything to nothing, meant to reset
  the world if good or evil overruns it. 心の舞 / かいふくのまい heart dance / healing dance.
- サイレントムーン Silent Moon (Altaba's magic ship, マジックシップ). 魔法の鏡 magic mirror. 聖剣 Ark's holy sword.
  ドラゴンのクラ dragon saddle (ch18). ドラゴンライダー Dragon Rider. ブレイクストーム Break Storm. デーモン族 demon race.
  魔王 the demon lord (FS1). 戦象部隊 war-elephant corps. 帝国ばんざい "Long live the Empire".

## 3. Chapter by chapter
- **ch00 Prologue.** Narration: 20 years after Ark became king, Val grew into the Valdes Empire. Gibogera reports Paracel
  conquered and whispers of a Kentune girl and the Dance of Ruin to Nereid. Riad is summoned home; Talikara sneers; Nereid
  offers to "end war" and reveals Salina, to be made a puppet by ritual. Riad attacks Gibogera with Break Storm, flees with
  Salina; Nereid orders her taken alive, Riad killed. Upper/lower: emperor upper vs Gibogera lower at first.
- **ch01 Stage 1 Escape.** Riad and Salina flee; Riad senses his father has changed. Klaus joins. Heading for the Free Port.
- **ch02 Stage 2 Setting sail.** Free Port; plan to ask King Ark of Felsaria for help. Valakana appears to repay a debt; the
  army breaks the port treaty. Altaba of Rhodes and the Silent Moon. Comic banter (Klaus, Valakana).
- **ch03 Stage 3 Felsaria.** Landing; Bernasas has framed Riad for raiding villages and sets Kai on them. Kai senses no evil,
  Bernasas turns on him. Kai joins. Altaba clings to Valakana on land.
- **ch04 Stage 4 Docaty.** They save Elia from kidnappers; Bernasas tricks Docaty into fighting them. Salina's heart dance
  heals him; he believes them and leads them to the castle. Bernasas flees.
- **ch05 Stage 5 King Ark.** Riad meets Ark, who sails to Valdes for talks with Eleanor, Dino, Lantia, Lucida, Godar on the
  borrowed Silent Moon. Monsters attack the castle; Queen Ferio commands; Elia insists on joining. Kai won't dismount.
- **ch06** Battle: Sifil and Neiful, out monster-hunting, rescued; a fake Riad led the raid. Suspicion of an imperial pact with
  monsters; fear for Ark.
- **ch07 Stage 6 Departure.** No word from Ark (magic mirror blank). Riad offers to find him; Ferio lets Sifil, Neiful, Elia
  go; Docaty stays. Valakana's creed: choose and carve your own road.
- **ch08** North forest: Kaylinus joins (flirts with Salina and Elia); plan to burn the forest under the enemy army.
- **ch09** Success; prisoner reveals Ark is held in an imperial fortress and the empire seeks the White Dragon at Sundead.
  Altaba's camp side frightens him.
- **ch10 Stage 7 Dragon.** Sundead: Bernasas has convinced Rigit they are villains. Flashback "15 years ago": Ark stops a White
  vs Green Dragon fight; the White Dragon vows to guard east Felsaria, Rigit to inherit. Rigit apologises and joins. Plan:
  steal an imperial ship at Ruidock.
- **ch11 Stage 8 Seizure.** Ruidock occupied; Silent Moon sold to merchants. Doris rescued (16, looks 8, Kansai-ben,
  overpowered summon mishap). They retake the ship.
- **ch12 Stage 9 Sea battle.** Weiss attacks; Riad learns Zoldin ordered it. Kaylinus: board the enemy ship.
- **ch13** Weiss wins anyway; the ship goes down, Salina grabbed at as they are swept apart. Short, dramatic.
- **ch14 Stage 10 Zoldin.** Washed up on Tebaim's coast; Sifil, Altaba, Kai missing. Riad has amnesia; Zoldin attacks;
  Riad's memory returns mid-fight (shown when he names Elia unprompted). Zoldin withdraws. Rigit's hidden power hinted.
- **ch15 Stage 11 Kindoa.** Child-slave market; Neiful rescues a crying Sifil. Dying officer: Troia is now imperial.
- **ch16 Stage 12 King of Troia.** Paris panics at Riad's arrival. Altaba rejoins. Kaylinus's trick: smuggle in via an art
  object (Trojan-horse joke). Riad lectures Paris; Paris demands they wipe out the imperial force in Guinevia.
- **ch17 Stage 13 Snow country Guinevia.** Valakana's flashback of meeting Riad and Salina (caption "5 years ago" likely
  belongs here). Bernasas with penguins; Kai returns; Doris summons O-Yuki by mistake. Circlus found, joins, oddly knows Riad's
  name (Valakana suspicious). Paracel's king begs help; Salina insists.
- **ch18 Stage 14 Paracel Castle.** Circlus tries to keep Riad back. Siege; Aldenara wakes early; flood plan; Sifil rides
  Rigit as Dragon Rider. Enemy ambush at the lake ("how did they know?" - spy hint). King points to the Kentune village.
- **ch19 Stage 15 Kentune.** Northern valley; Shunary attacks then recognises Salina; clan wiped out by imperial treachery.
  Bernasas with cats. The party is sucked into a tree.
- **ch20 Stage 16 Dance of Ruin.** Inside the tree a voice reveals Salina's origin; chimera trial; Salina dances the Dance of
  Ruin; the chimera was Linus, who explains the dance and dies. Everyone comforts Salina.
- **ch21 Stage 17 Poor elephants.** Bernasas already knows about the dance (spy hint); war elephants. The party mocks him till
  he charges in raging and dies. Rebellions spread.
- **ch22 Stage 18 Rhodes Island.** Helping Rhodes rebels; Weiss again; Kaylinus: fill the shallows so the fight is on land;
  Rhodes people help. Circlus flirts.
- **ch23** Weiss dies, praising Riad. Island joined to the mainland.
- **ch24 Stage 19 Tunnel.** Klaus's old shortcut to the palace. Gibogera unleashes cursed Ark; Sifil pleads; Ark freed. Lantia,
  Eleanor, Neiful's father rescued. Ark goes home, entrusts Sifil to Riad. Riad suspects a power controlling the empire.
- **ch25 Stage 20 Master and pupil.** Riad defeats Zoldin, who dies revealing the emperor changed and warning about Gibogera.
- **ch26 Stage 21 Van Palace.** Green Dragon recognises Rigit. Overwhelmed at the capital; Paracel's king, Paris, Ark,
  Lantia, Eleanor, Docaty arrive with troops. Final push.
- **ch27 Stage 22 Talikara.** Sickly Talikara knows everything "from a spy"; the brothers duel; Circlus takes the blow,
  confesses love, dies; she was the spy. Talikara tells Nereid's history, asks Riad to kill their father, dies.
- **ch28 Stage 23 Emperor.** Gibogera presents Nereid transformed and ecstatic (オオッ！よい気持ちじゃ). Riad vows to finish him;
  his regeneration fails; Nereid, himself again, dies asking for peace.
- **ch29 Stage 24 Pursuit.** Gibogera reveals his origin and Aldenara's; chase.
- **ch30 Stage 25 Gibogera.** Inside Gibogera's body; Salina's Dance of Ruin; attack the heart. Aldenara was shut out.
- **ch31** Epilogue: Sifil home; Ferio's reward is a book on kingship.
- **ch32** Sifil, Neiful, Elia plan to visit Riad; Docaty sulks at Kai over Elia growing up.
- **ch33** Kaylinus and Doris on a training journey, bickering. **ch34** Altaba fishing in Rhodes, misses Riad.
- **ch35** Rigit bored guarding peaceful Felsaria. **ch36** Valakana, Shunary and Klaus rebuild Valdes town; Shunary wins him.
- **ch37** Riad and Salina: a world of friends ends war; Riad succeeds Nereid, signs peace treaties; Queen Salina dances.
- **ch38** Staff credits (Riad/Salina host them).

## 4. Late reveals - keep early lines neutral
- Circlus is Gibogera's spy and Talikara's lover (ch27). In ch17-22 she must read as a clingy flirt; keep the hints
  (knowing Riad's name, ambushes, Bernasas knowing about the dance) as subtle as the Japanese.
- Talikara is sympathetic and dying (ch27). His ch00 "ばかなやつだ" stays a cold aside.
- Zoldin's hidden loyalty to Riad and grief over the emperor (ch25). Earlier he is a hard enemy.
- Nereid was once a peace-seeker corrupted by Gibogera (ch27-28). Riad's ch01 hunch "something has changed" is only a hunch.
- Gibogera's and Aldenara's shared origin as the first humans (ch29).
- Salina's true lineage and memory loss (ch20); before that she sincerely knows no dance of ruin. The Dance of Ruin's real
  purpose (reset the world, balance of good and evil) is only explained in ch20.
- The chimera is Linus (ch20). Valakana is a demon and the nature of his debt (ch17).
- Ark is captured (told ch09) and cursed (ch24).
- Shunary/Valakana romance (ch36); Riad becomes ruler and Salina queen (ch37).
- Not secrets but easy to get wrong: Neiful is female; Doris is 16; "しぇーぎ" is Rigit saying 正義.

# Plan: Achievements + Statistics

## Goals
- Hard-but-achievable achievement thresholds (not trivial)
- STATS and BADGES buttons added to main menu
- Tabbed modal (STATS | BADGES) — no extra menus

## 1. Data Layer

### localStorage keys
- `snakeStats` — JSON object:
  ```js
  {
    gamesPlayed: 0,
    totalFood: 0,
    totalTicks: 0,
    longestSnake: 0,
    bestScore: 0,
    totalDeaths: 0,
    totalTimeMs: 0,
    skinsUnlocked: 0
  }
  ```
- `snakeAchievements` — JSON array of unlocked achievement IDs

### Per-game tracking (in-memory, reset on startGame)
- `gameStartTime` — timestamp when game started
- `gameFood` — food eaten this game
- `gameTicks` — ticks survived this game

---

## 2. Achievement Definitions

Thresholds (intentionally hard):

| ID | Name | Condition | Secret |
|---|---|---|---|
| `first_blood` | First Blood | Eat 1 food total | no |
| `glutton` | Glutton | Eat 50 food in one game | no |
| `behemoth` | Behemoth | Snake reaches 20 length | no |
| `speedrun` | Speedrun | Finish a game in <15 seconds | no |
| `marathon` | Marathon | Survive 300 ticks | no |
| `highroller` | High Roller | Score ≥ 100 | no |
| `addict` | Addict | Play 50 games | no |
| `unlocker` | Collector | Unlock 3 skins | no |
| `all_skins` | Completionist | Unlock all 6 skins | no |
| `slowpoke` | Slowpoke | Reach score 0 and die to wall (no food eaten) | no |
| `speedster` | Speedster | Reach tick interval ≤ 60ms | no |
| `veteran` | Veteran | Play 200 games | yes |
| `grandmaster` | Grandmaster | Score ≥ 500 | yes |
| `legendary` | Legendary | Score ≥ 1000 | yes |
| `food_hoarder` | Food Hoarder | Eat 500 total food | yes |
| `centurion` | Centurion | Score exactly 100 | yes |

---

## 3. Achievement Check Flow

**On food eaten (inside eat block):**
- `glutton` — check if gameFood ≥ 50
- `behemoth` — check if snake.length ≥ 20
- `slowpoke` — flag triggered if gameFood === 0 when gameOver

**On endGame:**
- `speedrun` — if (Date.now() - gameStartTime) < 15000
- `marathon` — if gameTicks ≥ 300
- `highroller` — if score ≥ 100
- `speedster` — if speed ≤ 60
- `centurion` — if score === 100
- Update stats: gamesPlayed, totalFood, totalTicks, longestSnake, bestScore, totalDeaths, totalTimeMs, skinsUnlocked
- `addict` — if gamesPlayed ≥ 50
- `veteran` — if gamesPlayed ≥ 200
- `unlocker` — if skinsUnlocked ≥ 3
- `all_skins` — if skinsUnlocked === 6
- `food_hoarder` — if totalFood ≥ 500
- `grandmaster` — if bestScore ≥ 500
- `legendary` — if bestScore ≥ 1000

---

## 4. UI — Tabbed Modal

### Main Menu buttons (add to `#menu-grid`)
```
[PLAY]  [SOUND ON]  [SKINS]  [STATS]  [BADGES]
```

### `#stats-modal` / `#badges-modal` — tabbed single modal
Tab buttons at top: `[STATS]` `[BADGES]`

**STATS tab:**
```
┌─────────────────────────────────┐
│  GAMES PLAYED        BEST SCORE │
│      42                 87      │
│                                 │
│  TOTAL FOOD       LONGEST SNAKE │
│      512                18      │
│                                 │
│  TOTAL DEATHS      TIME PLAYED  │
│       42             1h 23m 45s │
│                                 │
│  SKINS UNLOCKED                │
│      4 / 6                    │
└─────────────────────────────────┘
```

**BADGES tab:**
Grid of badge cards (3 columns):
- Unlocked: colored icon + name + description, subtle glow
- Locked (non-secret): gray + description
- Locked (secret): dark gray + "???"
- New (just unlocked): gold border pulse animation, 3s

### `#achievement-toast`
Top-center banner:
```
★ NEW BADGE: Behemoth — Snake reached 20 length!
```
- Gold border, dark bg, slides down
- Auto-dismiss after 3s
- Multiple stack vertically

---

## 5. Modifications to snake.html

### HTML additions
- BADGES button in menu
- STATS and BADGES menu buttons
- `#stats-modal` container (hidden by default)
- `#badges-modal` container (hidden by default)
- `#achievement-toast` container
- Tab buttons: STATS | BADGES

### CSS additions
- Badge card: 80×90px, icon top, name below, locked state gray
- Badge grid: 3-column flex wrap
- Tab styling (active/inactive)
- Toast slide-in animation
- New badge pulse animation

### JS additions
- `STATS` object with achievement definitions
- `stats` and `achievements` localStorage load/save
- `updateStats()` — update stats object, save to localStorage
- `checkAchievements()` — check all, unlock new ones, return list
- `showAchievementToast(list)` — display toast(s)
- `renderStats()` — fill stat values in modal
- `renderBadges()` — build badge grid
- `showStatsModal()` / `showBadgesModal()` / `closeStatsModal()`
- Per-game in-memory trackers: `gameStartTime`, `gameFood`, `gameTicks`
- `startGame()`: reset per-game trackers, increment gamesPlayed
- `eat()`: increment `gameFood`, call `checkFoodAchievements()`
- Tick loop: increment `gameTicks`
- `endGame()`: updateStats(), checkAchievements(), showToast()

---

## 6. File changes
- `snake.html` — single file, all changes inline

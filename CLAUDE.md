# CLAUDE.md

給 Claude Code（或任何後續維護者）在這個資料夾工作時的規則與慣例說明。

## 專案概述

一個單頁的「任務計時器」（25 分鐘倒數），視覺主題是從軌道上看星球的太空艙介面。純前端、零依賴、零建置流程，全部寫在一個 HTML 檔裡。

- 正式網址：https://0809-mission-timer.vercel.app
- GitHub：https://github.com/mantingyeh-svg/0809-mission-timer（`main` 分支，push 後 Vercel 會自動重新部署）

## 檔案結構

- `index.html` — 唯一的原始檔。HTML、CSS（`<style>`）、JS（`<script>`）都寫在同一個檔案裡，**不要**拆成獨立的 `.css`/`.js`，也不要引入任何外部套件、CDN 或框架。
- 沒有 `package.json`、沒有建置工具、沒有 node_modules。修改後直接存檔即可用瀏覽器打開驗證。

## 既有設計慣例（修改時請延續，不要另立新風格）

### CSS

- **顏色一律用 CSS 變數**，集中定義在 `:root`（`--bg-0`、`--accent`、`--btn-primary`、`--icon-glow`、`--text-hi/lo`、`--gray-btn*`…）。新增顏色時比照辦理，不要在規則裡直接寫死顏色去覆蓋這些語義變數。
- **形狀語言是膠囊/圓角**：按鈕、星球切換分頁一律 `border-radius:999px`，沒有方角元件。
- **字體分工**：等寬字體（`SF Mono, Menlo, Consolas`）只用在計時器數字、狀態標籤、日出日落這類「數據感」文字；一般 UI 文字（按鈕、標籤）用系統無襯線字體。
- **版面用 `position:fixed` + `vw`/`vh`** 鋪滿全螢幕，不是傳統文件流排版；`.hud` 用 flex column 置中疊圖層。
- **發光效果統一用 `filter:drop-shadow(...)` 或 `box-shadow`**，顏色引用共用變數（例如 `var(--icon-glow)`），不要每個元素各寫一組陰影色。
- **動畫用 CSS `@keyframes`**，透過加/移除 class（例如 `.jumper-pos.jumping`）控制啟停，不要用 inline style 硬切 animation。
- **已知陷阱**：祖先元素若有 `transform`，會讓子元素的 `position:fixed` 失效（會相對該祖先定位而非 viewport）。曾因此把 `#jumperPos` 移到 `<body>` 直接子層以避開 `.controls` 的 `transform:translateX(-50%)`。新增 `position:fixed` 元素前，先確認其祖先鏈沒有 `transform`。

### JavaScript

- **整支 script 包在單一 IIFE**（`(function(){ "use strict"; ... })();`），不要模組化、不要建立全域變數，所有狀態靠 closure 共享。
- **一律用 `var`**，不要混用 `let`/`const`，維持風格一致。
- **函式一律用宣告式 `function foo(){}`**（不要用箭頭函式或函式表達式），依賴 hoisting 讓後面定義的函式可以被前面的程式呼叫。
- **固定亂數種子 `mulberry32(seed)`**：星星、星球斑駁紋理、土星環、放射粒子都是用不同的 hardcode 種子產生「看起來隨機但每次重繪都一樣」的資料，避免 resize/重繪時畫面跳動。新增任何視覺上「隨機分布但要固定不跳動」的元素，比照此模式。
- **「只建置一次」守衛模式**：`buildXxx()` 函式開頭要有 `if(xxxAlreadyBuilt) return;`，確保幾何/粒子資料只算一次，`resize()` 重複呼叫不會重算。
- **Canvas 渲染走單一 `frame(time)` 迴圈**，用 `requestAnimationFrame` 自我遞迴；圖層順序固定為：背景漸層 → 顆粒紋理(grain) → 星星 → 土星環 → 星球本體 → 放射粒子。新增圖層時依此順序插入，不要打亂既有疊圖邏輯。
- **任務狀態機**：`state` 只有 `idle | running | standby` 三種值，搭配 `remaining`（剩餘秒數）與 `criticalPhase`（是否進入最後 5 分鐘）兩個旗標。所有 UI 變化（按鈕啟停、太空人位置/跳動、粒子加速、星球跳動）都要從這些變數 derive，並集中透過 `syncMissionVisuals()` 同步，不要在各按鈕的 click handler 裡各自處理視覺效果。
- **顏色計算共用 `mixColor()` / `rgbaStr()`**：星球明暗、斑駁色調、粒子色都用這兩個 helper 做線性插值，不要手動拼 rgba 字串。
- **每個星球是一個 theme 物件**（`PLANET_THEMES` 裡的 `earth/mars/moon/jupiter/saturn`），欄位固定為 `bg / glow / rim / base / dayColor / nightColor / bands / rings`。新增星球比照這個 schema 填寫。

## 專案硬性規則（以後每次修改都必須遵守）

1. **背景永遠是深色星空**；主色（強調色）只用在當下要凸顯的那一個元素上，不要同時把主色套在多個元件，稀釋掉「這是重點」的訊號。
2. **星球與火箭一律用 canvas 或 CSS 手繪**，不得引用任何外部圖片（含 emoji 圖片、線上圖庫、CDN 圖檔）。目前的火箭與太空人圖示都是 inline SVG，新增/替換視覺元素時比照辦理。
3. **按鈕文案固定用航太語彙**：發射、待機、返航、補給。不要改用「開始/暫停/重置/加時間」之類的一般詞彙；未來若新增按鈕，也要從航太語彙裡挑詞，維持整體語感一致。
4. **倒數的分鐘數要放在檔案最上面當一個明確的設定值**（例如 `TOTAL_SECONDS`），不要把時間長度用 magic number 散落在程式碼各處。修改倒數長度時只改這一個地方就要能生效；新增跟時間相關的門檻（例如警示/危急階段的秒數）也應該一併集中管理，而不是各自硬編碼。
5. **所有中文文案一律使用繁體中文**，不得出現簡體字。此規則由 `.claude/hooks/check_traditional_chinese.py` 這支 PreToolUse hook 強制執行（設定在 `.claude/settings.json`）：寫入內容含簡體字時會直接擋下該次 Write/Edit。若要調整偵測用的簡體字表，改那支腳本裡的 `SIMPLIFIED_CHARS`。

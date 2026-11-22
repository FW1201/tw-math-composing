# 對接 tw-edu-skills 的研究交接

查核日期：2026-11-22；參考 [tw-edu-skills README](https://github.com/FW1201/tw-edu-skills) 及 [v5 撰寫規範](https://github.com/FW1201/tw-edu-skills/blob/main/docs/SKILL-AUTHORING-v5.md)。以下為規劃建議，尚未新增、安裝或修改任何 skill。

## 已觀察到的現有架構

- README 顯示 v5.0.1，獨立 skill 位於根目錄，以 schema、examples 與 CLI 為多數文件生成技能提供輸入、驗證、輸出；獨立安裝；由教師審查。
- v5 規範描述七個固定章節、frontmatter、共用 workflow 與 teacher-profile、references、語意關卡、路由測例及維持獨立運作的門檻。
- `tw-edu-exam-generator` 分學生卷與教師答案卷；`tw-edu-worksheet-creator`、`tw-edu-slides-creator`、`tw-edu-mini-app`、`tw-edu-material-reviewer` 及 `tw-edu-research-viz` 與數學圖文有潛在交接，但目前未逐一核對其 schema 的實際圖形支援。

## 候選邊界，供下階段決定

- 候選職責：接收明確數學約束與目標版面，生成／校驗數學圖形及公式資產，再交給試卷、學習單、簡報或網頁工具；不代替出題、教案設計或教師審題。
- 是否建一支統一 skill、數學繪圖與排版拆分，或先作為現有 skill 模式，須依真實頻率、獨立輸入／輸出和維護成本決定；尚未做決策。
- 可能名稱 `tw-edu-math-composing` 僅為候選，須確認命名、路由及系統整合約束。
- 路由正例：①「給我 115° 的量角器圖，保留可改參數」②「根據表格製作符合國中教材的直方圖」；近似反例：「依雙向細目表出整份段考」應以試卷 skill 主責，再視需要交接圖文。

## 實作前待決與驗證

1. 預期宿主、平台、離線與安裝限制；DOCX 原生公式／圖形、PPT、SVG、PDF、HTML 的實際可編輯性與互通性。
2. 數學物件描述與驗證格式、單位／座標／角度慣例、圖文分離及學生／教師版契約。
3. 優先學段、具代表性的教師原始需求、先實作的情境與最低驗收樣本。
4. 無障礙、授權與中文字型；選擇圖形和公式引擎前逐項驗證授權及匯出，不推定任一軟體能支援所有格式。
5. 依現行主 repo 的新增技能門檻、manifest、封裝、CI 與測試慣例重新確認；列出課綱證據來源及待核查項，避免用猜測補學習代碼。

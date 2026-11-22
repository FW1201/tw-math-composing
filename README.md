# 臺灣 K–12 數學圖形與排版研究

> **維護位置已移轉。** 自 v0.4.0 起，數學圖文與考卷技能在 [FW1201/tw-edu-skills](https://github.com/FW1201/tw-edu-skills/tree/main/tw-edu-math-composing) 發布，教案、學習單與簡報沿用套件原有技能。整併見 [PR #2](https://github.com/FW1201/tw-edu-skills/pull/2)。以下保留 v0.3.0 的歷史內容與研究入口。

本專案提供 [tw-edu-math-composing](tw-edu-math-composing/SKILL.md) v0.3.0，一支面向臺灣數學教師、可由教材設計、數學圖文或排版輸出開始的 skill。首版以國小、國中、普通高中三套可列印教材驗收。老師可以提供一份已有的題目請它排版，也可以只要求角度圖、數線、統計圖或可編輯公式。

把整個 `tw-edu-math-composing` 資料夾放在宿主的技能目錄即可使用。例：「使用 tw-edu-math-composing 製作一份國小四年級量角學習單，用黑白 A4 印，另附教師版。」所附 [輸出說明](tw-edu-math-composing/references/output.md) 含本機重製方法。可從 [三學段原創案例](tw-edu-math-composing/examples) 跑出 Word、PDF 與圖形來源。實測結果見 [首版驗收](research/v0.1-acceptance.md)。

- [情境目錄](research/scenarios.md)：按學段、視覺類型與驗收重點整理。
- [來源與課綱範圍](research/sources.md)：官方來源、版本及證據界線。
- [品質與測試需求](research/quality-and-cases.md)：數學正確、可讀、可編輯與測試案例。
- [既有系統整合交接](research/integration.md)：tw-edu-skills 架構與下一階段待決事項。

## 考卷字型與版面

考卷可指定字型及備用字型，並選擇單欄、雙欄或按題組混排。預設使用 Noto Serif TC、三層題號與純空白作答區，輸出附字型與版面紀錄。[設定及驗收方式](tw-edu-math-composing/references/output.md#字型與考卷分欄) · [分區混排示例](tw-edu-math-composing/examples/exam-layout.json) · [v0.2 驗收](research/v0.2-acceptance.md) · [左右題區示例](tw-edu-math-composing/examples/exam-fixed-columns.json)。

## 使用與範圍

國小 1–6、國中 7–9、普通高中 10–12 為主要盤點範圍；學段僅表示可能出現的情境，不構成每個年級的課綱判定。技術型、綜合型高中另有領綱，尚待逐條對照。K 指幼兒園：以操作和圖像為探索需求，尚未查核幼兒園課程綱要，不宣稱其屬於數學領綱。實際年級、課程類別、學習內容代碼與考試範圍應回查官方文件及教師提供教材。

清單為研究者根據來源與教學需求整理的**候選情境**，不是逐條官方課綱，也不保證涵蓋所有教科書或版本。第三方教材以連結和短篇描述索引，不在此複製課本圖或試題；重製前應確認權利。研究查核日期：2026-11-22。

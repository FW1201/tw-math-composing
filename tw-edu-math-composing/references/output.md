# 排版輸出與教材資料

輸出以繁中 A4 為預設。維持題幹、公式、圖與必要表格在同一作答脈絡。教師版加答案與提示，學生版採白名單組裝。學生交付時只傳學生檔及必要圖文來源。

教材來源為 UTF-8 JSON。上層有 `version: 1`、`title`、`stage`、`purpose`、`sources`、`items`。每題有唯一 `id`、`prompt`，可含 `formula`、`figure`、`table`、`answer_lines` 及教師專用 `answer`。公式輸入含 `latex` 與 `parts`，可用字串、`frac`、`sup`、`matrix`、`system` 組成。樣例展示各圖形類型和參數。學生來源會移除教師專用欄位。檔案只在指定輸出目錄內產生。

```bash
python3 -m pip install python-docx Pillow
python3 scripts/compose.py examples/elementary.json --validate-only
python3 scripts/compose.py examples/elementary.json --output /path/to/artifacts
```

內附工具用 Python 3.10+、python-docx、Pillow 和 soffice。可用 `--no-pdf` 僅輸出 DOCX，或用 `--figures-only` 只輸出 SVG。需要完整圖文時驗證所有工具可用，再生成。公式是 Word 原生 OMML，表格與文字是 Word 物件，數學圖可從 SVG 與參數重製。超出內建圖形種類時，可用其他本機工具產生 SVG，再依相同題號、來源與學生版規則交付。

逐份開啟後看 A4 黑白、題圖距離、表格欄底、可寫空間、公式上下標與字型。PDF 應與 DOCX 內容一致。聲稱可編輯前，在 Word 選取公式並更改一項，再重新開啟確認結構仍在。任何未執行的檢驗需標出。

## 字型與考卷分欄

在來源 JSON 的 `layout` 記錄字型與版面。舊資料沒有這一欄時，以 Noto Sans TC、單欄輸出。

```json
{
  "layout": {
    "font_family": "Noto Sans TC",
    "fallback_font_family": "Noto Sans TC",
    "mode": "mixed",
    "zones": [
      {"start_item": "A1", "columns": 2, "title": "第一部分｜短題"},
      {"start_item": "B1", "columns": 1, "title": "第二部分｜圖表與推理"}
    ]
  }
}
```

- **單欄 `single`**：全部題目全寬，適合題幹較長、寬表格、大圖或手寫推導。
- **雙欄 `double`**：全部題目雙欄，封面標題和學生欄位保留全寬。題目依左欄往下、再右欄往下的順序流動。適合較短的題目。
- **分區混排 `mixed`**：每區從指定的 `start_item` 開始，直到下一區，標題可省略。第一區從首題開始，各區起始題號依原題序且不重複，須包含單欄和雙欄。題組標題全寬，同一題的 `page_break: true` 可讓該區或題目另起一頁。

使用 Word 原生分節分欄，學生版及教師版各自流動，同一份題目的頁碼可能因此不同。圖形、表格及作答線依欄寬縮放，避免窄欄溢出。遇到寬公式、密集表頭或需要手寫的長題，移到單欄區並重新檢查 PDF。可由 [示範輸入](../examples/exam-layout.json) 重製混排，或改成 `single`、`double` 並移除 `zones`。

指定字型用於正文、標題與圖表標籤，公式沿用 Word 的數學字型。產生器若能用 `fc-match` 確認字型已安裝，會採用指定字型，找不到時試用設定的備用字型。無法確認時會在終端與 `render-report.json` 提示。若有 `pdffonts`，報告也列出 PDF 實際使用及內嵌的字型。逐頁查看輸出，仍是檢查缺字及排版的依據。

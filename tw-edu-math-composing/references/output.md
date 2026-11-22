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

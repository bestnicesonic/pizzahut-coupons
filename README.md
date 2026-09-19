# Pizza Hut 必勝客官方即時優惠券數據源

> 專為《必勝客優惠券速查指南》打造的免維護、零依賴雲端影子後端。

* **數據來源**：必勝客台灣官方促銷專區 (`https://www.pizzahut.com.tw/promotions/?mode=cpSch&type=plu&fm=hicon`)
* **排程時段**：台灣時間 08:00 ～ 24:00 每小時自動抓取一次（包含 00:00 跨日換檔）；凌晨 01:00 ～ 07:00 門市打烊休眠不跑。
* **即時 CDN 存取網址 (CORS 開放)**：
  `https://raw.githubusercontent.com/bestnicesonic/pizzahut-coupons/main/pizzahut_official.json`

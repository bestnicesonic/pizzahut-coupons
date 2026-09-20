import urllib.request
import re
import json
import os
from datetime import datetime, timezone, timedelta

URL = "https://www.pizzahut.com.tw/promotions/?mode=cpSch&type=plu&fm=hicon"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.pizzahut.com.tw/"
}

TZ_TW = timezone(timedelta(hours=8))

def crawl():
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        html = resp.read().decode('utf-8', errors='ignore')

    sections = re.findall(r'<details[^>]*id=["\']content_list_(\d+)["\'][^>]*>.*?<h3[^>]*class=["\']arrowTitle["\'][^>]*>(.*?)</h3>.*?(.*?)</details>', html, re.DOTALL)
    coupons = []

    for sec_id, sec_title, sec_content in sections:
        sec_title = sec_title.strip()
        items = re.findall(r'<div[^>]*class=["\']pdpop-li["\'][^>]*data-plu=["\']([^"\']+)["\'][^>]*>(.*?)</div>\s*</div>\s*(?=<div class=["\']pdpop-li|$)', sec_content, re.DOTALL)
        
        for plu, item_html in items:
            img_m = re.search(r'<img[^>]+src=["\']([^"\']+)["\']', item_html)
            img_url = img_m.group(1) if img_m else ""
            if img_url and img_url.startswith("//"):
                img_url = "https:" + img_url
                
            name_m = re.search(r'class=["\']pdpop-name["\'][^>]*>(.*?)</p>', item_html, re.DOTALL)
            name = name_m.group(1).strip() if name_m else ""
            clean_name = re.sub(rf'^{plu}\s*[-–—:]\s*', '', name)
            
            desc_m = re.search(r'class=["\']pdpop-price["\'][^>]*>(.*?)</div>', item_html, re.DOTALL)
            desc = desc_m.group(1).strip() if desc_m else ""
            desc = re.sub(r'</?(?:br|div|p)[^>]*>', ' ', desc)
            desc = re.sub(r'\s+', ' ', desc).strip()
            
            price_m = re.search(r'\$(\d+)', desc) or re.search(r'\$(\d+)', name)
            price = price_m.group(1) if price_m else "0"
            
            coupons.append({
                "couponCode": str(plu),
                "name": clean_name or name,
                "fullName": name,
                "price": price,
                "description": desc,
                "category": sec_title,
                "imageUrl": img_url,
                "orderUrl": f"https://www.pizzahut.com.tw/order/?mode=step_2&type_id=1025&cno={plu}",
                "isOfficial": True,
                "source": "必勝客官方促銷"
            })

    # 讀取現有檔案，比對促銷內容是否有實質變動
    existing_file = "pizzahut_official.json"
    is_changed = True
    now_tw = datetime.now(TZ_TW)
    
    if os.path.exists(existing_file):
        try:
            with open(existing_file, "r", encoding="utf-8") as f:
                old_data = json.load(f)
            old_coupons = old_data.get("coupons", [])
            # 比較代碼與價格
            old_summary = [(c.get("couponCode"), c.get("price"), c.get("name")) for c in old_coupons]
            new_summary = [(c.get("couponCode"), c.get("price"), c.get("name")) for c in coupons]
            
            if old_summary == new_summary:
                is_changed = False
                print("Promotions unchanged.")
                
                # 檢查是否需要觸發 30 天防休眠心跳 (Heartbeat Keepalive)
                last_updated_str = old_data.get("updated_at", "")
                if last_updated_str:
                    try:
                        last_updated = datetime.fromisoformat(last_updated_str)
                        if (now_tw - last_updated).days >= 30:
                            print("30 days without updates, triggering Heartbeat Keepalive commit!")
                            is_changed = True
                    except Exception:
                        pass
        except Exception as e:
            print("Error reading existing file, forcing update:", e)
            is_changed = True

    if is_changed:
        output_data = {
            "updated_at": now_tw.isoformat(),
            "total": len(coupons),
            "coupons": coupons
        }
        with open(existing_file, "w", encoding="utf-8") as f:
            json.dump(output_data, f, ensure_ascii=False, indent=2)
        print(f"pizzahut_official.json updated! Total coupons: {len(coupons)}")
    else:
        print("Skipping file write to keep Git commit history clean.")

if __name__ == "__main__":
    crawl()

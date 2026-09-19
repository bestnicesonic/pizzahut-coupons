import urllib.request
import re
import json
from datetime import datetime

URL = "https://www.pizzahut.com.tw/promotions/?mode=cpSch&type=plu&fm=hicon"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Referer": "https://www.pizzahut.com.tw/"
}

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

    output_data = {
        "updated_at": datetime.now().isoformat(),
        "total": len(coupons),
        "coupons": coupons
    }

    with open("pizzahut_official.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"Crawl finished, total: {len(coupons)}")

if __name__ == "__main__":
    crawl()

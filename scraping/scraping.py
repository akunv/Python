import requests
from bs4 import BeautifulSoup
import urllib.parse
import urllib3
import io
import time
import csv
import re
import pdfplumber

# SSL警告を非表示にする
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# ==========================================
# 設定
# ==========================================
BASE_LIST_URL = 'https://xd-web.kutc.kansai-u.ac.jp/teacher/2025m2p7b6q9e1/id/index.html'
TEST_MODE = False
TEST_LIMIT = 5
OUTPUT_CSV = 'thesis_list_cleaned.csv'

# ==========================================
# 関数定義
# ==========================================
def get_soup(url):
    try:
        response = requests.get(url, verify=False, timeout=10)
        response.encoding = response.apparent_encoding
        if response.status_code == 200:
            return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"アクセスエラー ({url}): {e}")
    return None

def clean_title(raw_text):
    """
    抽出された生のテキストから、タイトル部分だけを正規表現で切り出す。
    例: "情22-0001 青木 綾音 2025 年度 卒業研究 1／2 関大総情のメタバースオープンキャンパスの実装研究 情 22-0001 青木 綾音"
    → "関大総情のメタバースオープンキャンパスの実装研究"
    """
    if not raw_text:
        return "抽出不可"

    # 改行や余計な空白を1つの半角スペースに統一
    text = re.sub(r'\s+', ' ', raw_text).strip()

    # パターン： 「1／2」や「1 / 2」のようなページ番号表記の後から、
    # 末尾にある「情22-0001」のような学籍番号らしき文字列の前までを抽出する
    
    # 1. 「〇/〇」または「〇／〇」の直後を探す
    match_start = re.search(r'\d\s*[／/]\s*\d\s+(.+)', text)
    if match_start:
        candidate = match_start.group(1)
        
        # 2. 末尾にある「情 22-0001」や「情22-0001」以降を削る
        # (?:情|情\s*)\d{2}-\d{4} というパターンで学籍番号を検知
        candidate = re.split(r'(?:情|情\s*)\d{2}-\d{4}', candidate)[0].strip()
        
        return candidate
    
    # もし想定したパターン（1/2など）が見つからない場合は、そのまま返す
    return text

def extract_title_from_pdf(pdf_url):
    try:
        response = requests.get(pdf_url, verify=False, timeout=15)
        if response.status_code != 200:
            return "ダウンロード失敗"

        pdf_file = io.BytesIO(response.content)
        
        # PyPDF2からpdfplumberに変更（文字化けに強く、レイアウト崩れしにくい）
        with pdfplumber.open(pdf_file) as pdf:
            first_page = pdf.pages[0]
            # layout=True にすると、見た目の行の並びに近く抽出される
            text = first_page.extract_text(layout=True)
            
        if not text:
            return "テキスト抽出不可"

        # ページ上部の数行（文字が密集している部分）を結合
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        raw_top_text = " ".join(lines[:6]) # 少し余裕を持たせて6行分結合
        
        # クリーニング関数に通す
        clean_t = clean_title(raw_top_text)
        
        return clean_t

    except Exception as e:
        return f"PDF解析エラー: {e}"

# ==========================================
# メイン処理
# ==========================================
def main():
    print("スクレイピングを開始します...")
    
    soup_index = get_soup(BASE_LIST_URL)
    if not soup_index:
        return

    group_urls = []
    for a_tag in soup_index.find_all('a'):
        href = a_tag.get('href', '')
        if href.startswith('id_'):
            full_url = urllib.parse.urljoin(BASE_LIST_URL, href)
            group_urls.append(full_url)

    pdf_links = []
    for g_url in group_urls:
        g_soup = get_soup(g_url)
        if not g_soup:
            continue
            
        for a_tag in g_soup.find_all('a'):
            href = a_tag.get('href', '')
            if '.pdf' in href.lower():
                full_pdf_url = urllib.parse.urljoin(g_url, href)
                student_name = a_tag.text.strip()
                pdf_links.append({
                    'name': student_name,
                    'url': full_pdf_url
                })
        time.sleep(1)

    print(f"合計 {len(pdf_links)} 件のPDFリンクを抽出しました。\n")
    process_list = pdf_links[:TEST_LIMIT] if TEST_MODE else pdf_links

    with open(OUTPUT_CSV, mode='w', encoding='utf-8-sig', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(['学籍番号・氏名', 'PDF_URL', '抽出タイトル'])

        for i, item in enumerate(process_list, 1):
            print(f"[{i}/{len(process_list)}] {item['name']} を処理中...")
            
            title = extract_title_from_pdf(item['url'])
            print(f"  > {title}")
            
            writer.writerow([item['name'], item['url'], title])
            time.sleep(2)

    print(f"\n完了しました！ 結果は '{OUTPUT_CSV}' に保存されています。")

if __name__ == "__main__":
    main()
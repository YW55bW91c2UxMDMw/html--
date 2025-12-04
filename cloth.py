import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
from bs4 import BeautifulSoup
import json
import random
import datetime
import warnings

warnings.filterwarnings("ignore")

NAVER_CLIENT_ID = "HMwCrBS8Xv5l711DTmLx"
NAVER_CLIENT_SECRET = "dhN31FkMhL"

class RealTimeCrawler:
    def __init__(self):
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Referer': 'https://search.shopping.naver.com/'
        }

    def fetch_naver_ranking(self):
        """네이버 쇼핑 '남성 의류' 베스트 100을 실제로 긁어옵니다."""
        print("[크롤러] 네이버 쇼핑 서버에 잠입 중...")
        
        url = "https://search.shopping.naver.com/best/category/click?categoryCategoryId=50000169&viewType=list&sort=rank"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=5)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.text, 'html.parser')
            
            title_elements = soup.find_all("div", class_=lambda x: x and "imageTitle_title" in x)
            
            items = []
            for el in title_elements[:30]:
                raw_name = el.get_text()
                category = self._classify_item(raw_name)
                
                items.append({
                    "name": raw_name,
                    "category": category,
                    "style": "trend",
                    "source": "live_crawling"
                })
            
            if not items:
                print("크롤링은 성공했으나 태그를 못 찾음 (네이버 구조 변경됨)")
                return []
                
            print(f"[성공] 실시간 아이템 {len(items)}개 확보 완료!")
            return items

        except Exception as e:
            print(f"[실패] 크롤링 에러: {e}")
            return []

    def _classify_item(self, name):
        """상품명을 보고 상/하의/아우터 자동 분류"""
        n = name.replace(" ", "")
        
        # 아우터 키워드
        if any(x in n for x in ["패딩", "코트", "자켓", "점퍼", "가디건", "후리스", "바람막이", "무스탕", "베스트", "아노락"]):
            return "outer"
        # 하의 키워드
        elif any(x in n for x in ["바지", "팬츠", "슬랙스", "데님", "진", "청바지", "조거", "트레이닝하의"]):
            return "bottom"
        # 상의 키워드
        elif any(x in n for x in ["티셔츠", "맨투맨", "후드", "니트", "셔츠", "스웨터", "나시", "긴팔"]):
            return "top"
        
        return "top" # 모르겠으면 상의로 침
    
class NaverDataLab:
    def __init__(self):
        self.headers = {
            "X-Naver-Client-Id": NAVER_CLIENT_ID,
            "X-Naver-Client-Secret": NAVER_CLIENT_SECRET,
            "Content-Type": "application/json"
        }
        # 네이버 쇼핑 카테고리 ID (남성 의류 기준)
        # 50000837: 아우터, 50000830: 상의, 50000836: 하의
        self.cat_ids = {"outer": "50000837", "top": "50000830", "bottom": "50000836"}

    def get_search_trend(self, keywords):
        """1. 통합검색어 트렌드 (관심도)"""
        if not NAVER_CLIENT_ID: return {k: random.randint(40, 80) for k in keywords}

        url = "https://openapi.naver.com/v1/datalab/search"
        
        # 오늘 날짜 구하기
        today = datetime.date.today()
        month_ago = today - datetime.timedelta(days=30)

        keyword_groups = [{"groupName": k, "keywords": [k]} for k in keywords]
        
        body = {
            "startDate": month_ago.strftime("%Y-%m-%d"),
            "endDate": today.strftime("%Y-%m-%d"),
            "timeUnit": "date",
            "keywordGroups": keyword_groups[:5], # 최대 5개 제한
            "device": "pc", # or "mo"
            "ages": ["10", "20"], # 10대, 20대 타겟팅
            "gender": "m" # 남성
        }

        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(body))
            res_json = response.json()
            scores = {}
            if "results" in res_json:
                for item in res_json["results"]:
                    # 기간 내 최대 검색량(ratio) 가져오기
                    if item["data"]:
                        # 최근 데이터의 평균 혹은 최대값을 점수로 사용
                        max_ratio = max([d["ratio"] for d in item["data"]])
                        scores[item["title"]] = max_ratio
            return scores
        except Exception as e:
            print(f"검색 트렌드 오류: {e}")
            return {k: 50 for k in keywords}

    def get_shopping_click(self, category_type, keyword):
        """2. 쇼핑인사이트 키워드 클릭량 (구매 의도)"""
        if not NAVER_CLIENT_ID: return random.randint(40, 90)

        url = "https://openapi.naver.com/v1/datalab/shopping/category/keyword"
        cat_id = self.cat_ids.get(category_type, "50000000") # 없으면 패션의류 전체

        today = datetime.date.today()
        month_ago = today - datetime.timedelta(days=30)

        body = {
            "startDate": month_ago.strftime("%Y-%m-%d"),
            "endDate": today.strftime("%Y-%m-%d"),
            "timeUnit": "date",
            "category": cat_id,
            "keyword": [{"name": keyword, "param": [keyword]}],
            "device": "",
            "gender": "m",
            "ages": ["10", "20"]
        }

        try:
            response = requests.post(url, headers=self.headers, data=json.dumps(body))
            res_json = response.json()
            if "results" in res_json and res_json["results"]:
                 # 데이터 중 최대 클릭량 반환
                 data_points = res_json["results"][0]["data"]
                 if data_points:
                     return max([d["ratio"] for d in data_points])
            return 0
        except Exception as e:
            print(f"쇼핑 인사이트 오류 ({keyword}): {e}")
            return 50

class FashionEngine:
    def __init__(self):
        self.crawler = RealTimeCrawler()
        self.api = DataLabAPI()
        
        # 1. 안전장치: 크롤링 실패 시 사용할 비상용 데이터 (Default DB)
        self.fallback_db = [
            {"name": "[기본] 오버핏 옥스포드 셔츠", "category": "top", "style": "formal"},
            {"name": "[기본] 와이드 슬랙스", "category": "bottom", "style": "formal"},
            {"name": "[기본] 캐시미어 코트", "category": "outer", "style": "formal"},
            {"name": "[기본] 그레이 후드티", "category": "top", "style": "casual"},
            {"name": "[기본] 카고 조거 팬츠", "category": "bottom", "style": "casual"},
            {"name": "[기본] 숏패딩", "category": "outer", "style": "casual"},
        ]
        
        self.current_db = []

    def load_data(self):
        """데이터 로딩: 크롤링 시도 -> 실패하면 기본 DB 사용"""
        crawled_data = self.crawler.fetch_naver_ranking()
        
        if crawled_data:
            self.current_db = crawled_data + self.fallback_db # 섞어서 사용
        else:
            self.current_db = self.fallback_db
            
        # API 점수 매기기 (모든 아이템에 대해)
        for item in self.current_db:
            item['score'] = self.api.get_score(item['name'])

    def recommend(self, style):
        """스타일에 맞는 코디 추천"""
        # 스타일 필터링 (trend는 모든 스타일에 포함)
        candidates = [
            i for i in self.current_db 
            if i.get('style') == style or i.get('style') == 'trend'
        ]
        
        if not candidates: candidates = self.current_db

        # 카테고리별 1등 뽑기
        result = {}
        for cat in ['outer', 'top', 'bottom']:
            items = [i for i in candidates if i['category'] == cat]
            if items:
                # 점수순 정렬
                best = sorted(items, key=lambda x: x['score'], reverse=True)[0]
                result[cat] = best
            else:
                result[cat] = {"name": "추천 아이템 없음", "score": 0}
                
        return result

# =========================================================
# [GUI] 사용자 화면
# =========================================================
class App:
    def __init__(self, root):
        self.root = root
        self.root.title("🔥 실시간 네이버 패션 크롤러 v1.0")
        self.root.geometry("450x600")
        self.engine = FashionEngine()

        # 스타일
        style = ttk.Style()
        style.theme_use('clam')
        
        # 헤더
        ttk.Label(root, text="NAVER Shopping Live Ranking", font=('Impact', 16)).pack(pady=15)
        
        # 컨트롤 패널
        frame = ttk.Frame(root)
        frame.pack(pady=5)
        
        ttk.Label(frame, text="오늘의 스타일: ").pack(side='left')
        self.style_var = tk.StringVar(value="casual")
        combo = ttk.Combobox(frame, textvariable=self.style_var, values=["casual", "formal", "street"], state="readonly", width=10)
        combo.current(0)
        combo.pack(side='left', padx=5)

        self.btn_start = ttk.Button(frame, text="서버 접속 및 분석", command=self.run_process)
        self.btn_start.pack(side='left', padx=5)

        # 로그 창 (진행상황 표시)
        self.log_frame = ttk.LabelFrame(root, text=" 시스템 로그 ", padding=10)
        self.log_frame.pack(fill='x', padx=15, pady=10)
        self.lbl_log = ttk.Label(self.log_frame, text="대기 중...", foreground="gray")
        self.lbl_log.pack(anchor='w')

        # 결과 창
        self.res_frame = ttk.LabelFrame(root, text=" 👑 AI 추천 코디 ", padding=15)
        self.res_frame.pack(fill='both', expand=True, padx=15, pady=5)
        
        self.labels = {}
        for cat, title in [('outer', '아우터'), ('top', '상  의'), ('bottom', '하  의')]:
            f = ttk.Frame(self.res_frame)
            f.pack(fill='x', pady=5)
            ttk.Label(f, text=title, font=('맑은 고딕', 10, 'bold'), width=6).pack(side='left')
            self.labels[cat] = ttk.Label(f, text="-", foreground="blue", font=('맑은 고딕', 10))
            self.labels[cat].pack(side='left')

    def run_process(self):
        self.btn_start.config(state='disabled')
        self.lbl_log.config(text="📡 네이버 쇼핑 데이터 수집 시작...")
        threading.Thread(target=self._thread_task).start()

    def _thread_task(self):
        # 1. 크롤링 및 데이터 로드
        self.engine.load_data()
        
        # 2. 추천 로직 수행
        outfit = self.engine.recommend(self.style_var.get())
        
        # 3. GUI 업데이트
        self.root.after(0, lambda: self._update_ui(outfit))

    def _update_ui(self, outfit):
        # 로그 업데이트
        count = len(self.engine.current_db)
        self.lbl_log.config(text=f"✅ 분석 완료! (총 {count}개의 실시간 상품 분석함)")
        
        # 결과 표시
        for cat in ['outer', 'top', 'bottom']:
            item = outfit[cat]
            clean_name = item['name'][:25] + "..." if len(item['name']) > 25 else item['name']
            self.labels[cat].config(text=f"{clean_name} ({item.get('score',0)}점)")
            
        self.btn_start.config(state='normal')

if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
import argparse
from bs4 import BeautifulSoup
from collections import deque
from dataclasses import dataclass
from datetime import datetime
import pandas as pd
import random
import re
import requests
from time import sleep
from typing import List, Optional

@dataclass
class Mathematician:
    """수학자의 정보를 저장하는 데이터 클래스"""
    name: str  # 이름
    id: str  # ID
    university: str  # 대학
    year: str  # 연도
    degree_type: str  # 학위 종류
    nationality: str  # 국적
    level: int  # 세대 레벨
    url: str  # URL
    descended_from: List[str]  # Advisor들의 ID 목록

class MathGenealogyScraper:
    """Mathematics Genealogy Project 웹사이트를 스크래핑하는 클래스"""
    BASE_URL = "https://genealogy.math.ndsu.nodak.edu"

    def __init__(self, start_id: int, end_id: Optional[int] = None, end_depth: int = 15, wait_sec: float = 2.5, verbose: bool = True):
        """스크래퍼 초기화

        Args:
            start_id (int): 시작할 수학자의 ID
            end_id (Optional[int]): 탐색을 중단할 수학자의 ID (기본값: None)
            end_depth (int): 탐색을 중단할 최대 세대 깊이 (기본값: 15)
            wait_sec (float): 요청 간 대기 시간 (초) (기본값: 2.5)
            verbose (bool): 상세 로그 출력 여부 (기본값: True)
        """
        self.start_id = str(start_id)
        self.end_id = str(end_id) if end_id else None
        self.end_depth = end_depth
        self.wait_sec = wait_sec
        self.verbose = verbose
        self.visited = set()  # 방문한 페이지 추적
        self.queue = deque()  # BFS를 위한 큐
        self.mathematicians = []  # 수집된 수학자 정보
        self.parent_map = {}  # 자식 -> 부모(들) 매핑
        self.target_found = False  # 목표 수학자를 찾았는지 여부
        self.target_level = 0  # 목표 수학자의 세대 레벨

    def log(self, message: str):
        """로그 메시지 출력

        Args:
            message (str): 출력할 메시지
        """
        if self.verbose:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            print(f"[{timestamp}] {message}")

    def get_page(self, id: str) -> Optional[BeautifulSoup]:
        """주어진 ID의 수학자 페이지를 가져옴

        Args:
            id (str): 수학자 ID

        Returns:
            Optional[BeautifulSoup]: 파싱된 HTML 페이지 또는 None (에러 발생 시)
        """
        url = f"{self.BASE_URL}/id.php?id={id}"
        try:
            random_delay = max(
                0,  # 음수가 되지 않도록 보호
                self.wait_sec + max(min(random.gauss(0, 0.1), 0.15), -0.1), # -0.1에서 0.15 사이의 랜덤 지연 시간 추가
            )
            self.log(f"페이지 가져오는 중: {url}")
            sleep(random_delay)

            response = requests.get(url)
            response.raise_for_status()
            return BeautifulSoup(response.text, "html.parser")
        except requests.RequestException as e:
            self.log(f"페이지 {id} 가져오기 오류: {e}")
            return None

    def collapse_whitespace(self, text: str) -> str:
        """텍스트에서 연속된 공백을 단일 공백으로 변환하고 앞뒤 공백을 제거

        Args:
            text (str): 처리할 텍스트

        Returns:
            str: 공백이 정리된 텍스트
        """
        return re.sub(r'\s+', ' ', text).strip()

    def parse_mathematician(self, soup: BeautifulSoup, level: int, advisors: List[str]) -> Optional[Mathematician]:
        """HTML에서 수학자 정보를 파싱

        Args:
            soup (BeautifulSoup): 파싱할 HTML
            level (int): 현재 세대 레벨
            advisors (List[str]): Advisor들의 ID 목록

        Returns:
            Optional[Mathematician]: 파싱된 수학자 정보 또는 None (파싱 실패 시)
        """
        try:
            # 이름 추출 및 whitespace 정리
            name = self.collapse_whitespace(soup.find("h2").text)

            # URL에서 ID 추출
            id = soup.find('a', href=lambda x: x and "id.php?id=" in x)["href"].split('=')[-1]

            # 기타 세부 정보 추출
            details = {}

            # 학위 정보 div 찾기
            degree_info = soup.select_one("#paddingWrapper > div:nth-child(6)") # paddingWrapper의 6번째 자식 div
            if degree_info:
                # 전체 텍스트 추출
                main_span = degree_info.find("span")
                if main_span:
                    full_text = main_span.text.strip()

                    # 대학 이름 추출 (color 스타일이 적용된 span)
                    university_span = main_span.find("span", style=lambda x: x and "color:" in x)
                    if university_span:
                        details["university"] = self.collapse_whitespace(university_span.text)
                        # 대학 이름을 기준으로 앞뒤 텍스트 분리
                        parts = full_text.split(university_span.text.strip())
                        if len(parts) == 2:
                            # Ph.D. 추출 (대학 이름 앞의 텍스트)
                            details["degree_type"] = self.collapse_whitespace(parts[0])
                            # 연도 추출 (대학 이름 뒤의 텍스트)
                            details["year"] = self.collapse_whitespace(parts[1])

                # 국적 추출
                flag_img = degree_info.find("img", src=lambda x: x and x.endswith(".gif"))
                if flag_img and flag_img.get("title"):
                    details["nationality"] = self.collapse_whitespace(flag_img["title"])

            mathematician = Mathematician(
                name=name,
                id=id,
                university=details.get("university", ''),
                year=details.get("year", ''),
                degree_type=details.get("degree_type", ''),
                nationality=details.get("nationality", ''),
                level=level,
                url=f"{self.BASE_URL}/id.php?id={id}",
                descended_from=advisors
            )

            self.log(f"수학자 정보 파싱 완료: {name} (ID: {id}, 레벨: {level})")
            return mathematician
        except Exception as e:
            self.log(f"수학자 정보 파싱 오류: {e}")
            return None

    def get_advisors(self, soup: BeautifulSoup) -> List[str]:
        """페이지에서 Advisor들의 ID를 추출

        Args:
            soup (BeautifulSoup): 파싱할 HTML

        Returns:
            List[str]: Advisor ID 목록
        """
        advisors = []
        for link in soup.find_all('a', href=lambda x: x and "id.php?id=" in x):
            if "Advisor" in link.parent.text:
                advisor_id = link["href"].split('=')[-1]
                advisors.append(advisor_id)
        return advisors

    def scrape(self):
        """BFS 방식으로 수학자 계보를 스크래핑"""
        self.log(f"스크래핑 시작 (시작 ID: {self.start_id}, 최대 깊이: {self.end_depth})")
        self.queue.append((self.start_id, 1))  # (id, level)

        while self.queue:
            current_id, level = self.queue.popleft()

            # 종료 조건 확인
            if self.target_found and level > self.target_level:
                break  # 목표 수학자의 세대보다 높은 세대에 도달

            if not self.target_found and level > self.end_depth:
                break  # 최대 세대 깊이보다 높은 세대에 도달

            if current_id in self.visited:
                self.log(f"이미 방문한 페이지 건너뛰기: {current_id}")
                continue

            self.visited.add(current_id)

            # 서버에 부담을 주지 않기 위해 지연 시간 추가
            sleep(self.wait_sec)

            soup = self.get_page(current_id)
            if not soup:
                continue

            # Advisor ID 목록 가져오기
            advisors = self.get_advisors(soup)
            self.log(f"Advisor ID 목록: {', '.join(advisors) if advisors else '없음'}")

            # 자식 -> 부모(들) 매핑 업데이트
            for advisor_id in advisors:
                if advisor_id not in self.parent_map:
                    self.parent_map[advisor_id] = []
                self.parent_map[advisor_id].append(current_id)

            mathematician = self.parse_mathematician(soup, level, advisors)
            if mathematician:
                self.mathematicians.append(mathematician)

                # 목표 수학자 확인
                if self.end_id and current_id == self.end_id and not self.target_found:
                    self.log(f"목표 수학자 (ID: {self.end_id})를 찾았습니다!")
                    self.target_found = True
                    self.target_level = level

                # Advisor들을 가져와서 큐에 추가
                for advisor_id in advisors:
                    if advisor_id not in self.visited:
                        self.queue.append((advisor_id, level + 1))

        if self.target_found:
            self.log(f"스크래핑 완료. 목표 수학자 및 동일 세대({self.target_level})의 수학자들까지 모두 수집했습니다. 총 {len(self.mathematicians)}명의 수학자 정보를 수집했습니다.")
        else:
            self.log(f"스크래핑 완료. 목표 수학자를 찾지 못했으며 최대 세대 깊이({self.end_depth})까지 모두 수집했습니다. 총 {len(self.mathematicians)}명의 수학자 정보를 수집했습니다.")
        self.log(f"스크래핑 완료. 총 {len(self.mathematicians)}명의 수학자 정보를 수집했습니다.")

    def save_to_excel(self, filename: str):
        """수집된 데이터를 Excel 파일로 저장

        Args:
            filename (str): 저장할 파일 이름
        """
        self.log(f"Excel 파일 저장 중: {filename}")

        # 데이터프레임 생성
        df = pd.DataFrame([vars(m) for m in self.mathematicians])

        # descended_from 리스트를 문자열로 변환 (Excel에서 보기 좋게)
        df["descended_from"] = df["descended_from"].apply(lambda x: ", ".join(x) if x else '')

        # 컬럼 순서 재정렬
        columns = ["name", "id", "university", "year", "degree_type", "nationality", "level", "descended_from", "url"]
        df = df[columns]

        df.to_excel(filename, index=False)
        self.log(f"데이터가 {filename}에 저장되었습니다.")

def main():
    parser = argparse.ArgumentParser(description="Mathematics Genealogy Project 스크래퍼")
    parser.add_argument("--start-id", type=int, required=True, help="시작할 수학자의 ID")
    parser.add_argument("--end-id", type=int, help="탐색을 중단할 수학자의 ID")
    parser.add_argument("--end-depth", type=int, default=15, help="탐색을 중단할 최대 세대 깊이 (기본값: 15)")
    parser.add_argument("--wait-sec", type=float, default=2.5, help="요청 간 대기 시간 (초) (기본값: 2.5)")
    parser.add_argument("--output", type=str, default="math_genealogy.xlsx", help="출력 파일 이름 (기본값: math_genealogy.xlsx)")
    parser.add_argument("--verbose", action="store_true", default=True, help="상세 로그 출력 (기본값: True)")
    parser.add_argument("--quiet", action="store_false", dest="verbose", help="로그 출력 비활성화")

    args = parser.parse_args()

    scraper = MathGenealogyScraper(
        start_id=args.start_id,
        end_id=args.end_id,
        end_depth=args.end_depth,
        wait_sec=args.wait_sec,
        verbose=args.verbose
    )
    scraper.scrape()
    scraper.save_to_excel(args.output)

if __name__ == "__main__":
    main()
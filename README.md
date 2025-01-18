# Mathematics Genealogy Project Scraper

이 프로젝트는 [Mathematics Genealogy Project 웹사이트](https://genealogy.math.ndsu.nodak.edu/index.php)를 스크래핑하여 수학자들의 학문적 계보를 너비 우선 탐색(BFS) 방식으로 추적합니다.
This project scrapes the [Mathematics Genealogy Project website](https://genealogy.math.ndsu.nodak.edu/index.php) to trace the academic lineage of mathematicians using a breadth-first search approach.
이 레포에는 계보를 그래프로 만들어주는 그런 심화된 기능 같은 것은 없습니다. No, this repo doesn't have any advanced functionality to graph the lineage.
이는 단순히 흥미삼아 당신이 옛날 저명한 학자(예: 레온하르트 오일러)의 몇대손인지 간단히 알아보고 싶을 때에나 쓸만한 아주 간단한 코드입니다. This is very simple pieces of code that you can use just for fun, for example, when you want to find out how many generations of famous scholars you are descended from Leonhard Euler.

## 기능 Features

- 시작 수학자부터 특정 수학자 또는 최대 세대 깊이까지의 학문적 계보 추적 Traces academic lineage from a starting mathematician up to a target mathematician or maximum depth
- 다음 정보 수집 Collects information including:
  - 학자의 이름 Name of Scholar
  - 아이디 ID
  - 대학 University
  - 연도 Year
  - 학위 종류 Degree type
  - 국적 Nationality
  - 세대 레벨 Generation level
  - Advisor들의 ID 목록 List of advisor IDs
- 결과를 Excel 파일로 저장 Saves results to an Excel file
- 상세한 진행 상황 로깅 Detailed progress logging with timestamps

## 요구사항 Requirements

- Python 3.7+
- `requirements.txt`에 명시된 패키지들 Required packages listed in `requirements.txt`

## 설치 방법 Installation

1. 이 저장소를 클론합니다 Clone this repository
2. 필요한 패키지들을 설치합니다 Install required packages:
```bash
pip install -r requirements.txt
```

## 사용 방법 Usage

기본 사용법 Basic usage:
```bash
python scraper.py --start-id START_ID
```

예시 Examples:
```bash
# 기본 사용 (최대 15세대까지 탐색)
python scraper.py --start-id 12345

# 특정 수학자까지 탐색 (예: 오일러)
python scraper.py --start-id 12345 --end-id 38586

# 최대 세대 깊이 지정
python scraper.py --start-id 12345 --end-depth 10

# 요청 간 대기 시간 조정 (초)
python scraper.py --start-id 12345 --wait-sec 5.0

# 출력 파일 이름 지정
python scraper.py --start-id 12345 --output my_genealogy.xlsx

# 로그 출력 비활성화
python scraper.py --start-id 12345 --quiet

# 모든 옵션 사용
python scraper.py --start-id 12345 --end-id 38586 --end-depth 12 --wait-sec 1.5 --output my_genealogy.xlsx --quiet
```

### 명령줄 인자 Command Line Arguments

- `--start-id` (필수): 시작할 수학자의 ID Required: ID of the starting mathematician
- `--end-id`: 탐색을 중단할 수학자의 ID ID of the target mathematician to stop at
- `--end-depth`: 탐색을 중단할 최대 세대 깊이 (기본값: 15) Maximum generation depth to explore (default: 15)
- `--wait-sec`: 요청 간 대기 시간 (초) (기본값: 2.5) Wait time between requests in seconds (default: 2.5)
- `--output`: 출력 파일 이름 (기본값: math_genealogy.xlsx) Output filename (default: math_genealogy.xlsx)
- `--verbose`: 상세 로그 출력 (기본값: True) Enable detailed logging (default: True)
- `--quiet`: 로그 출력 비활성화 Disable logging output

> **참고 Note**: `--quiet` 인자는 `--verbose` 인자를 덮어씁니다. 즉, `--quiet`와 `--verbose`를 동시에 사용하면 `--quiet`가 우선 적용됩니다.
> The `--quiet` flag overrides the `--verbose` flag. When both are specified, `--quiet` takes precedence.

## 참고사항 Notes

- 서버에 부담을 주지 않기 위해 기본적으로 요청 간 2.5초의 지연 시간을 포함했습니다 The script includes a 2.5-second delay between requests by default to be respectful to the server
- Excel 파일은 스크립트와 같은 디렉토리에 생성됩니다 The Excel file will be created in the same directory as the script
- 세대 레벨은 시작 수학자를 1로 시작하여 학문적 계보를 따라 올라갈수록 증가합니다 The generation level starts at 1 for the starting mathematician and increases as it goes up the academic tree
- Advisor들의 ID는 쉼표로 구분된 문자열 형태로 저장됩니다 Advisor IDs are stored as comma-separated strings in the Excel file
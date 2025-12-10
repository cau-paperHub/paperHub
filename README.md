# PaperHub

PaperHub는 연구자들이 학술 논문을 발견하고, 정리하고, 상호작용하는 방식을 혁신하기 위해 설계된 현대적인 지능형 웹 애플리케이션입니다. 강력한 검색 엔진, 개인화된 지식 그래프, 그리고 AI 기반 추천 기능을 결합하여, PaperHub는 고립된 읽기 경험을 역동적이고 연결된 경험으로 변화시킵니다.

## ✨ 주요 기능

### 📚 스마트 논문 관리
- **중앙 집중식 라이브러리**: 학술 논문을 한 곳에서 안전하게 업로드하고 정리할 수 있습니다.
- **맞춤형 컬렉션**: "읽을 논문", "읽는 중", "읽기 완료" 목록을 생성하여 진행 상황을 추적할 수 있습니다.
- **메타데이터 추출**: 업로드된 PDF에서 메타데이터를 자동으로 추출하고 색인화합니다.

### 🕸️ 인터랙티브 그래프 뷰
- **시각적 지식 그래프**: 인용, 저자, 주제를 기반으로 논문 간의 연결을 시각화합니다.
- **동적 탐색**: 인터랙티브 그래프 노드를 탐색하여 새로운 논문을 발견할 수 있습니다.
- **클러스터링**: 관련 논문을 자동으로 그룹화하여 연구 동향과 하위 분야를 식별하는 데 도움을 줍니다.

### 🤖 AI 기반 추천
- **개인화된 제안**: 고급 LLM 통합을 사용하여 읽기 기록 및 라이브러리 콘텐츠에 맞춘 논문 추천을 받습니다.
- **맥락적 통찰력**: AI가 생성한 설명을 통해 해당 논문이 추천된 *이유*를 이해할 수 있습니다.

### 📖 통합 PDF 뷰어
- **원활한 읽기**: 외부 도구 없이 브라우저 내에서 직접 논문을 읽을 수 있습니다.
- **주석 및 메모**: 주요 섹션을 강조 표시하고 논문에 개인 메모를 추가할 수 있습니다.

### 🔍 강력한 검색
- **arXiv 통합**: arXiv 데이터베이스에서 수백만 건의 논문을 직접 검색할 수 있습니다.
- **고급 필터**: 날짜, 저자, 카테고리별로 결과를 필터링하여 필요한 논문을 정확하게 찾을 수 있습니다.

## 🛠️ 기술 스택

### Frontend (`캡스톤_FE`)
- **Framework**: [React](https://react.dev/) with [Vite](https://vitejs.dev/)
- **Language**: [TypeScript](https://www.typescriptlang.org/)
- **Styling**: [Tailwind CSS](https://tailwindcss.com/)
- **State Management**: [Zustand](https://zustand-demo.pmnd.rs/)
- **Visualization**: [React Force Graph](https://github.com/vasturiano/react-force-graph), [Recharts](https://recharts.org/)
- **PDF Handling**: [React PDF](https://github.com/wojtekmaj/react-pdf)

### Backend (`캡스톤_BE`)
- **Framework**: [Spring Boot 3.5.6](https://spring.io/projects/spring-boot)
- **Language**: Java 17
- **Database**: [PostgreSQL](https://www.postgresql.org/)
- **Security**: Spring Security (JWT, BCrypt)
- **AI Integration**: [OpenAI API](https://openai.com/) (Java Client)
- **Storage**: AWS S3
- **PDF Processing**: [Apache PDFBox](https://pdfbox.apache.org/)

## 🚀 시작하기

### 필수 조건
- **Node.js** (v18+)
- **Java JDK** (v17)
- **PostgreSQL**
- **npm** 또는 **yarn**

### 백엔드 설정 (Backend Setup)
1. 백엔드 디렉토리로 이동합니다:
   ```bash
   cd 캡스톤_BE/paperHub_01
   ```
2. `src/main/resources/application.yml` 파일에서 환경 변수를 설정합니다:
   - 데이터베이스 자격 증명 (URL, 사용자 이름, 비밀번호)
   - OpenAI API 키
   - AWS S3 자격 증명
   - JWT 비밀 키
3. 애플리케이션을 실행합니다:
   ```bash
   ./gradlew bootRun
   ```

### 프론트엔드 설정 (Frontend Setup)
1. 프론트엔드 디렉토리로 이동합니다:
   ```bash
   cd 캡스톤_FE/paperHub
   ```
2. 의존성을 설치합니다:
   ```bash
   npm install
   ```
3. 개발 서버를 시작합니다:
   ```bash
   npm run dev
   ```

## 📂 프로젝트 구조

```
capstone/
├── 캡스톤_BE/          # 백엔드 소스 코드
│   └── paperHub_01/   # Spring Boot 애플리케이션
├── 캡스톤_FE/          # 프론트엔드 소스 코드
│   └── paperHub/      # React 애플리케이션
└── README.md          # 프로젝트 문서
```

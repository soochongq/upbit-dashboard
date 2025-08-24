# 🚀 업비트 기술적 분석 대시보드

## 📋 프로젝트 소개

이 프로젝트는 업비트 거래소의 주요 암호화폐 종목들을 실시간으로 모니터링하고, 기술적 지표를 분석하여 투자 기회를 포착하는 웹 대시보드입니다.

## ✨ 주요 기능

- 📊 **실시간 시장 모니터링**: BTC, ETH, XRP 등 12개 주요 종목
- 🔍 **기술적 지표 분석**: RSI, 볼린저 밴드, 이동평균 등
- ⏰ **자동 알림 시스템**: 조건 만족 시 텔레그램으로 즉시 알림
- 📱 **반응형 웹 디자인**: 모바일과 데스크톱 모두 지원
- 🎨 **현대적인 UI**: 직관적이고 아름다운 사용자 인터페이스

## 🌐 웹사이트 보기

**📱 라이브 데모**: [GitHub Pages에서 보기](https://your-username.github.io/upbit-dashboard/)

## 🛠️ 기술 스택

- **프론트엔드**: HTML5, CSS3, JavaScript
- **백엔드**: Python 3.8+
- **데이터 분석**: pandas, numpy
- **API**: 업비트 공식 API, 텔레그램 Bot API
- **스케줄링**: schedule 라이브러리

## 📁 프로젝트 구조

```
upbitnotion/
├── index.html              # 메인 웹 대시보드
├── upbit_alert.py          # 로컬 실행용 알림 시스템
├── upbit_alert_cloud.py    # 클라우드 배포용 알림 시스템
├── requirements.txt         # Python 패키지 의존성
├── test_telegram.py        # 텔레그램 봇 테스트
├── CLOUD_DEPLOYMENT.md     # 클라우드 배포 가이드
└── README.md               # 프로젝트 설명서
```

## 🚀 빠른 시작

### 1. 저장소 클론
```bash
git clone https://github.com/your-username/upbit-dashboard.git
cd upbit-dashboard
```

### 2. 의존성 설치
```bash
pip install -r requirements.txt
```

### 3. 환경 설정
```bash
# .env 파일 생성 (텔레그램 봇 설정)
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_ID=your_chat_id_here
```

### 4. 실행
```bash
# 로컬 실행
python upbit_alert.py

# 또는 클라우드 버전
python upbit_alert_cloud.py
```

## 📱 텔레그램 봇 설정

### 1. 봇 생성
1. @BotFather에게 `/newbot` 명령
2. 봇 이름과 사용자명 설정
3. API 토큰 받기

### 2. 채팅방 ID 확인
1. @userinfobot에게 메시지 전송
2. Chat ID 값 확인

### 3. 설정 적용
`.env` 파일에 토큰과 채팅방 ID 입력

## 🌐 웹 대시보드 사용법

1. **메인 페이지**: 시스템 개요 및 현재 상태 확인
2. **실시간 모니터링**: 12개 암호화폐 종목 분석 결과
3. **알림 설정**: 투자 조건 및 알림 옵션 설정
4. **통계 대시보드**: 과거 분석 결과 및 성과 지표

## 🔧 커스터마이징

### 분석 조건 수정
`upbit_alert.py` 파일에서 다음 조건을 조정할 수 있습니다:

```python
# RSI 조건 (기본값: ≤ 50)
rsi_condition = analysis['rsi'] <= 50

# 밴드폭 조건 (기본값: ≤ 0.3%)
band_width_condition = analysis['band_width'] <= 0.3

# 모니터링 종목 추가/제거
self.symbols = [
    'KRW-BTC',   # 비트코인
    'KRW-ETH',   # 이더리움
    # ... 추가 종목
]
```

### 알림 주기 조정
```python
# 매시간 정시
schedule.every().hour.at(":00").do(self.check_conditions)

# 매 30분마다
schedule.every(30).minutes.do(self.check_conditions)

# 매 15분마다
schedule.every(15).minutes.do(self.check_conditions)
```

## 📊 분석 지표 설명

### RSI (Relative Strength Index)
- **과매수**: 70 이상 (매도 신호)
- **과매도**: 30 이하 (매수 신호)
- **중립**: 30-70 사이

### 볼린저 밴드
- **상단 밴드**: 이동평균 + (표준편차 × 2)
- **하단 밴드**: 이동평균 - (표준편차 × 2)
- **밴드폭**: 상단-하단 밴드 간격 (좁을수록 횡보)

## 🚨 알림 조건

현재 설정된 알림 조건:
1. **RSI ≤ 50**: 중립~약세 상태
2. **밴드폭 ≤ 0.3%**: 매우 좁은 횡보 상태
3. **밴드 돌파**: 상단 또는 하단 밴드 통과

## 💡 투자 참고사항

⚠️ **주의**: 이 시스템은 투자 조언이 아닌 참고 자료입니다.
- 모든 투자 결정은 본인의 판단에 따라 신중하게 하시기 바랍니다
- 과거 성과가 미래 수익을 보장하지 않습니다
- 암호화폐 투자는 높은 위험을 수반합니다

## 🔄 업데이트 및 유지보수

### 정기 업데이트
- 업비트 API 변경사항 반영
- 새로운 기술적 지표 추가
- UI/UX 개선

### 버그 리포트
문제가 발생하면 GitHub Issues에 등록해 주세요.

## 📞 지원 및 문의

- **GitHub Issues**: [프로젝트 이슈 등록](https://github.com/your-username/upbit-dashboard/issues)
- **문서**: [상세 사용법 가이드](CLOUD_DEPLOYMENT.md)

## 📄 라이선스

이 프로젝트는 MIT 라이선스 하에 배포됩니다.

## 🙏 감사의 말

- 업비트 API 제공
- 텔레그램 Bot API
- 오픈소스 커뮤니티

---

**🎉 업비트 시장을 더 스마트하게 모니터링하세요!** 
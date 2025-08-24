# 🚀 업비트 기술적 분석 시스템 클라우드 배포 가이드

## 📋 개요

이 가이드는 업비트 기술적 분석 자동 알림 시스템을 클라우드에 배포하여 **24/7 운영**할 수 있도록 도와줍니다.

## ❌ 현재 한계

- **로컬 실행**: 컴퓨터를 끄면 알림 중단
- **인터넷 의존**: 집 인터넷 연결 상태에 영향
- **전력 소모**: 24시간 컴퓨터 운영 필요

## ✅ 클라우드 배포의 장점

- **24/7 운영**: 언제든지 알림 수신 가능
- **안정성**: 전문 서버 인프라 활용
- **비용 효율**: 월 $5-20 정도로 운영
- **자동 관리**: 서버 다운 시 자동 복구

## 🌐 클라우드 서비스 선택

### 1. **VPS (Virtual Private Server) - 초보자 추천**
- **DigitalOcean**: 월 $5부터, 사용하기 쉬움
- **Linode**: 월 $5부터, 안정적
- **Vultr**: 월 $2.50부터, 가격 경쟁력

### 2. **클라우드 플랫폼 - 고급 사용자**
- **AWS EC2**: 월 $10-20, 확장성 우수
- **Google Cloud**: 월 $10-20, 안정적
- **Azure**: 월 $10-20, 마이크로소프트 생태계

### 3. **무료 옵션 - 테스트용**
- **Heroku**: 무료 티어 (제한적)
- **Railway**: 무료 티어 (제한적)
- **Render**: 무료 티어 (제한적)

## 🚀 DigitalOcean 배포 가이드 (추천)

### 1단계: 계정 생성
1. [DigitalOcean](https://www.digitalocean.com/) 가입
2. 신용카드 등록 (월 $5 결제)

### 2단계: Droplet 생성
1. **Create** → **Droplets** 클릭
2. **Ubuntu 22.04 LTS** 선택
3. **Basic** 플랜에서 **$5/month** 선택
4. **Datacenter Region**: 서울 또는 도쿄 선택 (한국과 가까운 곳)
5. **Authentication**: SSH 키 또는 비밀번호 설정
6. **Droplet 이름**: `upbit-alert-system` 입력
7. **Create Droplet** 클릭

### 3단계: 서버 접속
```bash
# SSH로 서버 접속
ssh root@your_server_ip

# 또는 비밀번호로 접속
ssh root@your_server_ip
# 비밀번호 입력
```

### 4단계: 환경 설정
```bash
# 시스템 업데이트
apt update && apt upgrade -y

# Python 설치
apt install python3 python3-pip python3-venv -y

# 프로젝트 디렉토리 생성
mkdir /opt/upbit-alert
cd /opt/upbit-alert

# 가상환경 생성
python3 -m venv venv
source venv/bin/activate
```

### 5단계: 코드 배포
```bash
# requirements.txt 업로드 (로컬에서)
scp requirements.txt root@your_server_ip:/opt/upbit-alert/

# upbit_alert_cloud.py 업로드
scp upbit_alert_cloud.py root@your_server_ip:/opt/upbit-alert/

# 패키지 설치
pip install -r requirements.txt
```

### 6단계: 환경변수 설정
```bash
# .env 파일 생성
nano .env

# 다음 내용 입력
TELEGRAM_BOT_TOKEN=your_actual_bot_token
TELEGRAM_CHAT_ID=your_actual_chat_id
LOG_LEVEL=INFO

# Ctrl+X, Y, Enter로 저장
```

### 7단계: 서비스 등록
```bash
# systemd 서비스 파일 생성
nano /etc/systemd/system/upbit-alert.service

# 다음 내용 입력
[Unit]
Description=Upbit Technical Analysis Alert System
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/upbit-alert
Environment=PATH=/opt/upbit-alert/venv/bin
ExecStart=/opt/upbit-alert/venv/bin/python upbit_alert_cloud.py
Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target

# Ctrl+X, Y, Enter로 저장
```

### 8단계: 서비스 시작
```bash
# 서비스 활성화
systemctl daemon-reload
systemctl enable upbit-alert
systemctl start upbit-alert

# 상태 확인
systemctl status upbit-alert

# 로그 확인
journalctl -u upbit-alert -f
```

## 🔧 모니터링 및 관리

### 서비스 상태 확인
```bash
# 서비스 상태
systemctl status upbit-alert

# 로그 실시간 확인
journalctl -u upbit-alert -f

# 서비스 재시작
systemctl restart upbit-alert

# 서비스 중지
systemctl stop upbit-alert
```

### 로그 파일 확인
```bash
# 로그 파일 위치
tail -f /opt/upbit-alert/upbit_alert.log
```

## 💰 비용 예상

### DigitalOcean VPS
- **기본 플랜**: 월 $5 (1GB RAM, 1 CPU)
- **권장 플랜**: 월 $10 (2GB RAM, 1 CPU)
- **연간**: $60-120

### AWS EC2
- **t3.micro**: 월 $8-12 (1GB RAM, 2 CPU)
- **t3.small**: 월 $16-24 (2GB RAM, 2 CPU)

## 🚨 주의사항

### 1. **보안**
- SSH 키 인증 사용 권장
- 방화벽 설정 (22번 포트만 열기)
- 정기적인 보안 업데이트

### 2. **백업**
- 정기적인 코드 백업
- 설정 파일 백업
- 로그 파일 관리

### 3. **모니터링**
- 서버 상태 정기 확인
- 디스크 공간 모니터링
- 네트워크 연결 상태 확인

## 🔄 자동 재시작 설정

### PM2 사용 (Node.js 기반)
```bash
# PM2 설치
npm install -g pm2

# 애플리케이션 시작
pm2 start upbit_alert_cloud.py --name "upbit-alert" --interpreter python3

# 자동 시작 설정
pm2 startup
pm2 save
```

### Supervisor 사용
```bash
# Supervisor 설치
apt install supervisor

# 설정 파일 생성
nano /etc/supervisor/conf.d/upbit-alert.conf

# 내용 입력
[program:upbit-alert]
command=/opt/upbit-alert/venv/bin/python upbit_alert_cloud.py
directory=/opt/upbit-alert
user=root
autostart=true
autorestart=true
stderr_logfile=/var/log/upbit-alert.err.log
stdout_logfile=/var/log/upbit-alert.out.log

# Supervisor 재시작
supervisorctl reread
supervisorctl update
supervisorctl start upbit-alert
```

## 📱 텔레그램 설정 확인

### 봇 토큰 확인
1. @BotFather에게 `/mybots` 명령
2. 봇 선택 → `API Token` 확인

### 채팅방 ID 확인
1. @userinfobot에게 메시지 전송
2. `Chat ID` 값 확인

## 🎯 성공 지표

- ✅ 서버 24/7 운영
- ✅ 매시간 정시 알림
- ✅ 텔레그램 메시지 정상 전송
- ✅ 로그 파일 정상 생성
- ✅ 서비스 자동 재시작

## 🆘 문제 해결

### 서비스가 시작되지 않는 경우
```bash
# 로그 확인
journalctl -u upbit-alert -n 50

# 수동 실행 테스트
cd /opt/upbit-alert
source venv/bin/activate
python upbit_alert_cloud.py
```

### 텔레그램 메시지가 전송되지 않는 경우
1. 봇 토큰 확인
2. 채팅방 ID 확인
3. 봇이 채팅방에 초대되었는지 확인
4. 네트워크 연결 상태 확인

### 메모리 부족 오류
```bash
# 메모리 사용량 확인
free -h

# 더 큰 플랜으로 업그레이드 고려
```

## 📞 지원

문제가 발생하면 다음을 확인하세요:
1. 로그 파일 (`upbit_alert.log`)
2. 시스템 로그 (`journalctl -u upbit-alert`)
3. 서버 상태 (`systemctl status upbit-alert`)
4. 네트워크 연결 (`ping api.telegram.org`)

---

**🎉 축하합니다! 이제 컴퓨터를 끄고 있어도 24시간 언제든지 텔레그램 알림을 받을 수 있습니다!** 
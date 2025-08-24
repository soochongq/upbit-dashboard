import requests
import pandas as pd
import numpy as np
import time
import schedule
import json
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UpbitTechnicalAnalyzer:
    def __init__(self, telegram_bot_token, telegram_chat_id):
        """
        업비트 기술적 분석 자동 알림 시스템
        
        Args:
            telegram_bot_token (str): 텔레그램 봇 토큰
            telegram_chat_id (str): 텔레그램 채팅방 ID
        """
        self.base_url = "https://api.upbit.com/v1"
        self.telegram_bot_token = telegram_bot_token
        self.telegram_chat_id = telegram_chat_id
        
        # 분석할 종목들 (KRW 마켓)
        self.symbols = [
            'KRW-BTC',   # 비트코인
            'KRW-ETH',   # 이더리움
            'KRW-XRP',   # 리플
            'KRW-ADA',   # 에이다
            'KRW-DOT',   # 폴카닷
            'KRW-LINK',  # 체인링크
            'KRW-BCH',   # 비트코인캐시
            'KRW-SOL',   # 솔라나
            'KRW-AVAX',  # 아발란체
            'KRW-ATOM',  # 코스모스
        ]
    
    def get_candles(self, market, count=200):
        """
        업비트에서 캔들 데이터를 가져옵니다.
        
        Args:
            market (str): 마켓 코드 (예: KRW-BTC)
            count (int): 가져올 캔들 개수
            
        Returns:
            pd.DataFrame: 캔들 데이터
        """
        try:
            url = f"{self.base_url}/candles/minutes/60"
            params = {
                'market': market,
                'count': count
            }
            
            response = requests.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            df = pd.DataFrame(data)
            
            # 시간 순서로 정렬 (오래된 것부터)
            df = df.sort_values('candle_date_time_kst').reset_index(drop=True)
            
            return df
            
        except Exception as e:
            logger.error(f"캔들 데이터 조회 실패 ({market}): {e}")
            return None
    
    def calculate_rsi(self, prices, period=14):
        """
        RSI (Relative Strength Index) 계산
        
        Args:
            prices (pd.Series): 종가 데이터
            period (int): RSI 계산 기간
            
        Returns:
            pd.Series: RSI 값
        """
        delta = prices.diff()
        gain = delta.where(delta > 0, 0)
        loss = -delta.where(delta < 0, 0)
        
        avg_gain = gain.rolling(window=period).mean()
        avg_loss = loss.rolling(window=period).mean()
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """
        볼린저 밴드 계산
        
        Args:
            prices (pd.Series): 종가 데이터
            period (int): 이동평균 기간
            std_dev (float): 표준편차 배수
            
        Returns:
            tuple: (상단밴드, 중간밴드, 하단밴드, 밴드폭)
        """
        sma = prices.rolling(window=period).mean()
        std = prices.rolling(window=period).std()
        
        upper_band = sma + (std * std_dev)
        lower_band = sma - (std * std_dev)
        
        # 밴드폭을 백분율로 계산
        band_width = ((upper_band - lower_band) / sma) * 100
        
        return upper_band, sma, lower_band, band_width
    
    def analyze_symbol(self, symbol):
        """
        특정 종목의 기술적 분석을 수행합니다.
        
        Args:
            symbol (str): 종목 코드
            
        Returns:
            dict: 분석 결과
        """
        try:
            # 캔들 데이터 가져오기
            df = self.get_candles(symbol)
            if df is None or len(df) < 50:
                return None
            
            # 종가 데이터
            close_prices = df['trade_price']
            
            # RSI 계산
            rsi = self.calculate_rsi(close_prices)
            current_rsi = rsi.iloc[-1]
            
            # 볼린저 밴드 계산
            upper_band, middle_band, lower_band, band_width = self.calculate_bollinger_bands(close_prices)
            current_band_width = band_width.iloc[-1]
            current_price = close_prices.iloc[-1]
            
            return {
                'symbol': symbol,
                'current_price': current_price,
                'rsi': current_rsi,
                'band_width': current_band_width,
                'upper_band': upper_band.iloc[-1],
                'lower_band': lower_band.iloc[-1],
                'middle_band': middle_band.iloc[-1]
            }
            
        except Exception as e:
            logger.error(f"분석 실패 ({symbol}): {e}")
            return None
    
    def send_telegram_message(self, message):
        """
        텔레그램으로 메시지를 전송합니다.
        
        Args:
            message (str): 전송할 메시지
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data)
            response.raise_for_status()
            logger.info("텔레그램 메시지 전송 완료")
            
        except Exception as e:
            logger.error(f"텔레그램 메시지 전송 실패: {e}")
    
    def check_conditions(self):
        """
        모든 종목의 조건을 체크하고 조건에 맞는 종목이 있으면 알림을 보냅니다.
        """
        logger.info("기술적 분석 조건 체크 시작")
        
        alerts = []
        
        for symbol in self.symbols:
            try:
                analysis = self.analyze_symbol(symbol)
                
                if analysis is None:
                    continue
                
                # 조건 체크: RSI <= 50 and 밴드폭 <= 0.2%
                # 새로운 조건: RSI ≤ 50 + 밴드폭 ≤ 0.3% + 밴드 돌파
                rsi_condition = analysis['rsi'] <= 50
                band_width_condition = analysis['band_width'] <= 0.3
                upper_breakout = analysis['current_price'] > analysis['upper_band']  # 상단 돌파
                lower_breakout = analysis['current_price'] < analysis['lower_band']  # 하단 돌파
                band_breakout = upper_breakout or lower_breakout
                
                # 모든 조건을 만족해야 알림
                if rsi_condition and band_width_condition and band_breakout:
                    alerts.append(analysis)
                    
                    # 어떤 돌파인지 확인
                    if upper_breakout:
                        breakout_type = f"상단돌파 (현재가: {analysis['current_price']:,.0f} > 상단: {analysis['upper_band']:,.0f})"
                    else:
                        breakout_type = f"하단돌파 (현재가: {analysis['current_price']:,.0f} < 하단: {analysis['lower_band']:,.0f})"
                    
                    reason = f"RSI: {analysis['rsi']:.2f}, 밴드폭: {analysis['band_width']:.3f}%, {breakout_type}"
                    logger.info(f"조건 만족: {symbol} - {reason}")
                
                # API 호출 제한을 위한 딜레이
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"종목 체크 중 오류 ({symbol}): {e}")
                continue
        
        # 조건에 맞는 종목이 있으면 텔레그램으로 알림 전송
        if alerts:
            message = self.format_alert_message(alerts)
            self.send_telegram_message(message)
        else:
            logger.info("조건을 만족하는 종목이 없습니다.")
    
    def format_alert_message(self, alerts):
        """
        알림 메시지를 포맷팅합니다.
        
        Args:
            alerts (list): 조건을 만족한 종목들의 분석 결과
            
        Returns:
            str: 포맷팅된 메시지
        """
        message = "🚨 <b>업비트 기술적 분석 알림</b> 🚨\n\n"
        message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
        message += "💡 <b>알림 조건 (모두 만족):</b>\n"
        message += "🔸 RSI ≤ 50 (중립~약세)\n"
        message += "🔸 밴드폭 ≤ 0.3% (매우 좁은 횡보)\n"
        message += "🔸 밴드 돌파 (상단 또는 하단 통과)\n\n"
        
        for alert in alerts:
            symbol_name = alert['symbol'].replace('KRW-', '')
            message += f"📈 <b>{symbol_name}</b>\n"
            message += f"💰 현재가: {alert['current_price']:,.0f}원\n"
            message += f"📊 RSI: {alert['rsi']:.2f}\n"
            message += f"📏 밴드폭: {alert['band_width']:.2f}%\n"
            message += f"🔸 상단밴드: {alert['upper_band']:,.0f}원\n"
            message += f"🔹 하단밴드: {alert['lower_band']:,.0f}원\n"
    
            # 조건 만족 여부 표시
            # 돌파 유형 확인
            upper_breakout = alert['current_price'] > alert['upper_band']
            lower_breakout = alert['current_price'] < alert['lower_band']

            message += "✅ <b>만족 조건:</b> "
            message += f"RSI {alert['rsi']:.1f}≤50, 밴드폭 {alert['band_width']:.3f}%≤0.3%, "

            if upper_breakout:
                message += "🚀 상단 돌파 (강세 신호)\n\n"
            elif lower_breakout:
                message += "📉 하단 돌파 (약세 신호)\n\n"
        
        message += "⚠️ <i>투자 결정은 신중하게 하시기 바랍니다.</i>"
        
        return message
    
    def run_scheduler(self):
        """
        스케줄러를 실행합니다.
        """
        # 매시간 정시에 체크
        schedule.every().hour.at(":00").do(self.check_conditions)
        
        logger.info("스케줄러 시작 - 매시간 정시에 기술적 분석을 수행합니다.")
        
        # 프로그램 시작 시 한 번 체크
        self.check_conditions()
        
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 스케줄 체크


def main():
    """
    메인 함수 - 프로그램 설정 및 실행
    """
    
    # 설정값 입력 (실제 사용시 환경변수나 설정파일로 관리 권장)
    TELEGRAM_BOT_TOKEN = "8122286381:AAFqvR9kjb3nk6QbudNb17HW9IeSOwTsEkE"  # 텔레그램 봇 토큰
    TELEGRAM_CHAT_ID = "40167023"              # 텔레그램 채팅방 ID
    
    # 설정 확인
    if TELEGRAM_BOT_TOKEN == "YOUR_TELEGRAM_BOT_TOKEN" or TELEGRAM_CHAT_ID == "YOUR_CHAT_ID":
        print("❌ 텔레그램 봇 토큰과 채팅방 ID를 설정해주세요!")
        print("\n📝 설정 방법:")
        print("1. @BotFather에게 /newbot 명령을 보내서 봇을 생성하세요")
        print("2. 생성된 봇 토큰을 TELEGRAM_BOT_TOKEN에 입력하세요")
        print("3. 봇과 채팅을 시작하고 @userinfobot에게 메시지를 보내서 채팅방 ID를 확인하세요")
        print("4. 채팅방 ID를 TELEGRAM_CHAT_ID에 입력하세요")
        return
    
    # 분석기 초기화 및 실행
    try:
        analyzer = UpbitTechnicalAnalyzer(TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID)
        analyzer.run_scheduler()
        
    except KeyboardInterrupt:
        logger.info("프로그램이 사용자에 의해 중단되었습니다.")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {e}")


if __name__ == "__main__":
    main()

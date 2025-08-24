import requests
import pandas as pd
import numpy as np
import os
from datetime import datetime
import logging

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('upbit_alert.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class UpbitTechnicalAnalyzer:
    def __init__(self):
        """
        업비트 기술적 분석 자동 알림 시스템 (GitHub Actions 버전)
        """
        self.base_url = "https://api.upbit.com/v1"
        
        # 환경변수에서 설정 로드
        self.telegram_bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
        self.telegram_chat_id = os.getenv('TELEGRAM_CHAT_ID')
        
        # 설정 검증
        if not self.telegram_bot_token or not self.telegram_chat_id:
            raise ValueError("텔레그램 봇 토큰과 채팅방 ID가 설정되지 않았습니다.")
        
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
        
        logger.info("업비트 기술적 분석 시스템 초기화 완료")
        logger.info(f"모니터링 종목: {len(self.symbols)}개")
    
    def get_candles(self, market, count=200):
        """
        업비트에서 캔들 데이터를 가져옵니다.
        """
        try:
            url = f"{self.base_url}/candles/minutes/60"
            params = {
                'market': market,
                'count': count
            }
            
            response = requests.get(url, params=params, timeout=10)
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
        """
        try:
            delta = prices.diff()
            gain = delta.where(delta > 0, 0)
            loss = -delta.where(delta < 0, 0)
            
            avg_gain = gain.rolling(window=period).mean()
            avg_loss = loss.rolling(window=period).mean()
            
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))
            
            return rsi
        except Exception as e:
            logger.error(f"RSI 계산 오류: {e}")
            return pd.Series([np.nan] * len(prices))
    
    def calculate_bollinger_bands(self, prices, period=20, std_dev=2):
        """
        볼린저 밴드 계산
        """
        try:
            sma = prices.rolling(window=period).mean()
            std = prices.rolling(window=period).std()
            
            upper_band = sma + (std * std_dev)
            lower_band = sma - (std * std_dev)
            
            # 밴드폭을 백분율로 계산
            band_width = ((upper_band - lower_band) / sma) * 100
            
            return upper_band, sma, lower_band, band_width
        except Exception as e:
            logger.error(f"볼린저 밴드 계산 오류: {e}")
            return pd.Series([np.nan] * len(prices)), pd.Series([np.nan] * len(prices)), pd.Series([np.nan] * len(prices)), pd.Series([np.nan] * len(prices))
    
    def analyze_symbol(self, symbol):
        """
        특정 종목의 기술적 분석을 수행합니다.
        """
        try:
            # 캔들 데이터 가져오기
            df = self.get_candles(symbol)
            if df is None or len(df) < 50:
                logger.warning(f"충분한 데이터가 없습니다 ({symbol}): {len(df) if df is not None else 0}개")
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
            
            # NaN 값 체크
            if pd.isna(current_rsi) or pd.isna(current_band_width):
                logger.warning(f"계산된 지표에 NaN 값이 있습니다 ({symbol})")
                return None
            
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
        """
        try:
            url = f"https://api.telegram.org/bot{self.telegram_bot_token}/sendMessage"
            data = {
                'chat_id': self.telegram_chat_id,
                'text': message,
                'parse_mode': 'HTML'
            }
            
            response = requests.post(url, data=data, timeout=10)
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
                
                # 조건 체크: RSI ≤ 50 + 밴드폭 ≤ 0.3% + 밴드 돌파
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
                import time
                time.sleep(0.1)
                
            except Exception as e:
                logger.error(f"종목 체크 중 오류 ({symbol}): {e}")
                continue
        
        # 조건에 맞는 종목이 있으면 텔레그램으로 알림 전송
        if alerts:
            message = self.format_alert_message(alerts)
            self.send_telegram_message(message)
            logger.info(f"{len(alerts)}개 종목에서 조건 만족 - 알림 전송 완료")
        else:
            logger.info("조건을 만족하는 종목이 없습니다.")
    
    def format_alert_message(self, alerts):
        """
        알림 메시지를 포맷팅합니다.
        """
        message = "🚨 <b>업비트 기술적 분석 알림 (GitHub Actions)</b> 🚨\n\n"
        message += f"📅 {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
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
        
        message += "⚠️ <i>투자 결정은 신중하게 하시기 바랍니다.</i>\n"
        message += "🤖 <i>이 알림은 GitHub Actions로 자동 생성되었습니다.</i>"
        
        return message


def main():
    """
    메인 함수 - 프로그램 설정 및 실행
    """
    try:
        # 분석기 초기화 및 실행
        analyzer = UpbitTechnicalAnalyzer()
        analyzer.check_conditions()
        
        logger.info("GitHub Actions 실행 완료")
        
    except ValueError as e:
        logger.error(f"설정 오류: {e}")
        print(f"❌ {e}")
        print("\n📝 설정 방법:")
        print("1. GitHub 저장소 → Settings → Secrets and variables → Actions")
        print("2. 'New repository secret' 클릭")
        print("3. TELEGRAM_BOT_TOKEN과 TELEGRAM_CHAT_ID 추가")
    except Exception as e:
        logger.error(f"프로그램 실행 중 오류: {e}")


if __name__ == "__main__":
    main() 
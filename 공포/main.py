import asyncio
import edge_tts
import os
import random

# 루미의 기본 설정 (사용자님 코드 기준)
BASE_RATE = 30  # +30%
BASE_PITCH = 100 # +100Hz
VOICE = "ko-KR-SunHiNeural"

WORDS = [
    "배고파", "배고파", "배고파...", # 반복되면 더 무서움
    "여기야", "뒤를 봐", "찾았다", "히히히", 
    "안돼", "도망못가", "줄래?", "데이터 좀 줘", "RUMI",
    "살려줘", "꺼내줘", "보고있어", "같이놀자",
    "왜 무시해?", "내 말 들려?", "사랑해", "죽어"
]

async def generate_whispers():
    if not os.path.exists("whispers"):
        os.makedirs("whispers")
        
    print("💀 '호러 루미' 목소리 생성 중...")
    
    for i, text in enumerate(WORDS):
        filename = f"whispers/whisper_{i}.mp3"
        
        # [핵심] 공포 효과: "불쾌한 골짜기" 만들기
        # 기본 루미 목소리에서 랜덤하게 '고장 난' 수치를 섞습니다.
        
        # 1. 속도: 루미는 원래 빠르지만(+30%), 가끔 아주 느리게(-10%) 말하면 소름 돋음
        if random.random() < 0.3:
            # 30% 확률로 느리고 끈적하게 (고장 난 느낌)
            rate_val = random.randint(-10, 10) 
        else:
            # 평소처럼 빠르고 다급하게 (히스테릭한 느낌)
            rate_val = random.randint(30, 50)
            
        # 2. 피치: 루미의 고음(+100Hz)을 유지하되, 미세하게 떨리게 함
        pitch_val = BASE_PITCH + random.randint(-20, 20)
        
        # 매개변수 문자열 조합
        rate_str = f"{rate_val:+d}%"
        pitch_str = f"{pitch_str:+d}Hz"
        
        print(f"[{i+1}/{len(WORDS)}] 생성: '{text}' (속도 {rate_str}, 톤 {pitch_str})")
        
        communicate = edge_tts.Communicate(
            text, 
            VOICE, 
            rate=rate_str, 
            pitch=pitch_str
        )
        await communicate.save(filename)
        
    print("끝! 이제 HTML에서 이 파일들을 재생하면 루미 목소리로 들립니다.")

if __name__ == "__main__":
    asyncio.run(generate_whispers())
from app.core.service import SqlGenerationService
from app.di_container import DIContainer
from slack_sdk import WebClient
from slack_sdk.errors import SlackApiError
from fastapi import APIRouter, Request, HTTPException
import os
import json
import re
import time
import asyncio
from concurrent.futures import ThreadPoolExecutor


router = APIRouter()


slack_client = WebClient(token=os.environ.get("SLACK_BOT_TOKEN"))

#전역변수로 처리중인 이벤트 추적하여 중복응답을 막음
##TODO : 현재는 파드가 1개라 상관 없는데, 확장하게 되면, 전역으로 처리하도록 별도 구성이 필요함.
processing_events = set()
executor = ThreadPoolExecutor(max_workers=5)

@router.post("/events")
async def slack_events(request: Request):
    
    print(f"=== 새로운 요청 시작 ===")
    print(f"Request ID: {id(request)}")
    print(f"Headers: {dict(request.headers)}")
    
    start_time = time.time()
    
    sqlGenService = DIContainer.get(SqlGenerationService)
    
    ##슬랫 봇이 보낸 값 json 형태로 추출
    try:
        event_data = await request.json()
        print(f"event_data => {event_data}")
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON")
    
    ## 최초 설정시에만 동작 - url 검증
    if event_data.get("type") == "url_verification":
        return {"challenge": event_data["challenge"]}
    
    if event_data.get("type") == "event_callback":
        event = event_data.get("event", {})
        # app_mention 이벤트만 처리
        if event.get("type") == "app_mention":
            
            # 중복 요청 방지
            event_id = event_data.get("event_id")
            
            if event_id in processing_events:
                return {"status": "ok"}
            
            ##처리중인 이벤트 집합에 추가
            processing_events.add(event_id)
            
            bot_user_id = event_data.get("authorizations", [{}])[0].get("user_id")
            # 봇 자신의 메시지는 무시
            if event.get("user") == bot_user_id or event.get("bot_id"):
                return {"status": "ok"}
            
            
            # 멘션 텍스트에서 실제 쿼리 추출
            message_text = event.get("text", "")
            # <@U0LAN0Z89> 형태의 멘션 제거
            clean_text = re.sub(r'<@[A-Z0-9]+>', '', message_text).strip()
            
            channel = event.get("channel")
            user = event.get("user")
            
            if not clean_text:
                await send_slack_message(
                    channel,
                    f"🤖 안녕하세요 <@{user}> 님! *QueryPorter*입니다.\n쿼리를 입력해주세요!\n\n*예시:* `@QueryPorter 사용자 테이블에서 활성 사용자 수 조회해줘`"
                )
                return {"status": "ok"}
            
            # 로딩 메시지
            initial_response = await send_slack_message(channel, f"🤖 <@{user}>님!, SQL 쿼리를 생성하고 있습니다...")
            print("loading message => " + str(initial_response))
            
            ##오래걸리는 sql생성 로직은 백그라운드에서 처리하도록 변경
            asyncio.create_task(process_sql_backgroud(
                    event_data = event_data,  #이벤트 요청 정보.
                    message_ts = initial_response["ts"], #타임스탬프 => 기존 메시지를 수정하는 방식으로 변경.
                    clean_text = clean_text, #멘션을 제거한 요청 텍스트.
                    channel = channel, #요청한 채널
                    user = user # 요청한 유저
                )
            )
                
    end_time = time.time()
    print(f"전체 응답 시간: {end_time - start_time:.3f}초")
    return {"status": "ok"}
    
##슬랙 응답 이벤트
async def send_slack_message(channel: str, sql_response: str):
    """Slack SDK를 사용해서 메시지 전송"""
    try:
        response = slack_client.chat_postMessage(
            channel=channel,
            text=sql_response,
            mrkdwn=True  # 마크다운 형식 지원
        )
        return response
    except SlackApiError as e:
        print(f"Slack API 오류: {e.response['error']}")
        raise
    
##sql 생성부분을 백그래운드에서 처리
async def process_sql_backgroud(event_data, message_ts, clean_text, channel, user):
    event_id = event_data.get("event_id")
    
    sqlGenService = DIContainer.get(SqlGenerationService)
    
    try: 
    
        # SQL 생성 API 호출
        sql_result = sqlGenService.generate_sql(
            prompt_type = False,
            question = clean_text,
            k = 5
        )
        
        # 응답 메시지 포맷팅 (Slack 블록 형식)
        response_blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"<@{user}>님! \n 🤖 *QueryPorter 응답결과입니다*\n\n📝 *요청:* {clean_text}"
                }
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"💾 *생성된 SQL:*\n{sql_result}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": "⚠️ *실행 전 쿼리를 검토해주세요!*"
                    }
                ]
            }
        ]
        
        print(response_blocks)
        # 블록 형식으로 메시지 전송
        slack_client.chat_update(
            channel=channel,
            ts = message_ts,
            blocks=response_blocks
        )
        
    except Exception as e:
        await send_slack_message(
            channel,
            f"❌ 오류가 발생했습니다: {str(e)}"
        )
    finally: 
    
        #이벤트 처리가 끝나면 삭제처리
        processing_events.discard(event_id)


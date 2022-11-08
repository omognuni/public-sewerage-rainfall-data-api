# 하수관로-강우량 정보 API

### 설치
- git clone 후 다음 명령어 실행
```
docker-compose up --build
```
- 테스트 결과 확인
```
docker-compose run --rm public-sewerage-rainfall sh -c 'python manage.py test'
```
- 테스트 코드는 각 app 들의 tests 폴더 참조
  - app/core/tests

### User
- 이용자

| 내용       | Method | URL             |
| ---------- | ------ | --------------- |
| 회원가입   | POST   | api/user/create |
| Token 인증 | POST   | api/user/token  |

###

1. client는 "구청명"을 query 파라미터로 보냄
   -  data/?GU_NAME='강남구'
2. 해당 구청명을 가진 강우량 정보를 6*24개 가져옴 (10분에 한번씩, 하루치)
  - 예상 응답 데이터
  
```json
{"ListRainfallService":{
"list_total_count":16668,
"RESULT":{"CODE":"INFO-000","MESSAGE":"정상 처리되었습니다"},
"row":[
    {"RAINGAUGE_CODE":103.0,"RAINGAUGE_NAME":"개포2동","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":"2022-11-08 15:49"},
    {"RAINGAUGE_CODE":102.0,"RAINGAUGE_NAME":"세곡동","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":"2022-11-08 15:49"},
    {"RAINGAUGE_CODE":101.0,"RAINGAUGE_NAME":"강남구청","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":"2022-11-08 15:49"},
    {"RAINGAUGE_CODE":103.0,"RAINGAUGE_NAME":"개포2동","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":"2022-11-08 15:39"},
    {"RAINGAUGE_CODE":101.0,"RAINGAUGE_NAME":"강남구청","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":"2022-11-08 15:39"}
    ]
  }
}
```

3. 해당 응답 데이터에서 GU_CODE를 가져와 하수관로 요청 url에 사용
   - OPENAPI_URL/start_index/end_index/GU_CODE/측정일1/측정일2
   - 측정일1은 2번 응답데이터의 "RECEIVE_TIME" 최근값, 측정일2은 마지막 값의 시간까지만 사용
   - start_index와 end_index는 둘 다 1로 한번 보낸 뒤 list_total_count값을 받아 다시 전체 리스트를 받아오는 식으로 시도해볼 예정
4. 결과값
  - 10분 우량 시간대에 포함되는 수위 현황들 나열
```json
{
  "강남구": {
    "10분 우량": 10,
    "수위 현황": []
  }
}
```
1. 
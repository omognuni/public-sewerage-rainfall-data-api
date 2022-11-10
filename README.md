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
  - app/fetch/tests

### User
- 이용자

| 내용       | Method | URL             |
| ---------- | ------ | --------------- |
| 회원가입   | POST   | api/user/create |
| Token 인증 | POST   | api/user/token  |

###

1. client는 구분코드(GUBN)를 query 파라미터로 보냄
   -  /api/v1/fetch/data/?GUBN=1
2. 해당 구분코드에 해당하는 요청을 보낸 시간에서 1시간내 측정된 하수도 수위를 가져옴
   - OPENAPI_URL/start_index/end_index/GUBN/현재년월일시-1시간/현재년월일시

3. 해당 응답 데이터에서 구청명(GUBN_NAM)를 가져와 강수량 요청 url에 사용
   - OPENAPI_URL/start_index/end_index/"GUBN_NAM"구
  
4. 결과값
  - 1시간 시간대에 포함되는 수위 현황들 나열
```json
{ 
  "시간대": "YYYYMMDDHH~YYYYMMDDHH",
  "구청명": "강남구",
  "우량": [],
  "수위": []
}
```
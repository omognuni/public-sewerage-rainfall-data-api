# 하수관로-강우량 정보 API

### 설치
- 현재 repository clone
- .env 파일을 .env.sample과 같이 생성
```
OPENAPI_KEY=YOUR_API_KEY # openapi.seoul.go.kr에서 받은 API KEY
OPENAPI_URL=http://openapi.seoul.go.kr:8088/
```
- 명령어 실행
```
docker-compose up --build
```
- http://localhost:8000/api/v1/user/create 에서 유저 생성
- http://localhost:8000/api/v1/user/token 에서 유저 토큰 생성
- 생성한 토큰을 Authorization 헤더에 'Token 생성한토큰' 추가 (mod header 확장앱 사용)

#
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
| 회원가입   | POST   | api/v1/user/create |
| Token 인증 | POST   | api/v1/user/token  |


### Fetch
| 내용       | Method | URL             |
| ---------- | ------ | --------------- |
| 데이터 요청   | GET   | api/v1/fetch/data/?GUBN={number} |

### 설명

1. 클라이언트는 구분코드(GUBN)를 url로 query 파라미터와 함께 보냄
   -  /api/v1/fetch/data/?GUBN=1
2. 서버는 해당 구분코드에 해당하는 요청을 보낸 시간에서 1시간내 측정된 하수도 수위를 가져옴
   - OPENAPI_URL/start_index/end_index/GUBN/현재년월일시-1시간/현재년월일시

3. 서버는 해당 응답 데이터에서 구청명(GUBN_NAM)를 가져와 강수량 요청 url에 사용
   - OPENAPI_URL/start_index/end_index/"GUBN_NAM"구
  

4. 결과값을 클라이언트에 전달
   - 시간대에 포함되는 수위 현황들 나열
 
```json
{ 
  "시간대": "YYYYMMDDHH~YYYYMMDDHH",
  "구청명": "강남구",
  "우량": [],
  "수위": []
}
```
# 주식 거래 API

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


<img src='/images/test.PNG'>


### ERD
<img src='/images/ERD.png'>


### User
- 이용자

| 내용       | Method | URL             |
| ---------- | ------ | --------------- |
| 회원가입   | POST   | api/user/create |
| Token 인증 | POST   | api/user/token  |


from rest_framework import authentication, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response

from fetch.utils import fetch_data
from urllib import parse


class FetchAPIView(APIView):
    
    def get(self, request, format=None):
        '''GUBN 코드를 받아 데이터 반환'''
        GUBN = request.query_params.get('GUBN','')
        if GUBN:
            # url encode
            GUBN = parse.unquote(GUBN)
            # GUBN 코드는 무조건 2자리수 ex) 01, 02
            GUBN = str(GUBN).zfill(2)
            result = fetch_data(GUBN)
            if not result:
                return Response({'message':'없는 구청입니다.'}, status=status.HTTP_400_BAD_REQUEST)
            return Response(status=status.HTTP_200_OK, data=result)
        
        else:
            return Response({'message': '구분코드를 입력하세요'}, status=status.HTTP_400_BAD_REQUEST)
from unittest.mock import patch

from django.contrib.auth import get_user_model
from django.conf import settings
from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework.response import Response
from rest_framework import status

from fetch.utils import get_sewerage_data, get_rainfall_data, fetch_data

from datetime import datetime, timedelta, timezone
import json

GU_NAME='강남구'
GU_CODE = '01'

SEWERAGE_URL=settings.OPENAPI_URL + 'json/DrainpipeMonitoringInfo/'
RAINFALL_URL=settings.OPENAPI_URL + 'json/ListRainfallService/'
FETCH_URL = reverse('fetch:data')

KST = timezone(timedelta(hours=9))
IN_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f'


class FetchAPITest(TestCase):
    
    def setUp(self):
        '''
        Open Api에서 반환되는 데이터 설정 및 시간 설정
        '''
        # requests.get 메서드 mocking
        self.patcher = patch('requests.get')
        self.patched_get = (self.patcher.start())
        
        self.client= APIClient()
        self.user = get_user_model().objects.create_user(username='testname', password='testpass')
        self.client.force_authenticate(self.user)
        sewerage_timeset = (datetime.now(KST) - timedelta(seconds=10)).strftime(IN_DATE_FORMAT)
        rainfall_timeset = (datetime.now(KST) - timedelta(seconds=10)).strftime("%Y-%m-%d %H:%M")
        self.sewerage_sample_data = {
            "list_total_count":480,
            "RESULT":{"CODE":"INFO-000","MESSAGE":"정상 처리되었습니다"},
            "row":[{"IDN":"01-0004","GUBN":"01","GUBN_NAM":"종로","MEA_YMD":sewerage_timeset,"MEA_WAL":0.12,"SIG_STA":"통신양호","REMARK":"종로구 세종대로178 뒤 맨홀(KT광화문사옥뒤 자전거보관소앞 종로1길, 미대사관~종로소방서 남측, 중학천 하스박스)"},
                   {"IDN":"01-0003","GUBN":"01","GUBN_NAM":"종로","MEA_YMD":sewerage_timeset,"MEA_WAL":0.17,"SIG_STA":"통신양호","REMARK":"종로구 자하문로 21 앞 맨홀(영해빌딩앞코너 측구측, 백운동천 하수박스)"},
                   {"IDN":"01-0002","GUBN":"01","GUBN_NAM":"종로","MEA_YMD":sewerage_timeset,"MEA_WAL":0.02,"SIG_STA":"통신양호","REMARK":"중로구 세종대로 지하189 (세종로지하주차장 6층 천장)"},
                   {"IDN":"01-0001","GUBN":"01","GUBN_NAM":"종로","MEA_YMD":sewerage_timeset,"MEA_WAL":0.1,"SIG_STA":"통신양호","REMARK":"종로구 새문안로9길 9 앞 맨홀(세븐일레븐앞, 현대해상화재빌딩뒤, 백운동천하수박스)"},
                   {"IDN":"01-0004","GUBN":"01","GUBN_NAM":"종로","MEA_YMD":sewerage_timeset,"MEA_WAL":0.12,"SIG_STA":"통신양호","REMARK":"종로구 세종대로178 뒤 맨홀(KT광화문사옥뒤 자전거보관소앞 종로1길, 미대사관~종로소방서 남측, 중학천 하스박스)"}
                   ]
                }
        self.rainfall_sample_data = {
            "list_total_count":264364,
            "RESULT":{"CODE":"INFO-000","MESSAGE":"정상 처리되었습니다"},
            "row":[{"RAINGAUGE_CODE":101.0,"RAINGAUGE_NAME":"강남구청","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":rainfall_timeset},
                    {"RAINGAUGE_CODE":102.0,"RAINGAUGE_NAME":"세곡동","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":rainfall_timeset},
                    {"RAINGAUGE_CODE":103.0,"RAINGAUGE_NAME":"개포2동","GU_CODE":101.0,"GU_NAME":"강남구","RAINFALL10":"0","RECEIVE_TIME":rainfall_timeset},
                    {"RAINGAUGE_CODE":201.0,"RAINGAUGE_NAME":"강동구청","GU_CODE":102.0,"GU_NAME":"강동구","RAINFALL10":"0","RECEIVE_TIME":rainfall_timeset},
                    {"RAINGAUGE_CODE":202.0,"RAINGAUGE_NAME":"고덕2동","GU_CODE":102.0,"GU_NAME":"강동구","RAINFALL10":"0","RECEIVE_TIME":rainfall_timeset}
                ]
            }
        self.patched_get.return_value.status_code = 200
        
        # requests.get 메서드가 최종적으로 받아와야 하는 데이터
        self.patched_get.return_value.json.return_value = {
            "DrainpipeMonitoringInfo": self.sewerage_sample_data,
            "ListRainfallService": self.rainfall_sample_data
        }
        
    def tearDown(self):
        self.patcher.stop()

    def test_retrieve_sewerage_data(self):
        '''하수도 수위 데이터 가져오기 테스트'''
        start_date = '2022110810'
        end_date = '2022110811'
                
        data = get_sewerage_data(GU_CODE, start_date, end_date)

        url = SEWERAGE_URL + f'1/{data["DrainpipeMonitoringInfo"]["list_total_count"]}/' + GU_CODE + f'/{start_date}/{end_date}'
        self.assertEqual(data["DrainpipeMonitoringInfo"], self.sewerage_sample_data)
        self.patched_get.assert_called_with(url)

    def test_retrieve_rainfall_data(self):
        '''강수량 데이터 가져오기 테스트'''              
        start_idx = 1
        end_idx = 5
        data = get_rainfall_data(GU_NAME, start_idx, end_idx)
        url = RAINFALL_URL + f'{start_idx}/{end_idx}/' + GU_NAME
        
        self.patched_get.assert_called_once_with(url)
        self.assertEqual(data["ListRainfallService"],self.rainfall_sample_data)

    def test_fetch_data(self):
        '''하수도 수위와 강우량 데이터 fetching 테스트'''         
        data = fetch_data(GU_CODE)
        
        self.assertEqual(data['우량'], self.rainfall_sample_data['row'])
        self.assertEqual(data['수위'], self.sewerage_sample_data['row'])
        
    def test_retrieve_fetch_data(self):
        '''request와 query parameter를 보내 데이터 fetching 테스트'''
        params = {'GUBN': GU_CODE}
        res = self.client.get(FETCH_URL, params)
        
        self.assertEqual(res.data['우량'], self.rainfall_sample_data['row'])
        self.assertEqual(res.data['수위'], self.sewerage_sample_data['row'])
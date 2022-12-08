from django.conf import settings

from datetime import datetime, timedelta, timezone
import requests

ROOT_URL = settings.OPENAPI_URL
KST = timezone(timedelta(hours=9))
IN_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f %z'
OUT_DATE_FORMAT = '%Y%m%d%H'


class OpenAPIProvider:
    '''OpenAPI 데이터 수집 기본 클래스'''
    def __init__(self, key: str, data_type: str):
        self.root_url = ROOT_URL
        self.data_type = data_type
        self.key = key
        self.res_success_code = 'INFO-000'
    
    def _get_response(self, url: str)->dict:
        response = requests.get(url)
        return self._parse_response(response)
      
    def _get_response_code(self, response: dict) -> str:
        return response['RESULT']['CODE']

    def _get_list_total_count(self, response: dict) -> int:
        return response['list_total_count']
    
    def _parse_response(self, response: requests.Response) -> dict:
        try:
            data = response.json()[self.key]
            res_code = self._get_response_code(data)
            if res_code == self.res_success_code:
                return data
        except:
            return
    
    def get(self, start_date: str, end_date: str)-> dict:
        url = f'{self.root_url}/{start_date}/{end_date}'
        return self._get_response(url)
    
class SewerAPIProvider(OpenAPIProvider):
    '''하수도 수위 데이터 수집'''
    def get(self, GUBN: str, start_date:str, end_date:str, start=0, end=0) -> dict:
        url = f'{self.root_url}/{self.data_type}/{self.key}/1/1/{GUBN}/{start_date}/{end_date}'
        data = self._get_response(url)
        if data:
            list_total_count = self._get_list_total_count(data)
            
            _start = 1
            _end = list_total_count
            if start:
                _start = start
            if end:
                _end = end
                
            url = f'{self.root_url}/{self.data_type}/{self.key}/{_start}/{_end}/{GUBN}/{start_date}/{end_date}'
            return self._get_response(url)
        return
    
class RainAPIProvider(OpenAPIProvider):
    '''강우량 데이터 수집'''
    
    '''
    end가 100인 이유:
    강수량 측정계가 한 지역구에 5개를 넘지 않기 때문에
    1시간에 100개를 넘지 않음((측정계 개수) * 6 (10분에 한 번씩 측정, 1시간=6))
    open api에 요청을 보내면 보낸 시간을 기준으로 데이터를 가져오기 때문에
    end index를 100으로 놓고 1시간 이내인 것만 result에 추가
    '''
    def get(self, GU_NAME: str, start=1, end=100) -> dict:

        url = f'{self.root_url}/{self.data_type}/{self.key}/{start}/{end}/{GU_NAME}'
        data = self._get_response(url)
        if data:
            return data
        return
    

def fetch_data(GUBN):
    '''데이터 합치기'''
    sewer_data_provider = SewerAPIProvider(key='DrainpipeMonitoringInfo', data_type='json')
    rain_data_provider = RainAPIProvider(key='ListRainfallService', data_type='json')

    end_date = datetime.now(KST)
    start_date = end_date - timedelta(hours=1)
    
    str_end_date = end_date.strftime(OUT_DATE_FORMAT)
    str_start_date = start_date.strftime(OUT_DATE_FORMAT)
    
    sewer_data = sewer_data_provider.get(GUBN, start_date=str_start_date, end_date=str_end_date)
    
    if sewer_data == None:
        return
    
    GU_NAME = sewer_data['row'][0]['GUBN_NAM'] + '구'
    
    results = {
        "시간대":  str_start_date + "~" + str_end_date,
        "구청명": GU_NAME,
        "우량": [],
        "수위": [],
    }
    
    for data in sewer_data['row']:
        data_time = datetime.strptime(data['MEA_YMD'] + ' +0900', IN_DATE_FORMAT)
        # 현재 시간에서 한 시간 내에 있는 데이터들만 결과에 넣기
        if  data_time >= start_date and data_time <= end_date:
            results['수위'].append(data)

    rain_data = rain_data_provider.get(GU_NAME)
    
    if rain_data == None:
        return       
    
    for data in rain_data['row']:
        data_time = datetime.strptime(data['RECEIVE_TIME'] + ' +0900', "%Y-%m-%d %H:%M %z")
        # 현재 시간에서 한 시간 내에 있는 데이터들만 결과에 넣기
        if data_time >= start_date and data_time <= end_date:
            results['우량'].append(data)

    return results
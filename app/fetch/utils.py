from django.conf import settings

from datetime import datetime, timedelta, timezone
import requests

SEWERAGE_URL=settings.OPENAPI_URL + 'json/DrainpipeMonitoringInfo/'
RAINFALL_URL=settings.OPENAPI_URL + 'json/ListRainfallService/'

KST = timezone(timedelta(hours=9))
IN_DATE_FORMAT = '%Y-%m-%d %H:%M:%S.%f %z'
OUT_DATE_FORMAT = '%Y%m%d%H'


def get_sewerage_data_total_count(GUBN, start_date, end_date):
    '''데이터 한줄만 가져와서 list_total_count가 몇개인지 가져오기'''
    url = SEWERAGE_URL + '1/1/' + str(GUBN) + f'/{start_date}/{end_date}'
    response = requests.get(url)
    data = response.json()
    return data['DrainpipeMonitoringInfo']['list_total_count']

def get_sewerage_data(GUBN, start_date, end_date):
    '''하수도 수위 전체 데이터 가져오기'''
    list_total_count = get_sewerage_data_total_count(GUBN, start_date, end_date)
    # 1000개 넘어가면 error 발생, 나중에 pagination 적용
    if list_total_count >= 1000:
        list_total_count = 999 
    url = SEWERAGE_URL + f'1/{list_total_count}/' + str(GUBN) + f'/{start_date}/{end_date}'
    response = requests.get(url)
    data = response.json()
    if data['DrainpipeMonitoringInfo']['RESULT']['CODE'] == 'INFO-000':
        return data
    return

def get_rainfall_data(GU_NAME, start, end):
    '''강수량 가져오기'''
    url = RAINFALL_URL + f'{start}/{end}/' + GU_NAME
    response = requests.get(url)
    data = response.json()
    if data['ListRainfallService']['RESULT']['CODE'] == 'INFO-000':
        return data
    return

def fetch_data(GUBN):
    '''데이터 합치기'''
    end_date = datetime.now(KST)
    start_date = end_date - timedelta(hours=1)
    
    str_end_date = end_date.strftime(OUT_DATE_FORMAT)
    str_start_date = start_date.strftime(OUT_DATE_FORMAT)
    
    response = get_sewerage_data(GUBN, str_start_date, str_end_date)
    
    if response == None:
        return
    
    GU_NAME = response['DrainpipeMonitoringInfo']['row'][0]['GUBN_NAM'] + '구'
    
    results = {
        "시간대":  str_start_date + "~" + str_end_date,
        "구청명": GU_NAME,
        "우량": [],
        "수위": [],
    }
    
    for data in response['DrainpipeMonitoringInfo']['row']:
        data_time = datetime.strptime(data['MEA_YMD'] + ' +0900', IN_DATE_FORMAT)
        # 현재 시간에서 한 시간 내에 있는 데이터들만 결과에 넣기
        if  data_time >= start_date and data_time <= end_date:
            results['수위'].append(data)
            
    '''
    get_rainfall_data의 end index가 100인 이유:
    강수량 측정계가 한 지역구에 5개를 넘지 않기 때문에
    1시간에 100개를 넘지 않음((측정계 개수) * 6 (10분에 한 번씩 측정, 1시간=6))
    open api에 요청을 보내면 보낸 시간을 기준으로 데이터를 가져오기 때문에
    end index를 100으로 놓고 1시간 이내인 것만 result에 추가
    '''
    response = get_rainfall_data(GU_NAME, 1, 100)
    
    if response == None:
        return       
    
    for data in response['ListRainfallService']['row']:
        data_time = datetime.strptime(data['RECEIVE_TIME'] + ' +0900', "%Y-%m-%d %H:%M %z")
        # 현재 시간에서 한 시간 내에 있는 데이터들만 결과에 넣기
        if data_time >= start_date and data_time <= end_date:
            results['우량'].append(data)

    return results
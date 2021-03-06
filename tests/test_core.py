from datetime import datetime
from datetime import timedelta
import requests
import requests_mock
import time
import json
import jwt
import os
import pytest
from src.analytics.AnalyticsClient import analytics_client
import pandas as pd
from pandas._testing import assert_frame_equal

test_adobe_org_id= 'fake_org_id'
test_subject_account = 'fake_subject_account'
test_client_id = 'fake_client_id' 
test_client_secret = 'fake_client_secret'
test_account_id= 'fake_account_id'
test_access_token = 'fake_access_token'
test_report_suite_id = 'fake_rsid'

def _generate_adobe_client():
    client = analytics_client(
        adobe_org_id= test_adobe_org_id, 
        subject_account = test_subject_account, 
        client_id = test_client_id ,
        client_secret = test_client_secret,
        account_id= test_account_id)
    return client


def mockreturn(custom_report_object = None):
    
    mock_response_obj = {
        "totalPages":1,
        "firstPage":True,
        "lastPage":True,
        "numberOfElements":7,
        "number":0,
        "totalElements":7,
        "columns":{
            "dimension":{
                "id":"variables/daterangeday",
                "type":"time"
            },
            "columnIds":[
                "0"
            ]
        },
        "rows":[
            {
                "itemId":"1171131",
                "value":"Dec 31, 2017",
                "data":[
                    794.0
                ]
            },
            {
                "itemId":"1180001",
                "value":"Jan 1, 2018",
                "data":[
                    16558.0
                ]
            },
            {
                "itemId":"1180002",
                "value":"Jan 2, 2018",
                "data":[
                    17381.0
                ]
            }
        ],
        "summaryData":{
            "totals":[
                104310.0
            ]
        }
        }
    mock_response_str = json.dumps(mock_response_obj)

    # Generate fake response
    adapter = requests_mock.Adapter()
    adapter.register_uri('POST', 'mock://test.com/', status_code = 200, text = mock_response_str)
    
    session = requests.Session()
    session.mount('mock', adapter)
    
    res = session.post('mock://test.com/')

    return res


def test_client_constructor():

    client = _generate_adobe_client()
    
    assert client.adobe_auth_host == 'https://ims-na1.adobelogin.com'
    assert client.adobe_auth_url == '/'.join([client.adobe_auth_host, 'ims/exchange/jwt'])
    assert client.adobe_org_id == test_adobe_org_id
    assert client.subject_account == test_subject_account

    assert client.client_id == test_client_id
    assert client.client_secret == test_client_secret
    assert client.private_key_location == os.path.join(os.path.expanduser('~'), '.ssh/private.key')
    assert client.account_id == test_account_id

    assert client.experience_cloud_metascope == 'https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk'

    assert client.analytics_url == "https://analytics.adobe.io/api/{}/reports".format(test_account_id)

def test_empty_report_object():
    expected_report_object = {
            "rsid": '',
            "globalFilters": [],
            "metricContainer": {
                "metrics": []
            },
            "dimension": ''
        }
    actual_report_object = analytics_client._generate_empty_report_object()
    assert expected_report_object == actual_report_object

def test_jwtPayload():
    client = _generate_adobe_client()

    jwt_expiration = datetime(2020, 4, 8, 20, 30, 30, 107868)

    expected_jwt = {
        'iss': test_adobe_org_id, 
        'sub': test_subject_account, 
        'https://ims-na1.adobelogin.com/s/ent_analytics_bulk_ingest_sdk': True, 
        'aud': 'https://ims-na1.adobelogin.com/c/{}'.format(test_client_id), 
        'exp': jwt_expiration + timedelta(minutes = 30)
        }

    assert client._get_jwtPayload(jwt_expiration) == expected_jwt

def test_renew_access_token(mocker):
    ACCESS_TOKEN_VALUE = 'test token value'
    # adapter = requests_mock.Adapter()
    # mock reading private key
    client = _generate_adobe_client()

    client._read_private_key = mocker.Mock(return_value = 'test_key')
    jwt.encode = mocker.Mock(return_value = 'jwt_encoded')
    assert client._read_private_key() == 'test_key'

    test_response_text = json.dumps({"token_type":"bearer","access_token":ACCESS_TOKEN_VALUE,"expires_in":86399995})
    
    # Generate fake response
    adapter = requests_mock.Adapter()
    adapter.register_uri('GET', 'mock://test.com/path', text=test_response_text)
    session = requests.Session()
    session.mount('mock', adapter)
    test_response = session.get('mock://test.com/path')
    
    # Patch request and fake response
    mocker.patch("requests.post", return_value = test_response)
    
    assert ACCESS_TOKEN_VALUE == client._renew_access_token()





def test_get_request_headers(mocker):
    
    client = _generate_adobe_client()
    client._renew_access_token = mocker.Mock(return_value = test_access_token)

    expected_analytics_header = {           
            "X-Api-Key": test_client_id,
            "x-proxy-global-company-id": test_account_id,
            "Authorization" : "Bearer " + test_access_token,
            "Accept": "application/json",
            "Content-Type": "application/json"
        }

    print(client._get_request_headers())

    print(expected_analytics_header)

    assert client._get_request_headers() == expected_analytics_header

def test_format_date_range():
    client = _generate_adobe_client()
    
    #Case 1: different dates
    start_date ='2017-01-31'
    end_date = '2020-12-31'
    start_hour = 0
    end_hour = 0
    expected_date_format = '2017-01-31T00:00:00/2021-01-01T00:00:00'

    assert expected_date_format == client._format_date_range(date_start = start_date, date_end = end_date, hour_start = start_hour, hour_end = end_hour)
    
    client.report_object = client._generate_empty_report_object()
    client.set_date_range(start_date, end_date)
    assert client.report_object['globalFilters'][0]['dateRange'] == expected_date_format

    #Case 2: Same dates
    start_date = '2020-01-31'
    end_date = '2020-01-31'
    start_hour = 0
    end_hour = 5
    expected_date_format = '2020-01-31T00:00:00/2020-01-31T05:00:00'
    assert expected_date_format == client._format_date_range(date_start = start_date, date_end = end_date, hour_start = start_hour, hour_end = end_hour)

    client.report_object = client._generate_empty_report_object()
    client.set_date_range(start_date, end_date)
    expected_date_format = '2020-01-31T00:00:00/2020-02-01T00:00:00'
    assert client.report_object['globalFilters'][0]['dateRange'] == expected_date_format

    #Case 3: Same dates - different hours
    start_date = '2020-01-31'
    end_date = '2020-01-31'
    start_hour = 4
    end_hour = 15
    expected_date_format = '2020-01-31T04:00:00/2020-01-31T15:00:00'
    assert expected_date_format == client._format_date_range(date_start = start_date, date_end = end_date, hour_start = start_hour, hour_end = end_hour)

    client.report_object = client._generate_empty_report_object()
    client.set_date_range(start_date, end_date)
    expected_date_format = '2020-01-31T00:00:00/2020-02-01T00:00:00'
    assert client.report_object['globalFilters'][0]['dateRange'] == expected_date_format

def test_set_report_suite():
    client = _generate_adobe_client()

    client.set_report_suite(test_report_suite_id)

    assert client.report_object['rsid'] == test_report_suite_id

def test_metric_add():
    client = _generate_adobe_client()

    test_metric_name = "metrics/pageviews"
    expected_metric = {
            "columnId":"0",
            "id": test_metric_name
        }
    client.add_metric(test_metric_name)

    assert expected_metric == client.report_object['metricContainer']['metrics'][0]

    test_metric_name = "metrics/visits"
    expected_metric = {
            "columnId":"1",
            "id": test_metric_name
        }
    client.add_metric(test_metric_name)
    assert expected_metric == client.report_object['metricContainer']['metrics'][1]

def test_set_dimension():
    client = _generate_adobe_client()
    test_dimension_name = 'variables/daterangeday'

    client.set_dimension(test_dimension_name)

    assert test_dimension_name == client.report_object['dimension']

def test_get_page(mocker, monkeypatch):
    
    # mock reading private key
    client = _generate_adobe_client()
    client._get_request_headers = mocker.Mock(return_value = 'test headers')

    test_response_text_fail = 'error message'
    test_response_text_success = 'success message'
    
    # Generate fake response -
    adapter = requests_mock.Adapter()
    adapter.register_uri('POST', 'mock://fail.com/', status_code = 400, text = test_response_text_fail)
    adapter.register_uri('POST', 'mock://success.com/', status_code = 200, text = test_response_text_success)

    session = requests.Session()
    session.mount('mock', adapter)
    test_response_fail = session.post('mock://fail.com/')
    test_response_success = session.post('mock://success.com/')

    # Patch request and fail response
    mocker.patch("requests.post", return_value = test_response_fail)

    with pytest.raises(requests.exceptions.HTTPError) as e:
        assert client._get_page()
    assert e.value.response.status_code == 400
    assert e.value.response.text == test_response_text_fail

    # Patch request and success response
    mocker.patch("requests.post", return_value = test_response_success)
    page = client._get_page()

    assert page.status_code == 200
    assert page.text == test_response_text_success   



def test_get_report(mocker, monkeypatch):

    client = _generate_adobe_client()
    client.add_metric('metric-1')
    
    monkeypatch.setattr(client, "_get_page", mockreturn)
    
    tmp = client.get_report()

    d = {
        'itemId' : ['1171131', '1180001', '1180002'],
        'value': ['Dec 31, 2017', 'Jan 1, 2018', 'Jan 2, 2018'], 
        'metric-1': [794.0, 16558.0 , 17381.0]
    }

    expected_df = pd.DataFrame(data = d)
    
    assert expected_df.equals(tmp)





def test_no_results(mocker):
    client = _generate_adobe_client()
    client._get_request_headers = mocker.Mock(return_value = 'test headers')

    no_results_json = '{"totalPages":1,"firstPage":false,"lastPage":false,"numberOfElements":0,"number":0,"totalElements":0,"columns":{"dimension":{"id":"variables/evar65","type":"string"},"columnIds":["0","1","2"]},"rows":[],"summaryData":{"filteredTotals":[0.0,0.0,0.0],"totals":[0.0,0.0,0.0]}}'

    # Generate fake response -
    adapter = requests_mock.Adapter()
    adapter.register_uri('POST', 'mock://test.com/', status_code = 200, text = no_results_json)
    
    session = requests.Session()
    session.mount('mock', adapter)
    test_response = session.post('mock://test.com/')
    
    # Patch request and fail response
    mocker.patch("requests.post", return_value = test_response)

    page = client._get_page()

    assert page.status_code == 200
    assert page.text == no_results_json   

    # Adding metrics to the report_object    
    client.add_metric(metric_name = 'metrics/visits')
    client.add_metric(metric_name = 'metrics/orders')
    client.add_metric(metric_name = 'metrics/random')

    expected_output_df = pd.DataFrame({
        'itemId':['0'],
        'value':['Unspecified'],
        'metrics/visits':[0],
        'metrics/orders':[0],
        'metrics/random':[0]
        })

    assert_frame_equal(client.format_output(page), expected_output_df)

def test_get_metrics():

    client = _generate_adobe_client()

    client.add_metric(metric_name= 'metrics/event3')
    client.add_metric(metric_name= 'metrics/event4')
    index = ['0', '1']
    metricName = ['metrics/event3', 'metrics/event4']
    expected_metrics = pd.DataFrame(index=index, data = metricName)
    # expected_metrics.columns = ['metrics']
    # import pdb; pdb.set_trace()
    assert expected_metrics.equals(client._get_metrics())

def test_format_output(mocker):

    test_request_object = {
        "rsid":"adbedocrsid",
        "globalFilters":[
            {
                    "type":"dateRange",
                    "dateRange":"2017-12-31T00:00:00.000/2018-01-06T23:59:59.999"
            }
        ],
        "metricContainer":{
            "metrics":[
                {
                    "columnId":"0",
                    "id":"metrics/pageviews",
                    "filters":[
                    "0"
                    ]
                }
            ],
            "metricFilters":[
                {
                    "id":"0",
                    "type":"dateRange",
                    "dateRange":"2017-12-31T00:00:00.000/2018-01-06T23:59:59.999"
                }
            ]
        },
        "dimension":"variables/daterangeday",
        "settings":{
                "dimensionSort":"asc"
            }
        }
    
    test_response_text = {
        "totalPages":1,
        "firstPage":True,
        "lastPage":False,
        "numberOfElements":7,
        "number":0,
        "totalElements":7,
        "columns":{
            "dimension":{
                "id":"variables/daterangeday",
                "type":"time"
            },
            "columnIds":[
                "0"
            ]
        },
        "rows":[
            {
                "itemId":"1171131",
                "value":"Dec 31, 2017",
                "data":[
                    794.0
                ]
            },
            {
                "itemId":"1180001",
                "value":"Jan 1, 2018",
                "data":[
                    16558.0
                ]
            },
            {
                "itemId":"1180002",
                "value":"Jan 2, 2018",
                "data":[
                    17381.0
                ]
            }
        ],
        "summaryData":{
            "totals":[
                104310.0
            ]
        }
        }

    test_response_text_no_pages = {
        "totalPages":0,
        "firstPage":True,
        "lastPage":False,
        "numberOfElements":0,
        "number":0,
        "totalElements":0,
        "columns":{
            "dimension":{
                "id":"variables/daterangeday",
                "type":"time"
            },
            "columnIds":[
                "0"
            ]
        },
        "rows":[],
        "summaryData":{
            "totals":[]
        }
        }

    client = _generate_adobe_client()
    client.report_object = test_request_object

    # Expected value - with results
    value = ['Dec 31, 2017', 'Jan 1, 2018', 'Jan 2, 2018']    
    ids = ['1171131', '1180001', '1180002']
    metric = [794.0, 16558.0 , 17381.0]
    dt = {'itemId': ids , 'value' : value, 'metrics/pageviews' : metric}
    expected_value = pd.DataFrame(data = dt)

    # Expected value - no results
    value = ['Unspecified']    
    ids = ['0']
    metric = [0]
    dt = {'itemId': ids , 'value' : value, 'metrics/pageviews' : metric}
    expected_value_no_results = pd.DataFrame(data = dt)

    # Generate fake response -
    adapter = requests_mock.Adapter()
    adapter.register_uri('POST', 'mock://success.com/', status_code = 200, text = json.dumps(test_response_text))
    adapter.register_uri('POST', 'mock://fail.com/', status_code = 200, text = json.dumps(test_response_text_no_pages))

    session = requests.Session()
    session.mount('mock', adapter)
    test_response_success = session.post('mock://success.com/')
    test_response_success_no_results = session.post('mock://fail.com/')

    assert expected_value.equals(client.format_output(test_response_success))
    assert expected_value_no_results.equals(client.format_output(test_response_success_no_results))
    # Test empty results response

def test_add_dimension():
    client = _generate_adobe_client()
    client.add_dimension('fake_dimension')
    assert ['fake_dimension'] == client.dimensions
    client.add_dimension('fake_dimension_2')
    assert 'fake_dimension' == client.report_object['dimension']

def test_add_global_segment():
    client = _generate_adobe_client()
    client.add_global_segment('test_id_1')
    client.add_global_segment('test_id_2')

    #Case 2: Same dates
    start_date = '2020-01-31'
    end_date = '2020-01-31'
    expected_date_format = '2020-01-31T00:00:00/2020-02-01T00:00:00'

    expected_global_filters = [
            {
                "type":"segment",
                "segmentId":"test_id_1"
            },
            {
                "type":"segment",
                "segmentId":"test_id_2"
            }, 
            {
                "type":"dateRange",
                "dateRange" : expected_date_format
            }
        ]
    
    assert expected_date_format == client._format_date_range(date_start = start_date, date_end = end_date, hour_start= 0 , hour_end= 0)

    client.set_date_range(date_start = start_date, date_end = end_date)
    assert expected_global_filters == client.report_object['globalFilters']



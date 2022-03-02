from src.analytics.AnalyticsClient import analytics_client
from datetime import datetime
from azure.storage.blob import BlobClient 
import os





conn_string=os.environ['CONN_STRING']
accountName=os.environ['ACCOUNT_NAME']
accountKey=os.environ['ACCOUNT_KEY']
containerName =os.environ['CONTAINER_NAME']


ADOBE_ORG_ID = os.environ['ADOBE_ORG_ID']
SUBJECT_ACCOUNT = os.environ['SUBJECT_ACCOUNT']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
PRIVATE_KEY_LOCATION = os.environ['PRIVATE_KEY_LOCATION']
GLOBAL_COMPANY_ID = os.environ['GLOBAL_COMPANY_ID']
REPORT_SUITE_ID = os.environ['REPORT_SUITE_ID']





aa = analytics_client(
        adobe_org_id = ADOBE_ORG_ID, 
        subject_account = SUBJECT_ACCOUNT, 
        client_id = CLIENT_ID, 
        client_secret = CLIENT_SECRET,
        account_id = GLOBAL_COMPANY_ID, 
        private_key_location = PRIVATE_KEY_LOCATION
)

aa.set_report_suite(report_suite_id = REPORT_SUITE_ID)


aa.set_date_range(date_start = datetime.today().date().replace(day=1).strftime('%Y-%m-%d'), date_end= datetime.today().strftime('%Y-%m-%d'))

#add segment that filters to canadian regions
aa.add_global_segment(segment_id = "s300000938_615b634e7ee37961ec011b09")

#add segment that filters to canadian languages en/fr
aa.add_global_segment(segment_id = "s300000938_615c57f83207242d005be13c")

#add segment that filters to SC Labs (E/F)(v12)
aa.add_global_segment(segment_id = "s300000938_60d228c474f05e635fba03ff")

#add segment that filters to french home page
aa.add_global_segment(segment_id = "s300000938_61a91e4c8626233f6d4a356c")

'''
#add segment that filters to top 5 page titles
aa.add_global_segment(segment_id = "s300000938_616db7a9910209746265973b")

'''

aa.add_metric(metric_name= 'metrics/visits')

#add metric 'Average Time Spent on Site(secs)'
aa.add_metric(metric_name= 'metrics/averagetimespentonsite')

aa.add_dimension(dimension_name = 'variables/daterangeday')

#add page titles variables/evar11 into the API request body
aa.add_dimension(dimension_name = 'variables/evar11')


#add Region to the API request body
aa.add_dimension(dimension_name = 'variables/georegion')


#add dimension Page Language(v5)
aa.add_dimension(dimension_name = 'variables/evar5')




data = aa.get_report_multiple_breakdowns()






print(data)




blob = BlobClient.from_connection_string(conn_str=conn_string, container_name=containerName, blob_name=f"sclabs-site-analytics/test_ds_adls_saebdlstorage2_csv_Fact_Metrics_By_FRHomePage{datetime.today().strftime('%Y%m')}.csv")

print(str(data.to_csv()))

blob.upload_blob(str(data.to_csv()),overwrite=True)




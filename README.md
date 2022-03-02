# Adobe Analytics Python Class 

Download Reports data utilising the Adobe.io version 2.0 API locally.

To Integrate with Cloud (Azure) ,please check [Integrate with Azure](Azurepipeline.md)





# Authentication methods supported by the package:
1.JWT

2.OAuth (tested only through Jupyter Notebook!)

## Authentication via JSON Web Token (JWT aka Service Account)

We’re going to use JWT aka Service Account as the method for authentication since it’s designed for machine-to-machine communication. As such authentication can be completely automated on platforms such as Azure after it’s built.

Compare this to Oauth 2.0 based authentication which requires user input at some interval. You might want the user to authenticate from time to time, but my goal is to build this data ingestion pipeline that doesn’t require any user interaction once it’s built.

## JWT Requirements & Adobe.io access
In order to run the package, first you need to gain access to a service account from Adobe.io or request an existing certificate from Principle Publisher. The method used is JWT authentication. More instructions on how to create the integration at: https://www.adobe.io/authentication/auth-methods.html#!AdobeDocs/adobeio-auth/master/JWT/JWT.md. 

### To obtain JWT credientials from Adbobe Developer Console


In Projects > Credential Details > Get the Client ID and Client Secret:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/adobe-analytics-client-id-secret-v2.png)

In Projects > Credential Details > Generate a public/private keypair
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/adobe-analytics-generate-pub-priv-keys.png)

When you click the button you’ll download a zip file that contains a public key file and private key file. You can open these in any text editor to see what they look like. Keep the private key file handy, we’ll refer to it later in our Python code.

### Or you can request JWT certificate from Principle Publisher.

Sample certificate:
```python
{
   'CLIENT_SECRET':'xxxx',
   'ORG_ID':'xxxx@AdobeOrg',
   'API_KEY':'xxxxx',
   'TECHNICAL_ACCOUNT_ID':'xxxx@techacct.adobe.com',
   'TECHNICAL_ACCOUNT_EMAIL':'x@techacct.adobe.com',
   'PUBLIC_KEYS_WITH_EXPIRY':{
      'xxxxxx':'mm/dd/yyyy'
   }
}
```

After you have completed the integration, you will finde available the following information:

- Organization ID ( ORG_ID ): It is in the format of < organisation id >@AdobeOrg
- Technical Account ID( TECHNICAL_ACCOUNT_ID ): < tech account id >@techacct.adobe.com 
- Client ID( API_KEY ):Like a username for the API, Information is available on the completion of the Service Account integration
- Client Secret( CLIENT_SECRET ):Like a password for the API,  Information is available on the completion of the Service Account integration
- Account ID( TECHNICAL_ACCOUNT_ID ): Instructions on how to obtain it at https://youtu.be/lrg1MuVi0Fo?t=96
- Report suite( GLOBAL_COMPANY_ID ): Report suite ID from which you want to download the data. Usually it is 'canada5'.
- Private Key: Like a signature for your password
- JWT Payload: Some specific details that Adobe want you to show them to trade for the Access Token.

Make sure that the integration is associated with an Adobe Analytics product profile that is granted access to the necessary metrics ,dimensions and segments.



## Package installation
```python
pip install requirements.txt
```

## Samples

### Initial setup - JWT
After you have configured the integration and downloaded the package, the following setup is needed:
```python
ADOBE_ORG_ID = os.environ['ADOBE_ORG_ID']
SUBJECT_ACCOUNT = os.environ['SUBJECT_ACCOUNT']
CLIENT_ID = os.environ['CLIENT_ID']
CLIENT_SECRET = os.environ['CLIENT_SECRET']
PRIVATE_KEY_LOCATION = os.environ['PRIVATE_KEY_LOCATION']
GLOBAL_COMPANY_ID = os.environ['GLOBAL_COMPANY_ID']
REPORT_SUITE_ID = os.environ['REPORT_SUITE_ID']
```
Next initialise the Adobe client:
```python
aa = analytics_client(
        adobe_org_id = ADOBE_ORG_ID, 
        subject_account = SUBJECT_ACCOUNT, 
        client_id = CLIENT_ID, 
        client_secret = CLIENT_SECRET,
        account_id = GLOBAL_COMPANY_ID, 
        private_key_location = PRIVATE_KEY_LOCATION
)

aa.set_report_suite(report_suite_id = REPORT_SUITE_ID)
```


### Initial setup - OAuth

Import the package and initiate the required parameters
```python
import analytics_client

client_id = '<client id>'
client_secret = '<client secret>'
global_company_id = '<global company id>'
```
Initialise the Adobe client:
```python
aa = analytics_client(
        auth_client_id = client_id, 
        client_secret = client_secret,
        account_id = global_company_id
)
```
Perform the authentication

```python
aa._authenticate()
```

For a demo notebook, please refer to the [Jupyter Notebook - OAuth example](examples/JupyterNotebook/OAuthDemo.ipynb)



## Report Configurations
Set the date range of the report (format: YYYY-MM-DD)
```python
aa.set_date_range(date_start = '2019-12-01', date_end= '2019-12-31')
```
To configure specific hours for the start and end date:
```python
aa.set_date_range(date_start='2020-12-01', date_end='2020-12-01', hour_start= 4, hour_end= 5 )
```
If `hour_end` is set, then only up to that hour in the last day data will be retrieved instead of the full day.

## Global segments
To add a segment, you need the segment ID (currently only this option is supported). To obtain the ID, you need to activate the Adobe Analytics Workspace debugger (https://github.com/AdobeDocs/analytics-2.0-apis/blob/master/reporting-tricks.md). Then inspect the JSON request window and locate the segment ID under the 'globalFilters' object.

To apply the segment:
```python
aa.add_global_segment(segment_id = 's300000938_60d228c474f05e635fba03ff')

# add segment 'SC Labs (E/F)(v12)' to the report request body
```



### Request with 2 metrics and 1 dimension
```python
aa.add_metric(metric_name= 'metrics/visits')
aa.add_metric(metric_name= 'metrics/orders')
aa.add_dimension(dimension_name = 'variables/mobiledevicetype')
data = aa.get_report()
```
Output:

|itemId_lvl_1   |  value_lvl_1 | metrics/visits | metrics/averagetimeuserstay |  |
| --- | --- | --- | --- | --- 
|         0     |      Other    |  1    |    3    
|  1728229488   |       Tablet  |     2   |   45    
|  2163986270   | Mobile Phone  |    12   |    23    
|  ...    | ...  |       ...   |        ...   |      

### Request with 2 metrics and 2 dimensions:
```
aa.add_metric(metric_name= 'metrics/visits')
aa.add_metric(metric_name= 'metrics/averagetimespentonsite')
aa.add_dimension(dimension_name = 'variables/devicetype')
aa.add_dimension(dimension_name = 'variables/evar5')
data = aa.get_report_multiple_breakdowns()

```
Output:
Each item in level 1 (i.e. Tablet) is broken down by the dimension in level 2 (i.e. eng,fra). The package downloads all possible combinations. In a similar fashion more dimensions can be added.

| itemId_lvl_1 | value_lvl_1 | itemId_lvl_2 |  value_lvl_2 | metrics/visits | metrics/averagetimespentonsite  |  |
| --- | --- | --- | --- | --- | --- | --- 
|0 |Other |1 |fra| 233| 39| 
|0 |Other |2 |fra| 424| 12  | 
|0 |Other |3 |fra| 840| 41  | 
| ... | ... | ... | ... | ... | ... |  
| 1728229488 |Tablet |1 | eng| 80| 12  | 
| 1728229488 |Tablet |2 |eng| 50| 41  | 
| ... | ... | ... | ... | ... | ... |  



## Upload result to Azure Blob Storage

Now to connect to the Azure blob to upload the result, we must provide an the following parameters. You can find them on the “Access keys” page of the Azure blob storage account. To obtain the parameters, open the home page of Azure Portal Select Azure Blob storage account (stsaebdevca01 ) :

![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-blob-provide-access-key.jpg)

```python
conn_string=os.environ['conn_string']
accountName=os.environ['accountName']
accountKey=os.environ['accountKey']
containerName =os.environ['containerName']
```

Now we can initiate the blob client and upload our result as a csv into the container

```python
blob = BlobClient.from_connection_string(conn_str=conn_string, container_name=containerName, blob_name='blob_parent/blob_name')

blob.upload_blob(str(data.to_csv()),overwrite=True)
```

## Unit Test

Run the following code to unit test the code

```python
py.test Adobe-Azure-analytics-api-v2.0/tests/test_core.py
# or
pytest 
```


# Next Steps

[Integrate with Azure](Azurepipeline.md)

[Connect with Power BI](PowerBIReadme.md)

# Issues, Bugs and Suggestions:


Known missing features:
- No support for filtering
- No support for top N 
- No support for custom sorting


| title | description | ms.service|  author  | ms.date |
| --- | --- | --- | --- | --- 
|Ingest data by using Databricks in Azure Data Factory |This tutorial provides step-by-step instructions for ingesting data by using a databricks activity in Azure Data Factory |Data-Factory | Juntao Zou| 01/13/2021| 







# Transform and load data in the cloud by using a Databrick activity in Azure Data Factory



In this tutorial, you use the Azure portal to create an Azure Data Factory pipeline. This pipeline ingests data and does minimum transfomation by using a Databrick activity and Azure Key Vault linked service. 

You perform the following steps in this tutorial:

> * Access to a data factory. 
> * Access to a pipeline that uses a Databrick activity.
> * Integrate pipeline with Azure Key Vault.
> * Trigger a pipeline run.
> * Monitor the pipeline run.

If you don't have Azure portal access, please connect with the system administrator before you begin.

## Prerequisites


* **Azure storage account**. You create a Python script and an input file, and you upload them to Azure Storage. The output from the Spark program is stored in this storage account. The on-demand Spark cluster uses the same storage account as its primary storage.  




## Cloud versus On-Prem

Key difference between running python notebook in cloud versus OnPrem is that where private key is stored.

### Run Python Notebook in cloud reads private key stored in Azure Key Vault
[AnalyticsClient - Cloud(Azure) Class](src/analytics/AzureAnalyticsClient.py)

```python

    def _read_private_key(self):
        # Request private Key
        # This secret scope is backed by Azure Key vault
        aa_private_key = dbutils.secrets.get(scope = "scope_name", key = "key_name")
        private_key = bytes('-----BEGIN PRIVATE KEY-----\n'+aa_private_key+'\n-----END PRIVATE KEY-----', 'utf-8')
        return private_key

```
### Run Python script OnPrem reads private key locally stored in OnPrem machine.
[AnalyticsClient - OnPrem Class](src/analytics/AnalyticsClient.py)

```python

    def _read_private_key(self):
        # Request Access Key
        # This Needs to point at where your private key is on the file system
        keyfile = open(self.private_key_location, 'r')
        private_key = keyfile.read()
        return private_key
```
## Access to a data factory

1. Launch **Microsoft Edge** or **Google Chrome** web browser. Currently, Data Factory UI is supported only in Microsoft Edge and Google Chrome web browsers,go to 
https://portal.azure.com login and then select **Data Factory**. 

![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-access-portal.png)





## Access Azure linked services
You author two linked services in this section: 
    
- An **Azure Databrick linked service** that links an Azure Databricks to the data factory.  

- An **Azure Key Vault linked service** that links an Azure Databricks to Azure Key Vault


### Access Databrick linked service

1. On the home page, switch to the **Manage** tab in the left panel. 

![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-LinkedService-ADF.png)

2.Click on the Databricks Linked Service

![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-LinkedService-ADF-connection.png)

3.The Linked Service authenticates through Azure Key Vault Secret


![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-LinkedService-ADF-connection_value.png)


### Access Azure Key Vault linked service(scope)
1.Access Databricks Notebook
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-Notebook-open.png)

2.Create a scope for Databricks 
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-scope.png)

3.The scope created is used to read private key stored in Azure Key Vault
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-Notebook-content.png)

```python

    def _read_private_key(self):
        # Request private Key
        # This secret scope is backed by Azure Key vault
        aa_private_key = dbutils.secrets.get(scope = "scope_name", key = "key_name")
        private_key = bytes('-----BEGIN PRIVATE KEY-----\n'+aa_private_key+'\n-----END PRIVATE KEY-----', 'utf-8')
        return private_key

```


## Access to a pipeline


1.Click on 'Open' to launch Azure Data Factory Studio 
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-open.png)


2.Follow the instructions below:  
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-access-pipeline.png)

3.Access to the Databrick activity:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-open.png)


4.View the Databrick Notebook with the following content: [AnalyticsClient - Cloud(Azure) Class](examples/DatabricksNotebook/DatabricksExample.ipynb)
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Databricks-Notebook.png)






## Trigger a pipeline run

1.Select **Add Trigger** on the toolbar, and then select **Trigger Now**. 

![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-trigger-now.png)

2.Select **Add Trigger** on the toolbar, and then select **Edit/New**. 

![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-trigger-newedit.png)


## Monitor the pipeline run

1. Switch to the **Monitor** tab. Confirm that you see a pipeline run. 
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-monitor.png)
2. Select **Refresh** periodically to check the status of the pipeline run. 

  

3. To see activity runs associated with the pipeline run, select **View Activity Runs** in the **Actions** column.

  

   You can switch back to the pipeline runs view by selecting the **All Pipeline Runs** link at the top.

  

## Verify the output
Verify that the output file *blob_name.csv* is created under the *sclabs-site-analytics* folder based on parameter *containerName* below. 

```python
blob = BlobClient.from_connection_string(conn_str=conn_string, container_name=containerName, blob_name="sclabs-site-analytics/blob_name.csv")
```

Verify the data based on input parameters. 


![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-Data-Factory-result.png)

## Summary
The pipeline in this sample ingests data by using a Databrick activity and Azure Key Vault linked service. You learned how to: 

> * Access a data factory. 
> * Access a pipeline that uses a Databrick activity.
> * Trigger a pipeline run.
> * Monitor the pipeline run.

## Next Steps
To learn how to connect transformed data with Power BI in order to visualize: 

[Connect with Power BI](PowerBIReadme.md)






# Connect  with Power BI

In this article, I am going to explain how we can access the data from the Azure Blob Storage using Power BI. To do that, we are going to use the below tools:

Azure Blob Storage account: We have uploaded the source CSV file to it


Power BI Desktop: To view the data imported from the CSV file

## Connect to Blob Storage from Power BI

First, To import the data from the CSV file and load it into the Power BI report, we must configure the connection between Power BI and CSV file that is in Azure Blob container. To do that, first, open Power BI Desktop and click on “Get Data” from the Home ribbon:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-blob-to-PBI.png)


In the “Get Data” dialog box, click on Azure Select “Azure Blob Storage” and click on “Connect”:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-blob-type-account-name.png)


In Azure Blob storage dialog box, provide the name of Azure storage Account or the URL of the Azure storage account and click on “OK”:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-blob-input-account-key.png)

Now to connect to the Azure blob from the Azure portal, we must provide an account access key. You can find this key on the “Access keys” page of the Azure blob storage account. To obtain the access key, open the home page of Azure Portal Select Azure Blob storage account (stsaebdevca01 ) select “Access keys”:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-blob-provide-access-key.jpg)

Copy the first key and paste it in the account key page of Power BI and click on connect.

In the navigator dialog box, you can see the list of the storage accounts and the blob containers.  On the left pan, you can see the list of the storage accounts and the containers. In the tight pan, you can see the list of files that have been uploaded to the selected container. We are going to import csv file in Power BI hence select the “.csv” file you wanted to import and click on the Transform Data button:
![](/assets/images/AA-to-Azure-Python-Wrapper-Class/Azure-blob-import.png)

## Summary

In this article, I have explained how we can access the CSV file that is uploaded to the Azure Blob Storage account using Power BI. Sometimes, the data are curated in Azure Synapse ,please connect with product owner to understand where they are located at. This article is useful for readers who are using Azure Blob Storage to store their excel files and use it to create Power BI reports.


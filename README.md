# Automated data pipeline with Airflow and AWS

## Project Scope

- Store the raw data in **S3 bucket**.
- Create staging, fact, dimensional tables on **AWS Redshift** as a Cloud Data Warehouse using Python code instead of the AWS Console.
- Utilize DAGs, tasks, schedules, operators, plugins on **Apache Airflow** that automates ETL data from **S3 bucket** into **AWS Redshift**.
- Configure data quality check regarding fault tolerent and error handling on processing tasks in Airflow.
- Query data in the **AWS Redshift** and implement some of anylytics purposes.

### Getting Started

1. Create an IAM User in AWS.

- Airflow needs an AWS user:
    - Search IAM Users in the search bar, and then click on Users.
    - Click on Add Users.
    - Input User name.
    - Check the field Access key - Programmatic access.
    - Click on Next Permissions.
    - In the Set permissions section, select Attach existing policies directly.
    - Search and select the following policies:
        - AdministratorAccess
        - AmazonRedshiftFullAccess
        - AmazonS3FullAccess
    - Click on Next: Tags, and the click on Next Review.
    - You will see a Review section. Ensure that you have the same permissions as in the image below.
    - Finally, click on Create user.
    - You should see a success message and user credentials on the next screen.
    - Click on Download .csv to download the credentails for the user you just created. These credentials would be used in connecting AWS to Airflow.

2. Add Airflow connection to AWS.

- Here, we'll use Airflow's UI to configure your AWS credentials.
    - To go to the Airflow UI.
    - Click on the **Admin** tab and select **Connections**.
    - Under Connections, click the plus button.
    - On the create connection page, enter the following values:
        - Connection Id: Enter aws_credentials.
        - Connection Type: Enter Amazon Web Services.
        - AWS Access Key ID: Enter your Access key ID from the IAM User credentials you downloaded earlier.
        - AWS Secret Access Key: Enter your Secret access key from the IAM User credentials you downloaded earlier. Once you've entered these values, select Save.
        - Click the Test button to pre-test your connection information.

3. Create Security Group and Cluster subnet group for Redshift

    3.1. Security Group

- Navigate to the **EC2 service**
- Under **Network and Security** in the left navigation pane, select **Security Groups**. Click the **Create Security Group** button to launch a wizard.
- In the Create security group wizard, enter the basic details.

    |Section|Field|Value|
    |---|---|---|
    |Basic details|Security group name|redshift_security_group|
    ||Description|Authorise redshift cluster access|
    ||VPC|Choose the default VPC. It is a VPC in a default region,and has a public subnet in each Availability Zone. If a default VPC doesn't show up, create a default VPC|
- In the Inbound rules section, click on **Add Rule** and enter the following values:

    |Section|Field|Value|
    |---|---|---|
    |Inbound rules|Type|Custom TCP Rule|
    ||Protocol|TCP|
    ||Port range|5439 The default port for Amazon Redshift is 5439, but your port might be different.|
    ||Source type|Custom
    ||Source|0.0.0.0/0 (Anywhere in the world)
- Outbound rules allow traffic to anywhere by default.
- Click on the Create security group button at the bottom. You will see a success message.

    3.2. Cluter subnet group
    - Amazon Redshift → Configurations → Subnet groups
    - Name: cluter-subnet-group-1
    - Add subnets → Add all the subnets for this VPC

4. Launch a Redshift Cluster
- On the Amazon Redshift Dashboard, choose **Create cluster**. It will launch the Create cluster wizard.
- **Cluster configuration**
    - Provide a unique identifier, such as redshift-cluster-1, and choose the Free trial option. It will automatically, choose the following configuration:
        - 1 node of dc2.large hardware type. It is a high performance with fixed local SSD storage
        - 2 vCPUs
        - 160 GB storage capacity
- **Database configurations**
    - A few fields will be already filled up by default. Ensure to have to the following values:

    |Field|Value|
    |---|---|
    |Database name| dev|
    |Database port| 5439|
    |Master user name |awsuser|
    |Master user password|Enter a password of awsuser|
- **Cluster permissions (optional)**
    - Choose the IAM role created earlier, myRedshiftRole, from the drop-down and click on the Associate IAM role button.
- **Additional configurations**
    - Toggle the button to turn off the "use defaults" feature, and expand the Network and security section. Choose the following values:

    |Field|Value|
    |---|---|
    |Virtual private cloud (VPC)|Default VPC|
    VPC security groups	|Choose the redshift_security_group created earlier.|
    |Cluster subnet group|Choose the default. It is the one you have just created.|
    |Availability Zone|No preference|
    |Enhanced VPC routing|Disabled|
    |Publicly accessible|Enable|
- Review your Cluster configuration and click on the **Create cluster** button at the bottom. It will take a few minutes to finish and show you a **Complete** status.
- Click on the **Clusters** menu item from the left navigation pane, and look at the cluster that you just launched. Make sure that the **Status** is **Available** before you try to connect to the database later. You can expect this to take 5-10 minutes.

5. Configure Redshift Serverless in AWS.
- Grant Redshift access to S3 so it can copy data from CSV files
    - Create a Redshift Role called `my-redshift-service-role` from the AWS Cloudshell:
        ```
        aws iam create-role --role-name my-redshift-service-role --assume-role-policy-document '{
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "Service": "redshift.amazonaws.com"
                    },
                    "Action": "sts:AssumeRole"
                }
            ]
        }'
        ```
    - Now give the role S3 Full Access:
        ```
        aws iam attach-role-policy --policy-arn arn:aws:iam::aws:policy/AmazonS3FullAccess --role-name my-redshift-service-role
        ```
    - Open the AWS console.
    - Search **Redshift** in the search bar, and then click on **Amazon Redshift**.
    - Click **Redshift Serverless**.
    - Click **Customize settings**.
    - Go with the default namespace name.
    - Check the box Customize admin user credentials.
    - Enter **awsuser** for the Admin user name.
    - Enter a password (R3dsh1ft).
    - Associate the `my-redshift-service-role` you created with Redshift (Hint: If the role you created didn't show up, refresh the page).
    - This will enable Redshift Serverless to connect with S3.
    - Accept the defaults for **Security and encryption**.
    - Accept the default **Workgroup** settings.
    - Select **Turn on enhanced VPC routing** and click **Save**.
    - Click **Continue** and wait for **Redshift Serverless** setup to finish.
    - On succesful completion, you will see Status Available, as shown below.
    - Click the **default** Namespace.
    - Click the **default** Workgroup.
    - Next, we are going to make this cluster publicly accessible as we would like to connect to this cluster via Airflow.
    - Click **Edit**
    - Select **Turn on Publicly accessible**.
    - Click **Save**.
    - Go to redshift-cluster-1 -> **Actions** -> **Modify publicly accessible setting**.
    - Click on **Enable** and **Save changes**.
    - Back to **default-workgroup**
    - Choose the link labeled **VPC security group** to open the Amazon Elastic Compute Cloud (Amazon EC2) console.
    - Go to **Inbound Rules** tab and click on **Edit inbound rules**.
    - Add an inbound rule, as shown in the image below.
        - Type = Custom TCP
        - Port range = 0 - 5500
        - Source = Anywhere-iPv4
    - Now Redshift Serverless should be accessible from Airflow.

    - Go back to the Redshift Workgroup and copy the endpoint. Store this locally as we will need this while configuring Airflow.

6. Add Airflow Connections to AWS Redshift
- Here, we'll use Airflow's UI to connect to AWS Redshift
    - To go to the Airflow UI:
    - Click on the **Admin** tab and select **Connections**.
    - Under **Connections**, select **Create**.
    - Under Connections, click the plus button.
    - In AWS Redshift Serverless Dashboard, click the default Workgroup
    - Copy the Redshift endpoint, found by clicking the Workgroup link
    - On the Airflow create connection page, enter the following values:

        - **Connection Id**: Enter redshift.
        - **Connection Type**: Choose Amazon Redshift.
        - **Host**: Enter the endpoint of your Redshift Serverless workgroup, excluding the port and schema name at the end. You can find this by selecting your workgroup in the Amazon Redshift console. See where this is located in the screenshot below. IMPORTANT: Make sure to NOT include the port and schema name at the end of the Redshift endpoint string.
        - **Schema**: Enter dev. This is the Redshift database you want to connect to.
        - **Login**: Enter awsuser.
        - **Password**: Enter the password you created when launching - Redshift serverless (R3dsh1ft). 
        - **Port**: Enter 5439. Once you've entered these values, select **Save**.

### Project instruction
#### DAGs Workflow
<img src="images_result\dag_workflow.png" class="img-responsive" alt=""> </div>

### AWS Architecture ([link](https://viewer.diagrams.net/?tags=%7B%7D&highlight=0000ff&edit=_blank&layers=1&nav=1&title=automated_pipeline_airflow.drawio#R7VtbU9s4FP41PDZj2fElj7lAtzN0tgvs9PKSEbGSuDhWKisk7K%2FfI1tKbElOAo2BtrTM4HMkS%2Fa5fOdiceYNF5v3DC%2FnH2lM0jPXiTdn3ujMdRHq%2BfBLcB5KToCCkjFjSSwn7RjXyX9EMh3JXSUxyWsTOaUpT5Z15oRmGZnwGg8zRtf1aVOa1ndd4hkxGNcTnJrcz0nM5yU38p0d%2Fy%2BSzOZqZ%2BTIkQVWkyUjn%2BOYriss7%2FzMGzJKeXm12AxJKoSn5FLed9Ewun0wRjJ%2BzA33w%2BjqK7tZRmm8mo5uvn38gMJ3cpV7nK7kC%2Fc%2FXwNjmNJVLJ%2BbPyhhLGmS8UKg%2FgB%2BYL%2Bhc%2BbDyFBQHdfXGDod1hnIpMQadYZOh3UG0pdH2v5If8AKw6Bqyzva%2Fk7lAeHHG9AVT5OMDLem5wBzxnCcgEqGNKUMeBnNQHqDOV%2BkQCG4XM8TTq6XeCKkuga3Ad6UZlwaP3IVLQUvVgXz5hj2YnKNQhOEnd%2BTUiHlnDTFyzy53d7FyGTF8uSeXJG8XFxwwRCX4nqxmQmf7eB13u3MGF0ti8f%2FAHtZR8dwOZ4IwxjjlIuFOKN3RL3omevB%2FwthfINpkqaaAO4J4wn4VT9NZmJ9TsV2WFIpmRYrglSSbHZZUCPPkZKwbRHjfE5i%2BUrSimELsml0D7R1OkArQheEsweYom4IpJ9KoEKRpNc7t0eOcuZ5xec95fJYYs1su%2FjOHeFCeuQjvNP1Dfc0fJLEgFeSpIzP6YxmOD3fcQeguyzeimo355IKFRTm9J1w%2FiDtD684rRvsNKXrfpYAoiWFaaCt7hUkulsdiMdp1MA%2BCMrpik3IPmFI9MdsRvat53btemYkhRe4rz%2Fd6VV2WGP5HeGTuVSHFVKtsGqDViu8mhBbm1aAnmUHnWnjhSYTmdMUTppMG88WFPS7keVupN3dDMlNEKJDNYxdXHQvokFlbJQAiEq7z4TvaOgG9wyGyPMDGx5Oi386WCkkvMS3JP1E80Quf0s5p4uDUDkhAvk1Dz0QPnC%2BLMUxTTbiOewxgJHSCcsIANEjt8WCBc4g6YnHa8ruBDLk4yllYwzIPSdjnDDBOxaSmwGhEac9V8NptW4Fp8PIRGnFO73Hey%2BBySBC9vBF3l8QXwUBPiLJ0aY6OHqoUp8IS%2BDli2zCeTUAj7xjEf4lAV495T6E32m3Kd%2BraHJbF6AWvaarOY1jJjfbkqvqNch9fG7zb07Y37ffBeC4TipAriomWb2VrGsQpjNYTSAilqP7RV%2BN7FJXb3H1l4irgdP3vPBxcdUNQ4T%2BnLiaey36f6j5v28GzcDi%2FsHjvR%2FICgA8BlhtxU5QFJpC7DVfD36sqBp4V5a2fZiAguWmEKIah6uZ%2FF0sdKsYAnhKFjzvrT4NeOWWiq3hOyiHayBeM1FZ8lqqYMPYdJtcJHFcZAi2qFHPGlrLsDRbCYMO6h1lLl5bhbBqGrZhGymddb7n4I%2FKRpgaAWbTEOS5PMl5Xhtu32xkm%2BQVGg3SM4xuYJgMsnVPwtZsJmy0mTlSOrrEWZxkM5j2TUh6p8jdlBOqUba3gOHvqJsi43%2FnOg36o6CssqYazUHPJHs2nYahljRaVNqzqLTblko9ZCjjOUqtTcK%2FVK4rhRZQuzpLELUy6%2Fcqz8q%2B2jHlWfSS9Zl6zJ8JFd2GUHGD87vcDAaj%2FnsL93oCqekqJezY8HCgTrRnr7WiZ19yXUuV9Ty2tbJTb6p7Zt1pjQpPSDyPNI8TZBJN5tEvemAwoy%2B7YG6AF0JJ2W2%2BfEsv5Spur1e3iZ6ZXFptorXs0nuZDt5TwgoQenR4aqgxI4gtzrQeVaJjo0r4olElssDG23edX6b%2F1Ov6owv3QIjU%2Bk9%2B33MGvoG%2Bv2v%2FiZE4nyfTXUQ6PfQHXVSH%2Fhf%2FdtNrLxu4UvJ0nWvCQJgpySFNdMCIXKcyOExXOT8%2BS%2Fy9k4NAdQGlhbiOtfm0zSOfJT9wmzsJp%2BtMbuuGPiQRD6AXYStrkOacrnJiTmufc8gSX99XrrCnlRttfuY6Mrc8QTnqNtjOPytSvH2MOX46fBwPC0ycIsO742X1HEeEaZHlypNmj0Gm1uwB6eWnb9hD9KyVhvmNo79cpg9%2Ftpq8XnRQTf6zqsnWJNiX7f9UemoROEzvjtyw32%2FSzqtLPPUDqag5GS0zn%2FEPgV5jEiecsvG964zTUrOtmVkUFqVG7SOFmX92e6ahKd7pDe0EmcUR%2BacKFOeFsN%2FaUlbr0M%2BV9Sytyu5zohCK9qRcz3xs7GSfII4%2BDCalerAvVJ7HerHTYM7hSGHp4TciteEpxfmpAZ7czQrd25oQDR8GDO0YbQzHiZwLR0%2FOa6FFh%2FCE5mEnmdAs7xRZ50mO3vtdDZc9x%2B9EkeF%2BQaDm1ZoDvuKeXrvmn8cosMyXOPupwu8Kr83UvVz1Vz8%2BcEDbdZz1QrejzlRW20DIEobdR%2BsZyN1fWBVjlb9T887%2FBw%3D%3D) to draw.io)

<img src="images_result\image.gif" class="img-responsive" alt=""> </div>
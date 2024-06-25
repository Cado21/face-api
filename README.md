# Project Documentation:

Python Version: 3.12.4
Pip version: pip 24.0

## Step 1: (Optional) Create virtual Environtment 

 
*IMPORTANT: skip this step if already have your own environtment*

Create Virtual Environtment:

```python3 -m venv myenv```

Replace `myenv` with your preferred name for the virtual environment directory.


## Step 2: Activate the virtual environtment

On macOS or Linux:
```source myenv/bin/activate```


on Windows:
```myenv\Scripts\activate```

## Step 3: Install the package

To install the package please run this:

```python3 -m pip install -r requirements.txt```

## Additional Notes

 - **Deactivating the virtual environment**: When you are done working in the virtual environment, you can deactivate it by running:

   ```deactivate```
 
 - **Reactivating** the virtual environment: To activate the virtual environment again in the future, navigate to your project directory and run the activation command again.

 - **Virtual environment directory**: It's a good practice to include the virtual environment directory (myenv in this example) in your .gitignore file if you are using version control to avoid committing it to your repository.


 # Environtment Variables:

1. Please create .env file in root folder
2. replace [variable] with your string, like this:
```
GOOGLE_APPLICATION_CREDENTIALS=secrets/[your-service-account].json
FIREBASE_STORAGE_BUCKET=[firebase-storage-bucketname]
```
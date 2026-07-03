import os  
for folder in ['tools','memory','ui','data']:  
    os.makedirs(folder, exist_ok=True)  
for f in ['main.py','.env','requirements.txt']:  
    open(f,'a').close()  
print('Folders and files created successfully!') 

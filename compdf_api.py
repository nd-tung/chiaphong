"""
ComPDF API integration for Excel to PDF conversion
"""
import os
import json
import requests
import traceback
import time

def convert_excel_to_pdf(excel_path):
    """Convert Excel to PDF using ComPDF API"""
    # ComPDF API credentials from environment variables
    PUBLIC_KEY = os.environ.get('COMPDF_PUBLIC_KEY')
    SECRET_KEY = os.environ.get('COMPDF_SECRET_KEY')
    
    if not PUBLIC_KEY or not SECRET_KEY:
        print("ERROR: ComPDF API credentials not found in environment variables")
        print("Please set COMPDF_PUBLIC_KEY and COMPDF_SECRET_KEY")
        return None
    
    try:
        # Step 1: Get the list of available tools
        tools_url = "https://api-server.compdf.com/server/v1/pdf/tools"
        tools_headers = {
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        print("Getting available PDF tools...")
        tools_response = requests.get(tools_url, headers=tools_headers, timeout=30)
        
        if tools_response.status_code != 200:
            print(f"Failed to get tools: {tools_response.text}")
            return None
            
        tools_result = tools_response.json()
        if tools_result.get('code') != 200:
            print(f"Tools request failed: {tools_result}")
            return None
            
        # Find the office-to-pdf tool URL
        tools_data = tools_result.get('data', [])
        office_to_pdf_url = None
        
        for tool in tools_data:
            if tool.get('toolType') == 'office-to-pdf':
                office_to_pdf_url = tool.get('toolUrl')
                break
                
        if not office_to_pdf_url:
            print("office-to-pdf tool not found in available tools")
            # Try a fallback URL
            office_to_pdf_url = "https://api-server.compdf.com/server/v1/office/pdf"
            print(f"Using fallback URL: {office_to_pdf_url}")
        else:
            print(f"Using office-to-pdf tool: {office_to_pdf_url}")
        
        # Step 2: Create conversion task
        create_task_url = "https://api-server.compdf.com/server/v1/task"
        create_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        create_payload = {
            "executeTypeUrl": office_to_pdf_url,
            "language": "english"
        }
        
        print("Creating ComPDF conversion task...")
        create_response = requests.post(create_task_url, headers=create_headers, json=create_payload, timeout=30)
        
        if create_response.status_code != 200:
            print(f"Failed to create task: {create_response.text}")
            return None
            
        create_result = create_response.json()
        if create_result.get('code') != 200:
            print(f"Task creation failed: {create_result}")
            return None
            
        task_id = create_result['data']['taskId']
        print(f"Task created: {task_id}")
        
        # Step 3: Upload file
        upload_url = "https://api-server.compdf.com/server/v1/file/upload"
        upload_headers = {
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        with open(excel_path, 'rb') as f:
            files = {
                'file': (os.path.basename(excel_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            upload_data = {
                'taskId': task_id,
                'language': 'english'
            }
            
            print("Uploading Excel file...")
            upload_response = requests.post(upload_url, headers=upload_headers, files=files, data=upload_data, timeout=60)
        
        if upload_response.status_code != 200:
            print(f"Failed to upload file: {upload_response.text}")
            return None
            
        upload_result = upload_response.json()
        if upload_result.get('code') != 200:
            print(f"File upload failed: {upload_result}")
            return None
            
        file_key = upload_result['data']['fileKey']
        print(f"File uploaded: {file_key}")
        
        # Step 4: Execute conversion
        execute_url = "https://api-server.compdf.com/server/v1/execute/start"
        execute_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        execute_payload = {
            "taskId": task_id,
            "fileKey": file_key
        }
        
        print("Starting conversion...")
        execute_response = requests.post(execute_url, headers=execute_headers, json=execute_payload, timeout=30)
        
        if execute_response.status_code != 200:
            print(f"Failed to execute conversion: {execute_response.text}")
            return None
            
        execute_result = execute_response.json()
        if execute_result.get('code') != 200:
            print(f"Conversion execution failed: {execute_result}")
            return None
            
        print("Conversion started, waiting for completion...")
        
        # Step 5: Check status and download
        max_attempts = 30  # Wait up to 5 minutes
        for attempt in range(max_attempts):
            time.sleep(10)  # Wait 10 seconds between checks
            
            print(f"Checking status... (attempt {attempt + 1}/{max_attempts})")
            
            # Check file info to get status
            status_url = f"https://api-server.compdf.com/server/v1/file/fileInfo?fileKey={file_key}&language=english"
            status_headers = {
                "Authorization": f"Bearer {PUBLIC_KEY}"
            }
            
            status_response = requests.get(status_url, headers=status_headers, timeout=30)
            
            if status_response.status_code != 200:
                print(f"Failed to check status: {status_response.text}")
                continue
                
            status_result = status_response.json()
            if status_result.get('code') != 200:
                print(f"Status check failed: {status_result}")
                continue
                
            task_status = status_result['data'].get('status')
            print(f"Task status: {task_status}")
            
            if task_status == 'TaskFinish':
                # Download the converted PDF
                download_url = status_result['data'].get('downloadUrl')
                if not download_url:
                    print("No download URL found")
                    return None
                    
                print(f"Downloading PDF from: {download_url}")
                
                download_response = requests.get(download_url, timeout=60)
                if download_response.status_code == 200:
                    return download_response.content
                else:
                    print(f"Failed to download PDF: {download_response.text}")
                    return None
                    
            elif task_status in ['TaskFail', 'TaskError']:
                failure_reason = status_result['data'].get('failureReason', 'Unknown error')
                print(f"Task failed: {failure_reason}")
                return None
            elif task_status == 'TaskProcessing':
                continue  # Keep waiting
                
        print("Timeout waiting for conversion to complete")
        return None
        
    except Exception as e:
        print(f"ComPDF API error: {e}")
        traceback.print_exc()
        return None

# Alternative implementation for direct API access without tool discovery
def convert_excel_to_pdf_direct(excel_path):
    """Convert Excel to PDF using ComPDF API (direct method)"""
    import requests
    import json
    import os
    import time
    
    # ComPDF API credentials from environment variables
    PUBLIC_KEY = os.environ.get('COMPDF_PUBLIC_KEY')
    SECRET_KEY = os.environ.get('COMPDF_SECRET_KEY')
    
    if not PUBLIC_KEY or not SECRET_KEY:
        print("ERROR: ComPDF API credentials not found in environment variables")
        print("Please set COMPDF_PUBLIC_KEY and COMPDF_SECRET_KEY")
        return None
    
    try:
        # Step 1: Create task - using direct Office to PDF endpoint
        create_task_url = "https://api-server.compdf.com/server/v1/office/pdf/task"
        create_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        create_payload = {
            "language": "english"
        }
        
        print("Creating ComPDF conversion task...")
        create_response = requests.post(create_task_url, headers=create_headers, json=create_payload, timeout=30)
        
        if create_response.status_code != 200:
            print(f"Failed to create task: {create_response.text}")
            return None
            
        create_result = create_response.json()
        if create_result.get('code') != 200:
            print(f"Task creation failed: {create_result}")
            return None
            
        task_id = create_result['data']['taskId']
        print(f"Task created: {task_id}")
        
        # Step 2: Upload file
        upload_url = "https://api-server.compdf.com/server/v1/file/upload"
        upload_headers = {
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        with open(excel_path, 'rb') as f:
            files = {
                'file': (os.path.basename(excel_path), f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            upload_data = {
                'taskId': task_id
            }
            
            print("Uploading Excel file...")
            upload_response = requests.post(upload_url, headers=upload_headers, files=files, data=upload_data, timeout=60)
        
        if upload_response.status_code != 200:
            print(f"Failed to upload file: {upload_response.text}")
            return None
            
        upload_result = upload_response.json()
        if upload_result.get('code') != 200:
            print(f"File upload failed: {upload_result}")
            return None
            
        file_key = upload_result['data']['fileKey']
        print(f"File uploaded: {file_key}")
        
        # Step 3: Execute conversion
        execute_url = "https://api-server.compdf.com/server/v1/office/pdf/convert"
        execute_headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        execute_payload = {
            "taskId": task_id,
            "fileKey": file_key
        }
        
        print("Starting conversion...")
        execute_response = requests.post(execute_url, headers=execute_headers, json=execute_payload, timeout=30)
        
        if execute_response.status_code != 200:
            print(f"Failed to execute conversion: {execute_response.text}")
            return None
            
        execute_result = execute_response.json()
        if execute_result.get('code') != 200:
            print(f"Conversion execution failed: {execute_result}")
            return None
            
        print("Conversion started, waiting for completion...")
        
        # Step 4: Check status and download
        status_url = f"https://api-server.compdf.com/server/v1/file/fileInfo"
        status_headers = {
            "Authorization": f"Bearer {PUBLIC_KEY}"
        }
        
        max_attempts = 30  # Wait up to 5 minutes
        for attempt in range(max_attempts):
            time.sleep(10)  # Wait 10 seconds between checks
            
            print(f"Checking status... (attempt {attempt + 1}/{max_attempts})")
            
            # Check file info to get status
            full_status_url = f"{status_url}?fileKey={file_key}&language=english"
            status_response = requests.get(full_status_url, headers=status_headers, timeout=30)
            
            if status_response.status_code != 200:
                print(f"Failed to check status: {status_response.text}")
                continue
                
            status_result = status_response.json()
            if status_result.get('code') != 200:
                print(f"Status check failed: {status_result}")
                continue
                
            status_data = status_result.get('data', {})
            task_status = status_data.get('status')
            print(f"Task status: {task_status}")
            
            if task_status == 'TaskFinish':
                # Download the converted PDF
                download_url = status_data.get('downloadUrl')
                if not download_url:
                    print("No download URL found")
                    return None
                    
                print(f"Downloading PDF from: {download_url}")
                
                download_response = requests.get(download_url, timeout=60)
                if download_response.status_code == 200:
                    return download_response.content
                else:
                    print(f"Failed to download PDF: {download_response.text}")
                    return None
                    
            elif task_status in ['TaskFail', 'TaskError']:
                failure_reason = status_data.get('failureReason', 'Unknown error')
                failure_code = status_data.get('failureCode', 'Unknown code')
                print(f"Task failed: Code={failure_code}, Reason={failure_reason}")
                return None
                
        print("Timeout waiting for conversion to complete")
        return None
        
    except Exception as e:
        print(f"ComPDF API error: {e}")
        import traceback
        traceback.print_exc()
        return None

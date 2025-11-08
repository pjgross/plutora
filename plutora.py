import json
import requests
import pandas as pd
from datetime import datetime
from typing import Optional, Dict, Any, List
from urllib.parse import quote
from pandas import Series
from typing import Union

with open("credentials.cfg") as data_file:
    data = json.load(data_file)

authUrl = data["urls"]["authUrl"]
baseUrl = data["urls"]["baseUrl"]
client_id = data["credentials"]["client_id"]
client_secret = data["credentials"]["client_secret"]
username = data["credentials"]["username"]
password = data["credentials"]["password"]

def getAccessToken():
    """Returns access_token"""
    headers = {}
    headers['content-type'] = "application/x-www-form-urlencoded"
    headers['cache-control'] = "no-cache"
    
    url = authUrl + "oauth/token"
    payload = "client_id=" + client_id + '&'
    payload += "client_secret=" + client_secret + '&'
    payload += "grant_type=" + 'password&'
    payload += "username=" + username.replace('@','%40') + '&'
    payload += "password=" + password + '&'
    
    response = requests.request("POST", url, data=payload, headers=headers)
    
    if not response.ok:
        print("Access token: ")
        print(response.text)
        exit()
        
    access_token = response.json()['access_token']
    return access_token

def Get_Envs_List(token: str):
    """
    Enriches booking data by replacing releaseId and environmentId with their respective names.
    
    Args:
        bookings_data (Dict): The original bookings data
    
    Returns:
        Dict: Enhanced bookings data with release and environment names
    """
    
    # Create caches to avoid duplicate API calls
    End_List = {}

    # Construct the full URL
    url = f"https://ukapi.plutora.com/environments"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    response = requests.get(url, headers=headers)

    return response.json()

def Get_Rel_List(token: str):
    """
    Enriches booking data by replacing releaseId and environmentId with their respective names.
    
    Args:
        bookings_data (Dict): The original bookings data
    
    Returns:
        Dict: Enhanced bookings data with release and environment names
    """
    
    # Create caches to avoid duplicate API calls
    End_List = {}

    # Construct the full URL
    url = f"https://ukapi.plutora.com/releases"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    response = requests.get(url, headers=headers)

    return response.json()

def Get_Rel_Status_List(token: str):
    """
    Enriches booking data by replacing releaseId and environmentId with their respective names.
    
    Args:
        bookings_data (Dict): The original bookings data
    
    Returns:
        Dict: Enhanced bookings data with release and environment names
    """
    
    # Create caches to avoid duplicate API calls
    End_List = {}

    # Construct the full URL
    url = f"https://ukapi.plutora.com/lookupfields/ReleaseStatusType"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    response = requests.get(url, headers=headers)

    return response.json()


def get_bookings_on_date(token, date_time: str = "2025-06-01T09:00:00") -> dict[str, Any] | None:
    """
    Retrieves bookings from Plutora API for a specific date/time.
    
    Args:
        date_time (str): The date and time to filter bookings (ISO format)
                        Default: "2025-06-01T09:00:00"
    
    Returns:
        Dict: JSON response from the API containing booking data
    """
    
    # Construct the filter query
    filter_query = f"`startDate` <= `{date_time}` and `endDate` >= `{date_time}`"
    
    # URL encode the filter parameter
    encoded_filter = quote(filter_query)
    
    # Construct the full URL
    url = f"https://ukapi.plutora.com/Bookings?filter={encoded_filter}"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        response.raise_for_status()

def get_tecrs(token: str, start_date_time: str = "2025-06-01", end_date_time: str = "2025-12-01") -> dict[str, Any] | None:
    """
    Retrieves bookings from Plutora API for a specific date/time.
    
    Args:
        date_time (str): The date and time to filter bookings (ISO format)
                        Default: "2025-06-01T09:00:00"
    
    Returns:
        Dict: JSON response from the API containing booking data
    """
    
    # Construct the filter query
    filter_query = f"`startDate` >= `{start_date_time}` and `startDate` <= `{end_date_time}`"
    
    # URL encode the filter parameter
    encoded_filter = quote(filter_query)
    
    # Construct the full URL
    url = f"https://ukapi.plutora.com/TECRs?filter={encoded_filter}"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers)
    
    # Check if request was successful
    if response.ok:
        return response.json()
    else:
        print(f"Error: {response.status_code}")
        print(response.text)
        response.raise_for_status()

def get_release_name(release_id: str, token: str) -> str:
    """
    Retrieves the release name for a given release ID.
    
    Args:
        release_id (str): The release ID to look up
        token (str): Authorization token
    
    Returns:
        str: The release name, or the original release_id if lookup fails
    """
    if not release_id or release_id == "00000000-0000-0000-0000-000000000000":
        return release_id
    
    # Construct the filter query for the specific release ID
    filter_query = f"`id` = `{release_id}`"
    
    # URL encode the filter parameter
    encoded_filter = quote(filter_query)
    
    # Construct the full URL
    url = f"https://ukapi.plutora.com/releases?filter={encoded_filter}"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }
    
    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        
        if response.ok:
            releases = response.json()
            if releases and len(releases) > 0:
                return releases[0].get('name', release_id)
            else:
                print(f"No release found for ID: {release_id}")
                return release_id
        else:
            print(f"Error fetching release {release_id}: {response.status_code}")
            return release_id
            
    except Exception as e:
        print(f"Exception fetching release name for {release_id}: {e}")
        return release_id
    
def get_environment_name(environment_id: str, token: str) -> str:
    """
    Retrieves the environment name for a given environment ID.
    
    Args:
        environment_id (str): The environment ID to look up
        token (str): Authorization token
    
    Returns:
        str: The environment name, or the original environment_id if lookup fails
    """
    if not environment_id or environment_id == "00000000-0000-0000-0000-000000000000":
        return environment_id
    
    # Construct the filter query for the specific environment ID
    filter_query = f"`id` = `{environment_id}`"
    
    # URL encode the filter parameter
    encoded_filter = quote(filter_query)
    
    # Construct the full URL
    url = f"https://ukapi.plutora.com/environments?filter={encoded_filter}"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }
    
    try:
        # Make the GET request
        response = requests.get(url, headers=headers)
        
        if response.ok:
            environments = response.json()
            if environments and len(environments) > 0:
                return environments[0].get('name', environment_id)
            else:
                print(f"No environment found for ID: {environment_id}")
                return environment_id
        else:
            print(f"Error fetching environment {environment_id}: {response.status_code}")
            return environment_id
            
    except Exception as e:
        print(f"Exception fetching environment name for {environment_id}: {e}")
        return environment_id
    
def enrich_bookings_with_names(bookings_data: Dict[Any, Any]) -> Dict[Any, Any]:
    """
    Enriches booking data by replacing releaseId and environmentId with their respective names.
    
    Args:
        bookings_data (Dict): The original bookings data
    
    Returns:
        Dict: Enhanced bookings data with release and environment names
    """
    result_set = bookings_data.get('resultSet', [])
    
    if not result_set:
        return bookings_data
    
    # Get access token for lookups
    token = getAccessToken()
    phases = Phase_id_to_name_Cache(token)
    # Create caches to avoid duplicate API calls
    release_name_cache = {}
    environment_name_cache = {}
    
    print(f"Fetching release and environment names for {len(result_set)} bookings...")
    
    # Process each booking
    for i, booking in enumerate(result_set):
        # Handle release ID
        release_id = booking.get('releaseId')
        if release_id and release_id != "00000000-0000-0000-0000-000000000000":
            # Check cache first
            if release_id in release_name_cache:
                release_name = release_name_cache[release_id]
            else:
                # Fetch release name and cache it
                release_name = get_release_name(release_id, token)
                release_name_cache[release_id] = release_name
                
            # Replace releaseId with releaseName
            booking['releaseName'] = release_name


            # Remove the original releaseId field
            del booking['releaseId']
           
        
        # Handle environment ID
        environment_id = booking.get('environmentId')
        if environment_id and environment_id != "00000000-0000-0000-0000-000000000000":
            # Check cache first
            if environment_id in environment_name_cache:
                environment_name = environment_name_cache[environment_id]
            else:
                # Fetch environment name and cache it
                environment_name = get_environment_name(environment_id, token)
                environment_name_cache[environment_id] = environment_name
                
            # Replace environmentId with environmentName
            booking['environmentName'] = environment_name

            # Remove the original environmentId field
            del booking['environmentId']
        booking['isEnvironmentGroup']  # Handle possible different casing  
        del booking['phaseId']
        #booking['Phase'] = phases[booking['phaseId']]
        #print(f"Phase {phases[booking.get('phaseId')]}")
        print(f"Processed {i + 1}/{len(result_set)} bookings", end='\r')
    
    print(f"\nCompleted processing all {len(result_set)} bookings")
    print(f"Found {len(release_name_cache)} unique releases")
    print(f"Found {len(environment_name_cache)} unique environments")
    
    return bookings_data

def export_bookings_to_excel(bookings_data: Dict[Any, Any], filename: str = "", include_names: bool = True) -> str:
    """
    Exports the resultSet from bookings data to an Excel file.
    
    Args:
        bookings_data (Dict): The JSON response from get_bookings()
        filename (str): Optional custom filename. If None, generates timestamp-based name.
        include_names (bool): If True, fetches release and environment names instead of IDs
    
    Returns:
        str: The filename of the created Excel file
    """
    # Enrich with release and environment names if requested
    if include_names:
        bookings_data = enrich_bookings_with_names(bookings_data)
    
    # Extract the resultSet array
    result_set = bookings_data.get('resultSet', [])
    
    if not result_set:
        print("No booking data found in resultSet")
        return ""
    
    # Create DataFrame from the resultSet
    df = pd.DataFrame(result_set)
    
    # Generate filename if not provided
    if filename is None:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"bookings_{timestamp}.xlsx"
    
    # Ensure filename has .xlsx extension
    if not filename.endswith('.xlsx'):
        filename += '.xlsx'
    
    # Export to Excel
    df.to_excel(filename, index=False, sheet_name='Bookings')
    
    print(f"Successfully exported {len(result_set)} booking records to {filename}")
    return filename

def get_and_export_bookings(date_time: str = "2025-09-01T09:00:00", filename: str = "", include_names: bool = True) -> str:
    """
    Convenience function that gets bookings and exports them to Excel in one call.
    
    Args:
        date_time (str): The date and time to filter bookings
        filename (str): Optional custom filename for the Excel file
        include_names (bool): If True, fetches release and environment names instead of IDs
    
    Returns:
        str: The filename of the created Excel file
    """
    try:
        # Get bookings data
        print("Fetching bookings data...")
        bookings = get_bookings_on_date(date_time)
        if bookings is None:
            raise ValueError("Bookings data is missing")
        # Export to Excel
        excel_filename = export_bookings_to_excel(bookings, filename, include_names)
        
        return excel_filename
        
    except Exception as e:
        print(f"Error retrieving and exporting bookings: {e}")
        raise

def Systems_id_to_name_Cache(token: str):
    """
    Enriches booking data by replacing releaseId and environmentId with their respective names.
    
    Args:
    
    Returns:
        Dict: system ids indexed by system name
    """
    
    # Create caches to avoid duplicate API calls
    System_cache = {}

    # Construct the full URL
    url = f"https://ukapi.plutora.com/systems"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    response = requests.get(url, headers=headers)
    for system in response.json():
        System_cache[system['id']] = system['name']

    return System_cache

def Phase_id_to_name_Cache(token: str):
    """
    Enriches booking data by replacing releaseId and environmentId with their respective names.
    
    Args:
    
    Returns:
        Dict: system ids indexed by system name
    """
    
    # Create caches to avoid duplicate API calls
    Phase_cache = {}

    # Construct the full URL
    url = f"https://ukapi.plutora.com/workitemnames/phases"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    response = requests.get(url, headers=headers)
    for system in response.json():
        Phase_cache[system['id']] = system['name']

    return Phase_cache

def Get_Bookings():
    token = getAccessToken()
    p_json = get_bookings_on_date(token)
    result_set = pd.DataFrame((p_json or {}).get('resultSet', []))

    p_envs = Get_Envs_List(token)
    envs_list = pd.DataFrame(p_envs)
    envs = envs_list.loc[:, ['id', 'name', 'linkedSystem']].rename(columns={'name': 'Environment Name', 'linkedSystem': 'System'})
    p_rels = Get_Rel_List(token)
    rel_list = pd.DataFrame(p_rels)
    rels = rel_list.loc[:, ['id', 'name', 'implementationDate']].rename(columns={'name': 'Release Name','implementationDate': 'Implementation Date'})
    merged_df = pd.merge(result_set, envs, left_on='environmentId', right_on='id', suffixes=('_booking', '_env'))
    #merged_df = merged_df[['Environment Name', 'startDate', 'endDate', 'System', 'releaseId', 'status', 'state']]
    merged_df = merged_df.merge(rels, left_on='releaseId', right_on='id').rename(columns={'status': 'Booking Status','state': 'Conflict State', 'startDate': 'Start Date', 'endDate': 'End Date'})
    merged_df = merged_df[['Environment Name', 'Start Date', 'End Date', 'System', 'Booking Status', 'Conflict State', 'Release Name', 'Implementation Date']]
    
    # automatically find all columns that look like dates
    date_cols = [
        col for col in merged_df.columns
        if merged_df[col].astype(str).str.match(r'\d{4}-\d{2}-\d{2}T').any()
    ]

    # convert and reformat each detected date column
    for col in date_cols:
        merged_df[col] = pd.to_datetime(merged_df[col], errors='coerce').dt.strftime('%d %b %Y %H:%M')

    return merged_df

def format_date_series(s: Union[Series, list, pd.Index]) -> Series:
    # ensure strings, strip whitespace
    s_str = pd.Series(s, dtype="string").str.strip()

    # 1) Try flexible parsing first — handles both with and without milliseconds
    dt = pd.to_datetime(s_str, errors="coerce")

    # 2) Fallback to explicit formats if any entries are still NaT
    if dt.isna().any():
        mask = dt.isna()
        for fmt in ("%Y-%m-%dT%H:%M:%S.%f", "%Y-%m-%dT%H:%M:%S", "%Y-%m-%dT%H:%M"):
            parsed = pd.to_datetime(s_str[mask], format=fmt, errors="coerce")
            dt.loc[mask] = parsed
            mask = dt.isna()
            if not mask.any():
                break

    # 3) Format to your desired output
    return dt.dt.strftime("%d %b %Y %H:%M")

# Function to call your API for one row
def get_tecr_customfields(row, token):
    url = f"https://ukapi.plutora.com/TECRs/{row.id}/additionalInformation"
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        items = response.json()
        result = {}
        for i, item in enumerate(items):
            name = item['name']
            data_type = item.get("dataType")

            # Pick the correct value depending on dataType
            if data_type == "FreeText":
                if item.get("text") == None:
                    result[name] = ""
                else:
                    result[name] = item.get("text")
            elif data_type == "ListField":
                if item.get("listItem") == None:
                    result[name] = ""
                else:
                    result[name] = item.get("listItem", {}).get("value")
            else:
                result[name] = ""

        return result
        # return a dict of the values you want to add


    except requests.RequestException as e:
        # handle network/API errors gracefully
        return {
            "api_status": None,
            "api_score": None,
            "api_message": f"Error: {e}"
        }
    
def Get_TECRs(startDate, endDate):
    token = getAccessToken()
    p_json = get_tecrs(token, startDate, endDate)
    result_set = pd.DataFrame(p_json)
    result = result_set.loc[:,['id','requestNumberIndex', 'title', 'crType', 'assignedTo', 'startDate', 'dueDate', 'description', 'releaseName', 'crStatus', 'outage', 'outageStartDate', 'outageEndDate']]
    
    date_cols = [
        col for col in result.columns
        if result[col].astype(str).str.match(r"\d{4}-\d{2}-\d{2}T").any()
    ]

    for col in date_cols:
        result[col] = format_date_series(result[col])

    result.fillna("", inplace=True)

    result.rename(columns={'requestNumberIndex': 'TECR No', 'title': 'Title', 'crType': 'TECR Type', 'assignedTo': 'Assigned To', 'startDate': 'Start Date', 'dueDate': 'Due Date', 'description': 'Description', 'releaseName': 'Release Name', 'crStatus': 'TECR Status', 'outage': 'Outage', 'outageStartDate': 'Outage Start Date', 'outageEndDate': 'Outage End Date'}, inplace=True)
    
    # Apply the function to each row and expand the dict into columns
    results = result.apply(get_tecr_customfields, axis=1, result_type='expand', args=(token,))
    
    df = pd.concat([result, results], axis=1)
    
    
    #result.set_index('id', inplace=True)
    return df

def get_rel_customfields(row, token):
    url = f"https://ukapi.plutora.com/releases/{row.id}/additionalInformation"
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        items = response.json()
        result = {}
        for i, item in enumerate(items):
            name = item['name']
            data_type = item.get("dataType")

            # Pick the correct value depending on dataType
            if data_type == "FreeText":
                if item.get("text") == None:
                    result[name] = ""
                else:
                    result[name] = item.get("text")
            elif data_type == "ListField":
                if item.get("listItem") == None:
                    result[name] = ""
                else:
                    result[name] = item.get("listItem", {}).get("value")
            else:
                result[name] = ""

        return result
        # return a dict of the values you want to add


    except requests.RequestException as e:
        # handle network/API errors gracefully
        return {
            "api_status": None,
            "api_score": None,
            "api_message": f"Error: {e}"
        }
    
def Get_Releases(startDate, endDate):
    token = getAccessToken()

    # Construct the filter query
    filter_query = f"`implementationDate` >= `{startDate}` and `implementationDate` <= `{endDate}`"
    
    # URL encode the filter parameter
    encoded_filter = quote(filter_query)
    
    # Construct the full URL
    url = f"https://ukapi.plutora.com/releases?filter={encoded_filter}"
    
    # Set up headers
    headers = {
        'accept': 'application/json',
        'Plutora-Info': 'script.name=swagger',
        'Authorization': f'bearer {token}'
    }
    
    # Make the GET request
    response = requests.get(url, headers=headers).json()
    
    result = pd.DataFrame(response)
    date_cols = [
        col for col in result.columns
        if result[col].astype(str).str.match(r"\d{4}-\d{2}-\d{2}T").any()
    ]

    for col in date_cols:
        result[col] = format_date_series(result[col])

    result.fillna("", inplace=True)
   
    # Apply the function to each row and expand the dict into columns
    results = result.apply(get_rel_customfields, axis=1, result_type='expand', args=(token,))
    
    df = pd.concat([result, results], axis=1)
    
    p_state = Get_Rel_Status_List(token)
    status_list = pd.DataFrame(p_state)
    states = status_list.loc[:, ['id', 'value']].rename(columns={'value': 'Release State'})
    merged_df = pd.merge(df, states, left_on='releaseStatusTypeId', right_on='id', suffixes=('_release', '_state'))

    
    #result.set_index('id', inplace=True)
    return merged_df.loc[:, ['id_release','identifier', 'name', 'Release State', 'implementationDate', 'plutoraReleaseType', 'releaseStatusMode', 'AgilePlaceRelId', 'AgilePlaceSysId', 'Categories', 'JiraId', 'Programme', 'Project']]

import os
import requests

# Define the directory containing the URLs and the directory to save the downloaded files
url_file = "/workspace/data/urls.txt"
save_dir = "/workspace/data/prices"

# Make sure the save directory exists
os.makedirs(save_dir, exist_ok=True)

# Open the file containing the URLs
with open(url_file, "r") as f:
    urls = f.read().splitlines()

# For each URL, download the file and save it to the specified directory
for url in urls:
    # Get the file name by splitting the URL and taking the last part
    file_name = url.split("=")[-1]
    # Create the path to save the file
    save_path = os.path.join(save_dir, file_name)

    # Send a HTTP request to the URL and save the response
    response = requests.get(url, stream=True)

    # Check if the request was successful
    if response.status_code == 200:
        # Open the save file in write mode
        with open(save_path, "wb") as fp:
            # Write the content of the response to the file
            for chunk in response.iter_content(chunk_size=1024):
                if chunk:
                    fp.write(chunk)
    else:
        print(f"Failed to download {url}")

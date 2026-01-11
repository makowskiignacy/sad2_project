import os
import glob
import csv
import urllib.request
import urllib.parse
import io
import re
import bn_simulator as bn

URL_SUMMARY = "https://raw.githubusercontent.com/sybila/biodivine-boolean-models/main/models/summary.csv"
URL_MODELS_PAGE = "https://github.com/sybila/biodivine-boolean-models/tree/main/models"
URL_BASE_RAW = "https://raw.githubusercontent.com/sybila/biodivine-boolean-models/main/models"

def fetch_available_models():
    try:
        response = urllib.request.urlopen(URL_SUMMARY).read().decode('utf-8')
    except Exception as e:
        return []
        
    available_models = []
    reader = csv.DictReader(io.StringIO(response), skipinitialspace=True)
    for row in reader:
        try:
            # Clean up keys and values
            row = {k.strip(): v.strip() for k, v in row.items()}
            num_vars = int(row['variables'])
            
            # We only want models with at most 16 nodes
            if num_vars <= 16:
                available_models.append({
                    "id": row['ID'],
                    "name": row['name'],
                    "vars": num_vars
                })
        except (ValueError, KeyError):
            continue
    return available_models

def find_model_folder_on_github(model_id):
    try:
        response = urllib.request.urlopen(URL_MODELS_PAGE).read().decode('utf-8')
        # Search for the path in the page source (GitHub embeds this in JSON-like structures)
        pattern = rf'"path":"models/([^"]*{model_id}[^"]*)"'
        match = re.search(pattern, response)
        return match.group(1) if match else None
    except Exception:
        return None

def download_bnet_model(model_info, destination_folder):
    local_path = os.path.join(destination_folder, f"{model_info['id']}_{model_info['name']}")
    os.makedirs(local_path, exist_ok=True)
    
    folder_name = find_model_folder_on_github(model_info['id'])
    if not folder_name:
        return

    # Construct the direct download URL
    encoded_folder = urllib.parse.quote(folder_name)
    download_url = f"{URL_BASE_RAW}/{encoded_folder}/model.bnet"
    save_file_path = os.path.join(local_path, "model.bnet")
    
    try:
        content = urllib.request.urlopen(download_url).read().decode('utf-8')
        with open(save_file_path, "w") as f:
            f.write(content)
    except Exception:
        pass

def ensure_models_are_present(models_dir):
    if os.path.exists(models_dir) and any(os.path.isdir(os.path.join(models_dir, d)) for d in os.listdir(models_dir)):
        return

    models = fetch_available_models()
    if not models:
        return

    # Sort models by number of variables to find the smallest and largest
    models.sort(key=lambda x: x['vars'])
    valid_models = [m for m in models if m['vars'] > 0]
    
    if valid_models:
        # Download the smallest model
        download_bnet_model(valid_models[0], models_dir)
        # Download the largest model (if it's different)
        if len(valid_models) > 1:
            download_bnet_model(valid_models[-1], models_dir)

def main():
    MODELS_DIR = "models"
    OUTPUT_DIR = "BN_data"
    
    os.makedirs(MODELS_DIR, exist_ok=True)
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Setup, make sure we have models to simulate
    ensure_models_are_present(MODELS_DIR)
    
    # Simulation, generate data for each model
    model_folders = sorted(glob.glob(os.path.join(MODELS_DIR, "*")))
    
    for folder in model_folders:
        if not os.path.isdir(folder): 
            continue
        
        bnet_file = os.path.join(folder, "model.bnet")
        if not os.path.exists(bnet_file):
            continue
            
        # Load the network rules
        network, node_names = bn.load_bnet(bnet_file)
        model_name = os.path.basename(folder)
            
        # Generate synchronous trajectories
        sync_data = [bn.simulate_sync(network, 50) for _ in range(10)]
        bn.save_bnf(os.path.join(OUTPUT_DIR, f"{model_name}_sync.data"), sync_data, node_names)
            
        # Generate asynchronous trajectories
        async_data = [bn.simulate_async(network, 50) for _ in range(10)]
        bn.save_bnf(os.path.join(OUTPUT_DIR, f"{model_name}_async.data"), async_data, node_names)
            
if __name__ == "__main__":
    main()

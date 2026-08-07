import paramiko
from scp import SCPClient
import sys
import time
import os

def create_ssh_client(server, port, user, password):
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    # We must use cloudflared as a proxy command for Cloudflare tunnels
    proxy_cmd = f"./cloudflared access ssh --hostname {server}"
    proxy = paramiko.ProxyCommand(proxy_cmd)
    
    print(f"Connecting to {server}:{port} as {user} via cloudflared proxy...")
    try:
        client.connect(server, port, user, password, sock=proxy, timeout=30)
        return client
    except Exception as e:
        print(f"Failed to connect: {e}")
        return None

def main():
    host = "whilst-skiing-tones-span.trycloudflare.com"
    port = 22
    user = "root"
    password = "metis123"
    
    # Ensure cloudflared exists and is executable
    if not os.path.exists("./cloudflared"):
        print("cloudflared binary not found! Please wait for it to download.")
        sys.exit(1)
        
    ssh = create_ssh_client(host, port, user, password)
    if not ssh:
        sys.exit(1)
        
    print("Successfully connected!")
    
    try:
        # 1. Setup colab environment
        print("Installing dependencies on Colab GPU...")
        stdin, stdout, stderr = ssh.exec_command("pip install -q transformers datasets seqeval accelerate")
        
        # Wait for pip install to finish
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print("Failed to install dependencies on Colab.")
            print(stderr.read().decode())
            return
            
        # 2. Upload script
        print("Uploading training script...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.put('/mnt/shared/Projects/Metis/ml/training/train_colab_script.py', '/content/train_colab_script.py')
            
        # 3. Execute script
        print("Running training script on Colab GPU... This will take a minute or two.")
        stdin, stdout, stderr = ssh.exec_command("python /content/train_colab_script.py")
        
        # Stream output
        for line in iter(stdout.readline, ""):
            print(line, end="")
            
        exit_status = stdout.channel.recv_exit_status()
        if exit_status != 0:
            print(f"Error running training script. Exit code: {exit_status}")
            err = stderr.read().decode()
            if err:
                print(err)
            return
            
        # 4. Download model
        print("Downloading trained model zip file...")
        with SCPClient(ssh.get_transport()) as scp:
            scp.get('/content/pii-roberta.zip', '/mnt/shared/Projects/Metis/pii-roberta.zip')
            
        print("Remote training and download complete!")
        
        # Unzip locally
        print("Extracting model locally...")
        os.system("cd /mnt/shared/Projects/Metis/ml/models && unzip -o ../../pii-roberta.zip > /dev/null")
        
    except Exception as e:
        print(f"An error occurred: {e}")
    finally:
        ssh.close()

if __name__ == "__main__":
    main()

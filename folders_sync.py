import os
import shutil
import time

LOG = 'log_file.txt'

# Log function
def log(message):
    now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    with open(LOG, 'a') as f:
        f.write('[' + now + ']' + message + '\n')

def sync_folders(source_folder, replica_folder):
    try:
        # Ensure the replica folder exists, create it if necessary
        if not os.path.exists(replica_folder):
            os.makedirs(replica_folder)

        # Walk through the source folder and its subfolders
        for root, _, files in os.walk(source_folder):
            for file in files:
                source_path = os.path.join(root, file)
                relative_path = os.path.relpath(source_path, source_folder)
                replica_path = os.path.join(replica_folder, relative_path)

                # Check if the file in the source folder is newer or missing in the replica
                if not os.path.exists(replica_path) or \
                        os.path.getmtime(source_path) > os.path.getmtime(replica_path):
                    shutil.copy2(source_path, replica_path)
                    print(f"Synced: {relative_path}")

        print("Synchronization completed.")

    except Exception as e:
        print(f"Error: {e}")

def compareHashFolder(source_folder, replica_folder):
    # compare hash folder
    # return True if all files are the same
    # return False if any file is different
    files = os.listdir(source_folder)
    files_backup = os.listdir(replica_folder)
    if len(files) != len(files_backup):
        return False

    for file in files:
        if file in files_backup:
            if not sync_folders(os.path.join(source_folder, file), os.path.join(replica_folder, file)):
                return False
        else:
            return False
    return True

if __name__ == "__main__":
    source_folder = "/Users/hello/sync_folders/source"
    replica_folder = "/Users/hello/sync_folders/replica"

    while True:
        if compareHashFolder(source_folder, replica_folder):
            now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f'[{now}] Files are up to date')
            log('Files are up to date')
            time.sleep(3600)
            continue

        print("Checking folder status...")
        # checking source folder
        if os.path.isdir(source_folder):
            print('Source Folder: Checked')
            log('Source Folder: Checked')
        else:
            print('Source folder is not exist')
            log('Source folder is not exist')
            break

        # Checking replica folder
        if os.path.isdir(replica_folder):
            print('Replica Folder: Checked')
            log('Replica Folder: Checked')
        else:
            print('Replica folder is not exist')
            log('Replica folder is not exist')
            break

        # Check file hash in Source and compare with Replica
        countSync = 0
        updateFile = 0
        deleteFile = 0

        # get all file in folder
        files = os.listdir(source_folder)
        # get all file in backup
        files_backup = os.listdir(replica_folder)
        # compare 2 list
        for file in files_backup:
            if file in files:
                if sync_folders(source_folder + '/' + file, replica_folder + '/' + file):
                    log(f'{file} is up to date')
                    countSync += 1
                else:
                    # copy file from folder to Replica
                    updateFile += 1
                    os.remove(replica_folder + '/' + file)
                    os.system('cp ' + source_folder + '/' + file + ' ' + replica_folder)
                    log(f'{file} is updated')
            if file not in files:
                # delete file in backup
                log(f'{file} is deleted')
                deleteFile += 1
                os.remove(replica_folder + '/' + file)

        for file in files:
            if file not in files_backup:
                # copy file from folder to Replica
                updateFile += 1
                log(f'{file} is copied')
                os.system('cp ' + source_folder + '/' + file + ' ' + replica_folder)

        now = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
        print(f'[{now}] sync: {countSync}; update: {updateFile}; delete: {deleteFile};')

        # Sleep for 1 hour
        time.sleep(3600)

import os


def create_folder():
    # Path to the folder in ProgramData directory
    folder_path = os.path.join(os.environ['ProgramData'], 'logger')
    ss_path = os.path.join(folder_path, 'screenshots')
    logs_path = os.path.join(folder_path, 'logs')

    # Create the folder if it doesn't exist
    if not os.path.exists(folder_path):
        os.makedirs(folder_path)
        os.makedirs(ss_path)
        os.makedirs(logs_path)

    # Set the folder's access permissions to 0o777
    os.chmod(folder_path, 0o777)

    return folder_path


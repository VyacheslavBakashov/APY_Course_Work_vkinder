import os

folder = 'config'
file_user_token = 'user_token_.txt'
file_group_token = 'vk_group_token_.txt'
file_db_password = 'db_pwd_.txt'

with open(os.path.join(folder, file_user_token), encoding='utf-8') as file:
    token_ = file.readline().strip()

with open(os.path.join(folder, file_group_token), encoding='utf-8') as file2:
    vk_group_token = file2.readline().strip()

with open(os.path.join(folder, file_db_password), encoding='utf-8') as f:
    pwd = f.readline()

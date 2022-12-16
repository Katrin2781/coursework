import VK
import YDisk
import os
import json

def read_token(file_name):
    with open(os.path.join(os.getcwd(), file_name), 'r') as tokenFile:
        token = tokenFile.readline().strip()
        id_user = tokenFile.readline().strip()
    return [token, id_user]


if __name__ == '__main__':
    # копирование фотографий из профиля VK
    my_VK_profile = VK.VK_user(read_token('token.txt'), 'profile')
    with open('my_photos_VK_prof.json', 'w') as pfile:
        json.dump(my_VK_profile.jsonList, pfile)
    my_YA = YDisk.Yandex('Photo VK_profile', read_token('token_Y.txt'),5)
    my_YA.load_Y_disk(my_VK_profile.exp_dict)

    # копирование фотографий со стены VK
    my_VK_wall = VK.VK_user(read_token('token.txt'), 'wall')
    with open('my_photos_VK_saved.json', 'w') as wfile:
        json.dump(my_VK_wall.jsonList, wfile)
    my_YA = YDisk.Yandex('Photo VK_wall', read_token('token_Y.txt'),15)
    my_YA.load_Y_disk(my_VK_wall.exp_dict)

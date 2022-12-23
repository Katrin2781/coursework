import VK
import YDisk
import json
import configparser


def read_token(access_obj):
    config = configparser.ConfigParser()
    config.read('setting.ini')
    token = config[access_obj]['TOKEN']
    return token


if __name__ == '__main__':
    # копирование фотографий из профиля VK
    id_user = input("Введите идентификатор пользователя VK или короткое имя: ")
    my_VK_profile = VK.VKUser(read_token('VK'), id_user, 'profile')
    quan_photo = int(input("Введите количество копируемых фотографий профиля: "))
    with open('my_photos_VK_prof.json', 'w') as pfile:
        json.dump(my_VK_profile.jsonList, pfile)
    my_YA = YDisk.Yandex('Photo VK_profile', read_token('Yandex'), quan_photo)
    my_YA.load_y_disk(my_VK_profile.exp_dict)

#    копирование фотографий со стены VK
    my_VK_wall = VK.VKUser(read_token('VK'), id_user, 'wall')
    quan_photo = int(input("Введите количество копируемых фотографий со стены: "))
    with open('my_photos_VK_saved.json', 'w') as wfile:
        json.dump(my_VK_wall.jsonList, wfile)
    my_YA = YDisk.Yandex('Photo VK_wall', read_token('Yandex'), quan_photo)
    my_YA.load_y_disk(my_VK_wall.exp_dict)

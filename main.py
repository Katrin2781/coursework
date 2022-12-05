import datetime
import os
from pprint import pprint
import json
import requests
from tqdm import tqdm

def read_token(file_name):
    with open(os.path.join(os.getcwd(), file_name), 'r') as tokenFile:
        token = tokenFile.readline().strip()
        id_user = tokenFile.readline().strip()
    return [token, id_user]

def find_max_size(search_max):
    """Возвращает ссылку на фото максимального размера и размер фото"""
    max_size = 0
    num_photo = 0
    for j in range(len(search_max)):
        file_size = search_max[j].get('width')*search_max[j].get('height')
        if file_size > max_size:
            max_size = file_size
            num_photo = j
    return search_max[num_photo].get('url'), search_max[num_photo].get('type')

def time_convert(date_unix):
    """Преобразование даты загрузки"""
    date_nf = datetime.datetime.fromtimestamp(date_unix)
    str_date = date_nf.strftime('%d-%m-%Y time %H-%M-%S')
    return str_date


class VK_user:
    def __init__(self, token_id, album_id, version='5.131'):
        """ Метод для получения начальных параметров запроса для VK"""
        self.token = token_id[0]
        self.id = token_id[1]
        self.version = version
        self.album = album_id
        self.startParams = {'access_token': self.token,
                            'v': self.version}
        self.jsonList, self.exp_dict = self._photo_info()

    def _get_photos(self):
        """Метод для получения словаря с параметрами фотографий"""
        url = 'http://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': self.album,
                  'photo_sizes': 1,
                  'extended': 1,
                  'rev': 1,
                  }
        photo_count = requests.get(url, params = {**self.startParams, **params}).json()['response']['count']
        params['count'] = photo_count
        photo_info = requests.get(url, params={**self.startParams, **params}).json()['response']
        result = {}
        photo_items = photo_info['items']
        l=len(photo_items)
        for i in range(photo_info['count']):
            likes = photo_items[i]['likes']['count']
            url_download, pict_size = find_max_size(photo_items[i]['sizes'])
            date_load = time_convert(photo_items[i]['date'])
            result_val = result.get(likes,[])
            result_val.append({'likes_count':likes,
                               'date_load':date_load,
                               'url_photo': url_download,
                               'size':pict_size
                               })
            result[likes] = result_val
        return result


    def _photo_info(self):
        """Метод для получения списка json для выгрузки и словаря ссылок на фото"""
        list_json = []
        links_photo = {}
        dict_photo = self._get_photos()

        for elem in dict_photo.keys():
            count = 0
            for val in dict_photo[elem]:
                if len(dict_photo[elem]) == 1:
                    f_name =f'{val["likes_count"]}.jpeg'
                else:
                    f_name = f'{val["likes_count"]}_{val["date_load"]}.jpeg'
                list_json.append({'file_name': f_name, 'size': val['size']})
                links_photo[f_name] = dict_photo[elem][count]['url_photo']
                count += 1
        return list_json, links_photo

class Yandex:
    def __init__(self, folder, token, num = 5):
        """ Метод для получения начальных параметров запроса для Я-диск"""
        self.token = token[0]
        self.add_files_num = num
        self.url ='https://cloud-api.yandex.net/v1/disk/resources'
        self.params = {'path':folder}
        self.headers = {'Authorization': self.token}
        self.folder = self._create_folder(folder)

    def _create_folder(self, name):
        """Метод для создания папки на Я-диск"""
        if requests.get(self.url, headers=self.headers, params=self.params).status_code != 200:
            requests.put(self.url,headers=self.headers, params=self.params)
            print(f'Папка {name} успешно создана!')
        else:
            print(f'Папка с именем {name} уже существует')
        return name

    def _link_load(self):
        """Метод для получения ссылки для загрузки фото на Я-диск"""
        resource = requests.get(self.url, headers=self.headers,
                                params=self.params).json()['_embedded']['items']
        list_load = []
        for el in resource:
            list_load.append(el['name'])
        return list_load

    def load_Y_disk(self, dict_f):
        """Метод загрузки фотографий на Я-диск"""
        files = self._link_load()
        copy_count = 0
        if len(dict_f) < self.add_files_num:
            l = len(dict_f)
        else:
            l = self.add_files_num
        for key, i in zip(dict_f.keys(), tqdm(range(l))):
            if copy_count < self.add_files_num:
                if key not in files:
                    params = {'path':f'{self.folder}/{key}',
                              'url':dict_f[key],
                              'overwrite':'false'}
                    requests.post(self.url+'/upload', headers=self.headers, params=params)
                    copy_count += 1
                else:
                    print(f'Файл {key} уже существует')
            else:
                break
        print(f'Запрос завершен, скопированно {copy_count} файлов!')


if __name__ == '__main__':
    # копирование фотографий из профиля VK
    my_VK_profile = VK_user(read_token('token.txt'), 'profile')
    with open('my_photos_VK_prof.json', 'w') as pfile:
        json.dump(my_VK_profile.jsonList, pfile)
    my_YA = Yandex('Photo VK_profile', read_token('token_Y.txt'),5)
    my_YA.load_Y_disk(my_VK_profile.exp_dict)

    # копирование фотографий со стены VK
    my_VK_wall = VK_user(read_token('token.txt'), 'wall')
    with open('my_photos_VK_wall.json', 'w') as wfile:
        json.dump(my_VK_wall.jsonList, wfile)
    my_YA = Yandex('Photo VK_wall', read_token('token_Y.txt'),15)
    my_YA.load_Y_disk(my_VK_wall.exp_dict)

import requests
from tqdm import tqdm



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

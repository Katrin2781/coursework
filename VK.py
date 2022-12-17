import requests
import datetime


def find_max_size(search_max):
    """Возвращает ссылку на фото максимального размера и размер фото"""
    max_size = 0
    num_photo = 0
    for j in range(len(search_max)):
        file_size = search_max[j].get('width') * search_max[j].get('height')
        if file_size > max_size:
            max_size = file_size
            num_photo = j
    return search_max[num_photo].get('url'), search_max[num_photo].get('type')


def time_convert(date_unix):
    """Преобразование даты загрузки"""
    date_nf = datetime.datetime.fromtimestamp(date_unix)
    str_date = date_nf.strftime('%d-%m-%Y time %H-%M-%S')
    return str_date


class VKUser:
    def __init__(self, token, id_user, album_id, version='5.131'):
        """ Метод для получения начальных параметров запроса для VK"""
        self.token = token
        self.user_vk = id_user
        self.version = version
        self.album = album_id
        self.startParams = {'access_token': self.token,
                            'v': self.version}
        self.id = self._get_id_user()
        self.jsonList, self.exp_dict = self._photo_info()


    def _get_id_user(self):
        """Метод для получения id пользователя"""
        url = 'http://api.vk.com/method/users.get'
        params = {'user_ids': self.user_vk}
        id_vk = requests.get(url, params={**self.startParams, **params}).json()['response'][0]['id']
        return id_vk

    def _get_photos(self):
        """Метод для получения словаря с параметрами фотографий"""
        url = 'http://api.vk.com/method/photos.get'
        params = {'owner_id': self.id,
                  'album_id': self.album,
                  'photo_sizes': 1,
                  'extended': 1,
                  'rev': 1,
                  }
        photo_count = requests.get(url, params={**self.startParams, **params}).json()['response']['count']
        params['count'] = photo_count
        photo_info = requests.get(url, params={**self.startParams, **params}).json()['response']
        result = {}
        photo_items = photo_info['items']
        for i in range(photo_info['count']):
            likes = photo_items[i]['likes']['count']
            url_download, pict_size = find_max_size(photo_items[i]['sizes'])
            date_load = time_convert(photo_items[i]['date'])
            result_val = result.get(likes, [])
            result_val.append({'likes_count': likes,
                               'date_load': date_load,
                               'url_photo': url_download,
                               'size': pict_size
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
                    f_name = f'{val["likes_count"]}.jpeg'
                else:
                    f_name = f'{val["likes_count"]}_{val["date_load"]}.jpeg'
                list_json.append({'file_name': f_name, 'size': val['size']})
                links_photo[f_name] = dict_photo[elem][count]['url_photo']
                count += 1
        return list_json, links_photo

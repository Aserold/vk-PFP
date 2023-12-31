import requests
import datetime
import json


class VK:
    def __init__(self, vk_token):
        self.vktoken = vk_token

    def get_photo_data(self, userid, amount_):
        url = 'https://api.vk.com/method/photos.get'
        params = {
            'owner_id': str(userid),
            'album_id': 'profile',
            'extended': '1',
            'access_token': vktoken,
            'v': '5.131'
        }
        res = requests.get(url, params=params).json()
        res = res['response']['items']
        # print(res)
        all_data_list = []
        like_check = []

        for data_item in res:
            temporary_dict = {}
            if data_item['likes']['count'] in like_check:
                temporary_dict[
                    'name'] = f"{datetime.datetime.fromtimestamp(data_item['date']).strftime('%Y-%m-%d')}.jpg"
            else:
                temporary_dict['name'] = str(f"{data_item['likes']['count']}.jpg")
            like_check.append(data_item['likes']['count'])
            for size in data_item['sizes']:
                if size['type'] == 'z':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'z'
                elif size['type'] == 'y':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'y'
                elif size['type'] == 'x':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'x'
                elif size['type'] == 'm':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 'm'
                elif size['type'] == 's':
                    temporary_dict['photo_url'] = size['url']
                    temporary_dict['size'] = 's'

            all_data_list.append(temporary_dict)
        global item_count
        item_count = sum('name' in item_ for item_ in all_data_list)

        if amount_ == 'all':
            return all_data_list
        elif amount_ >= item_count:
            return all_data_list
        else:
            item_count = amount_
            cut_data_list = all_data_list[:amount_]
            return cut_data_list


class Yandex:
    def __init__(self, ya_token):
        self.token = ya_token

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': 'OAuth {}'.format(self.token)
        }

    def create_folder(self, folder_name):
        url = 'https://cloud-api.yandex.net/v1/disk/resources'
        params = {'path': folder_name}
        response = requests.put(url, headers=self.get_headers(), params=params)

    def upload_photo(self, url, folder_name, file_name):
        response = requests.get(url)

        if response.status_code == 200:
            upload_url = "https://cloud-api.yandex.net/v1/disk/resources/upload"
            params = {
                'path': f'{folder_name}/{file_name}',
                'overwrite': 'true'
            }
            headers = {
                "Authorization": f"OAuth {self.token}",
            }

            upload_response = requests.get(upload_url, headers=headers, params=params)

            if upload_response.status_code == 200:
                upload_data = upload_response.json()
                href = upload_data["href"]

                upload_file_response = requests.put(href, data=response.content)

                if upload_file_response.status_code == 201:
                    pass
                else:
                    print("Error uploading a file to Yandex.Disk.| Ошибка загрузки файла на Яндекс.Диск.")
            else:
                print("Error receiving a link to upload a file to Yandex.Disk.| Ошибка получения ссылки для загрузки файла на Яндекс.Диск.")
        else:
            print("Photo upload error.|Ошибка загрузки фотографии.")

def ask_amount():
    init_amount = input('Enter the number of photos (5 by default) that you want to download(! - Download all)| Введите количество фотографий(по умолчанию 5), которые вы хотите скачать(! - Скачать все)>>>> ')
    if init_amount == '!':
        all_amount = 'all'
        return all_amount
    try:
        conv_amount = int(init_amount)
    except ValueError:
        conv_amount = 5
    return conv_amount


def progress_bar(progress, total, message):
    percent = 100 * (progress / float(total))
    bar = '█' * int(percent) + '-' * (100 - int(percent))
    print(f'\r|{bar}| {percent:.2f}% {message}', end='\r')

if __name__ == '__main__':
    token = input('Enter the Yandex token| Введите токен Яндекс>>>> ')

    vktoken = 'vk1.a.8UfSCy_kjCybRdZfQwHnhkRvL9UaC57JLbaL8orzf8RHHC8qIDQMruEmycCsXSzN4fAobaCrgjHe7AQ7ayWXawzpM9FKgfgrR-icMLQ-FJof6ucZsKkiSZh--JG9a1wpcV2WjCuD4tNw_GnrhxPyw5-FrDMrPbK5YfjZrHgb7LiDD7g5DLmQsc9e1dNj4QUpTNw8OuZsb_8QLQSG_p36ew'
    vk_test = VK(vktoken)
    ya_disk = Yandex(token)


    


    id_ = input('Enter vk id| Введите vk id>>>>')
    amount = ask_amount()
    data = vk_test.get_photo_data(id_, amount)
    # print(data)
    folder_name = input('Enter the folder name| Введите имя папки>>>> ')
    ya_disk.create_folder(folder_name)

    json_data = []

    for index, item in enumerate(data):
        temp_dict = {}
        name = item['name']
        photo_url = item['photo_url']
        ya_disk.upload_photo(photo_url, folder_name, name)
        temp_dict['file_name'] = item['name']
        temp_dict['size'] = item['size']
        json_data.append(temp_dict)
        progress_bar(index + 1, item_count, 'loading...')

    with open('info.json', 'w', encoding='utf8') as file:
        json.dump(json_data, file, indent=1)

    print(f'\nDone!')

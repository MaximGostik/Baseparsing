import requests
from bs4 import BeautifulSoup as BS
from abc import ABC, abstractmethod

class Baseparser(ABC):

    def __init__(self, url, header):
        self._start_url = url
        self.header = header
        self._result = []
        self.title = ''

    def __getitem__(self, item):
        if isinstance(item, (int, slice)):
            return self._result[item]
        raise TypeError("list indices must be integer or slices, not str")

    def __iter__(self):
        self._cursor = -1
        if not self._result:
            self.parse()
        return self

    def __next__(self):
        self._cursor += 1
        try:
            return self._result[self._cursor]
        except IndexError:
            del self._cursor
            raise StopIteration()

    def _get_text(self):
        res = requests.get(self._start_url,headers=self.header)
        res.raise_for_status()
        data = res.text
        return data


    @abstractmethod
    def parsing(self):
        ...

    def print_parsing(self):

        print(self.title)

        for car in self._result:
            print(f"Cсылка - {car['link']}, цена - {car['price']}, описание - {car['info']}")

class Kufar_parser(Baseparser):

    def parsing(self):

        data = self._get_text()
        soup = BS(data, "lxml")
        car_list = soup.find("div", class_="styles_cards__N3ZJH").find_all("section")
        self.title = "На Kufar.by найдено объявлений: " + str(len(car_list))

        for item in car_list:

            section_dict = {}

            section_dict["link"] = item.find("a")["href"]
            section_dict["price"] = item.find("div", class_="styles_bottom__price__rXpgP").find("span").text
            section_dict["info"] = item.find("p", class_="styles_params__haxwW styles_params--mobile__CPSIk").text.replace("\xa0","")
            section_dict["img"] = item.find("img")["data-src"]

            self._result.append(section_dict)
        return self.title, self._result


class AV_parser(Baseparser):

    def parsing(self):

        data = self._get_text()
        soup = BS(data, "lxml")
        car_list = soup.find_all("div", class_="listing-item")
        self.title = "На av.by найдено объявлений: " + str(len(car_list))

        for item in car_list:

            car_dict = {}

            car_dict["link"] = "https://cars.av.by" + item.find("a")["href"]
            car_dict["price"] = item.find("div", class_="listing-item__price").text.replace("\u2009", "").replace("\xa0","")
            car_dict["img"] = item.find("img")["data-src"]
            car_dict["info"] = item.find("div", class_="listing-item__params").text.replace("\u2009", "").replace("\xa0","")

            self._result.append(car_dict)
        return self.title, self._result

class ABW_parser(Baseparser):

    def parsing(self):

        data = self._get_text()
        soup = BS(data, "lxml")
        car_list = soup.find("ul", class_="list-body").find_all("li")
        car_list = car_list[:-1]
        self.title = "На ABW.by найдено объявлений: " + str(len(car_list))

        for item in car_list:

            try:
                car_dict = {}
                car_dict["img"] = item.find("img", class_="card-img__lazy")["src"]
                car_dict["link"] = "https://abw.by" + item.find("a")["href"]
                car_dict["price"] = item.find("p", class_="classified-card__byn").text
                car_dict["info"] = item.find("p", class_="classified-card__description").text

            except TypeError:
                None

            else:
                self._result.append(car_dict)

        return self.title, self._result

if __name__ == '__main__':

    print("Поиск объявлений Volvo s60 II поколения")

    URL_kufar = "https://auto.kufar.by/l/cars/volvo-s60-ii?cur=BYR"
    URL_av = "https://cars.av.by/filter?brands[0][brand]=1238&brands[0][model]=1256&brands[0][generation]=2748&transmission_type=2&engine_type[0]=5"
    URL_abw = "https://abw.by/cars/brand_volvo/model_s60/generation_ii"

    header = {
        "Accept":"*/*",
        "User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }
    Kufar_page = Kufar_parser(URL_kufar, header)
    Kufar_page.parsing()
    Kufar_page.print_parsing()
    AV_page = AV_parser(URL_av, header)
    AV_page.parsing()
    AV_page.print_parsing()
    ABW_page = ABW_parser(URL_abw, header)
    ABW_page.parsing()
    ABW_page.print_parsing()

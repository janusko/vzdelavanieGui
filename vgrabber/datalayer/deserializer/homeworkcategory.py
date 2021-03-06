from vgrabber.model import HomeWorkCategory, HomeWork


class HomeWorkCategoryDeserializer:
    def __init__(self, subject, category_element):
        self.__subject = subject
        self.__category_element = category_element

    def deserialize(self):
        home_work_category = HomeWorkCategory(
            self.__subject,
            self.__category_element.attrib['name']
        )
        
        if 'maxpoints' in self.__category_element.attrib:
            home_work_category.max_points = float(self.__category_element.attrib['maxpoints'])

        for homework_element in self.__category_element.xpath('./homework'):
            homework = HomeWork(
                self.__subject,
                int(homework_element.attrib['id']),
                homework_element.attrib['name'],
                int(homework_element.attrib['moodleid'])
            )
            
            if 'reqpoints' in homework_element.attrib:
                homework.required_points = float(homework_element.attrib['reqpoints'])

            home_work_category.add_home_work(homework)

        return home_work_category

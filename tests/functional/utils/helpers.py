from faker import Faker
from faker.providers import DynamicProvider

with open('utils/data.csv', 'r') as file:
    data = file.readlines()

film_names = [film.split(',')[1] for film in data]

genres = [
    "Western",
    "Adventure",
    "Drama",
    "Romance",
]

film_work_names = DynamicProvider(
    provider_name='film_name', elements=film_names
)
genre_names = DynamicProvider(provider_name='genre_name', elements=genres)

fake = Faker(['en_US'])
Faker.seed(5)
fake.add_provider(film_work_names)
fake.add_provider(genre_names)

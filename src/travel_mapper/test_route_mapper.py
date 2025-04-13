from src.travel_mapper.travel_mapper_base import TravelMapperBase


def test(query=None):
    if not query:
        query = """
        I want to do 2 week trip from Berkeley CA to New York City.
        I want to visit national parks and cities with good food.
        I want use a rental car and drive for no more than 5 hours on any given day.
        """

    mapper = TravelMapperBase()

    mapper.parse(query, make_map=True)


if __name__ == "__main__":
    test()

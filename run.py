from geo_converter import GeoConverter

def run() -> None:
    GeoConverter.convert_geo_reverse_and_save("_mock_202107_tweets")

if __name__ == '__main__':
    run()

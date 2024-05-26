import json


class DataStorage:
    @staticmethod
    def save_to_json(data, filename):
        try:
            with open(filename, 'w') as json_file:
                json.dump(data, json_file, indent=4)
        except IOError as e:
            print(f"Error saving data to JSON file: {e}")

    @staticmethod
    def load_from_json(filename):
        try:
            with open(filename, 'r') as json_file:
                return json.load(json_file)
        except (IOError, json.JSONDecodeError) as e:
            print(f"Error loading data from JSON file: {e}")
            return []

    async def insert_data_to_json(self, data, filename, cache):
        loaded_data = self.load_from_json("./data/database/scraped_data.json")

        merged_dict = {}
        updated_cache_objects = {}

        # Process existing JSON list
        for obj in loaded_data:
            key = obj["name"]
            merged_dict[key] = obj

        # Process new JSON list
        for obj in data:
            key = obj["name"]
            if key not in merged_dict or merged_dict[key]["price"] != obj["price"]:
                updated_cache_objects[key] = obj
            merged_dict[key] = obj

        result = list(merged_dict.values())
        self.save_to_json(result, filename)

        for key, value in updated_cache_objects.items():
            print(f"{key}: {value}")
            cache.set(key, json.dumps(value))

        return len(result) - len(loaded_data)

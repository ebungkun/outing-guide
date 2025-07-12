import pandas as pd
import json
from collections import defaultdict

def convert_csv_to_final_json_corrected(csv_path, output_path):
    """
    Converts a single comprehensive CSV file into a structured, grouped JSON format.
    This corrected version properly handles choices with the same name but different
    time contexts (day/night) by creating a context-aware lookup table.

    Args:
        csv_path (str): Path to the merged input CSV file.
        output_path (str): Path to save the final structured JSON file.
    """
    # --- 1. Hardcode the Choice-to-ID Mapping Tables with Location Data ---
    # This table is the single source of truth for choice IDs and their details.
    MAPPING_TABLES = {
        "choices": {
            # Common Choices (ID 100-199)
            "101": {"choice": "게임을 한다", "location": "어디서나"},
            "102": {"choice": "대련을 한다", "location": "어디서나"},
            "103": {"choice": "독서를 한다", "location": "어디서나"},
            "104": {"choice": "돌아다닌다", "location": "어디서나"},
            "105": {"choice": "도시락을 먹는다", "location": "어디서나"},
            "106": {"choice": "아무것도 하지 않는다", "location": "어디서나"},
            "107": {"choice": "잡담을 나눈다", "location": "어디서나"},
            "108": {"choice": "티타임을 가진다", "location": "어디서나"},
            "109": {"choice": "풍경을 바라본다", "location": "어디서나"},
            "110": {"choice": "휴식을 취한다", "location": "어디서나"},
            # Day Rare Choices (ID 200-299)
            "201": {"choice": "넓은 방주", "location": "낮의 방주"},
            "202": {"choice": "방주의 고요함", "location": "낮의 방주"},
            "203": {"choice": "분홍빛 벚꽃동산", "location": "낮의 벚꽃동산"},
            "204": {"choice": "팔랑이는 꽃잎", "location": "낮의 벚꽃동산"},
            "205": {"choice": "낮의 해변가", "location": "낮의 해변가"},
            "206": {"choice": "눈부신 해변", "location": "낮의 해변가"},
            "207": {"choice": "성벽 산책로", "location": "낮의 성벽산책로"},
            "208": {"choice": "성벽을 따라 걷는 길", "location": "낮의 성벽산책로"},
            "209": {"choice": "나뭇잎 사이의 햇살", "location": "낮의 종달새 숲"},
            "210": {"choice": "종달새 숲", "location": "낮의 종달새 숲"},
            # Night Rare Choices (ID 300-399)
            "301": {"choice": "밤의 해변가", "location": "밤의 해변가"},
            "302": {"choice": "차분한 파도소리", "location": "밤의 해변가"},
            "303": {"choice": "달빛 호숫가", "location": "밤의 달빛호숫가"},
            "304": {"choice": "반짝이는 호수", "location": "밤의 달빛호숫가"},
            "305": {"choice": "성벽 산책로", "location": "밤의 성벽산책로"},
            "306": {"choice": "성벽을 따라 걷는 길", "location": "밤의 성벽산책로"},
            "307": {"choice": "새가 지저귀는 밤", "location": "밤의 종달새 숲"},
            "308": {"choice": "종달새 숲", "location": "밤의 종달새 숲"},
            "309": {"choice": "별이 가득한 하늘", "location": "밤의 은하수 언덕"},
            "310": {"choice": "아름다운 하늘", "location": "밤의 은하수 언덕"}
        }
    }
    
    # --- 2. Create a Context-Aware Lookup Table ---
    # This nested dictionary stores IDs based on both choice text and time context.
    # Structure: { "choice_text": { "context": id } }
    # Example: { "성벽 산책로": { "day": 207, "night": 305 } }
    context_aware_map = defaultdict(dict)
    for id_str, details in MAPPING_TABLES["choices"].items():
        choice_text = details["choice"]
        choice_id = int(id_str)
        
        if 100 <= choice_id < 200:
            context = "common"
        elif 200 <= choice_id < 300:
            context = "day"
        elif 300 <= choice_id < 400:
            context = "night"
        else:
            continue # Skip if ID is out of expected ranges

        context_aware_map[choice_text][context] = choice_id

    try:
        # --- 3. Read the CSV file using pandas ---
        df = pd.read_csv(csv_path)

        # --- 4. Process the DataFrame to build the desired structure ---
        grouped_preferences = defaultdict(list)
        
        # Define column mappings for clarity
        preference_columns = {
            'common_liked': ('common', ['커먼 선호 1', '커먼 선호 2']),
            'common_disliked': ('common', ['커먼 비선호']),
            'rare_day_liked': ('day', ['낮 레어 선호 1', '낮 레어 선호 2']),
            'rare_day_disliked': ('day', ['낮 레어 비선호']),
            'rare_night_liked': ('night', ['밤 레어 선호 1', '밤 레어 선호 2']),
            'rare_night_disliked': ('night', ['밤 레어 비선호'])
        }

        # Helper function to get ID from text using the context-aware map
        def get_id_with_context(choice_text, context):
            if pd.notna(choice_text):
                cleaned_text = str(choice_text).strip()
                if cleaned_text in context_aware_map and context in context_aware_map[cleaned_text]:
                    return context_aware_map[cleaned_text][context]
                else:
                    # Print a warning if a choice text is not found for the given context
                    print(f"Warning: Choice '{cleaned_text}' for context '{context}' not in mapping table. Skipping.")
            return None

        for _, row in df.iterrows():
            character_name = row['정령']
            character_type = row['타입']

            preferences = {
                "common": {"liked": [], "disliked": []},
                "rare_day": {"liked": [], "disliked": []},
                "rare_night": {"liked": [], "disliked": []}
            }

            # Populate preferences using the column mappings and the new context-aware getter
            for key, (context, columns) in preference_columns.items():
                category, pref_type = key.split('_', 1) # e.g., 'common', 'liked'
                if len(pref_type.split('_')) > 1: # rare_day_liked -> 'rare_day', 'liked'
                    category = f"{category}_{pref_type.split('_')[0]}"
                    pref_type = pref_type.split('_')[1]
                
                id_list = [id_val for col in columns if (id_val := get_id_with_context(row[col], context)) is not None]
                preferences[category][pref_type].extend(id_list)
            
            character_data = {
                "character_name": character_name,
                "preferences": preferences
            }
            
            grouped_preferences[character_type].append(character_data)

        # --- 5. Assemble the final JSON object ---
        final_json = {
            "mapping_tables": MAPPING_TABLES,
            "character_preferences": dict(grouped_preferences)
        }

        # --- 6. Save the final object to a JSON file ---
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(final_json, f, ensure_ascii=False, indent=2)
        
        print(f"Success: Data has been converted and saved to '{output_path}'.")

    except FileNotFoundError:
        print(f"Error: The file was not found at the path '{csv_path}'.")
    except KeyError as e:
        print(f"Error: A required column was not found in the CSV file. Column: {e}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")


if __name__ == '__main__':
    # Define the input CSV file path
    # You should have 'merged_data.csv' in the same directory.
    input_csv_file = 'merged_data.csv'
    
    # Define the output JSON file path
    output_json_file = 'preferences.json'
    
    # To run this script, you need to install pandas:
    # pip install pandas
    
    # Execute the conversion function
    convert_csv_to_final_json_corrected(input_csv_file, output_json_file)

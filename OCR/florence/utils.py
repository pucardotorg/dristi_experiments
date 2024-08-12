
UID_KEY = "UID"
MESSAGE_KEY = "Message"
CONTAINS_KEYWORDS_KEY = "Contains Keywords"
EXTRACTED_DATA_KEY = "Extracted Data"


def add_words_counts(words_counts,response_words_counts):

    for key,value in response_words_counts:
        words_counts[key] += value
    return words_counts

def get_final_response(responses):
    final_response = {}
    contains_keywords = {}
    extracted_data = {}
    
    message_count = 0
    for response in responses:
        
        if MESSAGE_KEY in response:
            message_count += 1
        if CONTAINS_KEYWORDS_KEY in response:
            add_words_counts(contains_keywords, response[CONTAINS_KEYWORDS_KEY])
        if EXTRACTED_DATA_KEY in response:
            extracted_data.update(response[EXTRACTED_DATA_KEY])

    final_response[UID_KEY] = responses[0][UID_KEY]
    if message_count == len(responses):
        final_response[MESSAGE_KEY] = responses[0][MESSAGE_KEY]
        return final_response
    
    final_response[CONTAINS_KEYWORDS_KEY] = contains_keywords

    if extracted_data:
        final_response[EXTRACTED_DATA_KEY] = extracted_data

    return final_response

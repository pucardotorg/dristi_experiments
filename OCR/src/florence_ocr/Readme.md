'''
request 
curl -X POST http://localhost:1234/ \
     -F "file=@1c_cheque_return_memo_1.jpg" \
     -F 'word_check_list=["return memo", "memo"]' \
     -F "distance_cutoff=1" \
     -F "doc_type=cheque_return_memo" \
     -F "extract_data=true"

or 

curl -X POST http://localhost:1234/ \
     -F "file=@1c_cheque_return_memo_1.jpg" \
     -F 'word_check_list=["return memo", "memo"]' \
     -F "distance_cutoff=1"

'''
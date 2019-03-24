import re
from beautifultable import BeautifulTable

if __name__ == '__main__':
    fileREL = open("./time/TIME.REL","r").read()
    fileOutput = open("./output.txt","r").read()
    query_num_and_rel = {}
    num_and_rel = re.split('\n', fileREL)
    num_and_rel = [ x for x in num_and_rel if len(x) != 0]
    for x in num_and_rel:
        query_number = x[:2].replace(' ','')
        query_num_and_rel[query_number] =re.findall("\d+",x[2:])
    queries_output = re.split("@", fileOutput)
    del queries_output[0]
    
    output_query_num_and_rel = {}
    for x in queries_output:
        query = re.findall("Query:\d+", x)
        query_number = re.findall("\d+", query[0])
        docId = re.findall("docId: \d+", x)
        docId = [ str(int(x.replace('docId: ', ''))+1) for x in docId]
        output_query_num_and_rel[query_number[0]] = docId

    table = BeautifulTable()
    table.column_headers = ["Query", "Capture", "Missing"]
    for key, value in output_query_num_and_rel.items():
        capture = []
        missing = []
        for x in query_num_and_rel[key]:
            if x in value:
                capture.append(x)
            else:
                missing.append(x)        
        table.append_row([key, capture, missing])
    print(table)
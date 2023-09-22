'''import requests
import json


r = requests.post(
    'https://api.semanticscholar.org/graph/v1/paper/batch',
    params={'fields': f"title,abstract,year,authors,"
                      f"fieldsOfStudy,"
                      f"citationCount,citations.citationCount,citations.title,citations.abstract,citations.year,"
                      f"citations.authors,citations.fieldsOfStudy,"
                      f"references.citationCount,references.title,references.abstract,references.year,"
                      f"references.authors,references.fieldsOfStudy"},
    json={"ids": ["2e9d221c206e9503ceb452302d68d10e293f2a10"],
          "citations.limit": 1}
)
print(json.dumps(r.json(), indent=1))

# 2e9d221c206e9503ceb452302d68d10e293f2a10
r = requests.post(
        'https://api.semanticscholar.org/graph/v1/paper/batch',
        params={
            'fields': f"title,abstract,year,authors,"
                      f"fieldsOfStudy,"
                      f"citationCount,citations.citationCount,citations.title,citations.abstract,citations.year,"
                      f"citations.authors,citations.fieldsOfStudy,"
                      f"references.citationCount,references.title,references.abstract,references.year,"
                      f"references.authors,references.fieldsOfStudy"},
        json={"ids": related_to_root_ids[:1]}
    ).json()
    print(related_to_root_ids[0])
    print(r)
    for i in range(len(r)):
        print(r[i])
        references = sorted(r[i]['references'], key=lambda x: x['citationCount'] if x['citationCount'] else 0,
                        reverse=True)[:20]
        citations = sorted(r[i]['citations'], key=lambda x: x['citationCount'] if x['citationCount'] else 0, reverse=True)[:20]
        del r[i]['references']
        del r[i]['citations']
        r[i] = (r[i], references + citations)
    newrels = r'''

print(list(range(2, 5)))
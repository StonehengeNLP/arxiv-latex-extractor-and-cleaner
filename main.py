import re
import glob
import json
import tarfile

from extractor import LatexReader, LatexExtractor

latex_reader = LatexReader()
latex_extractor = LatexExtractor()

data = []
mapping = []

for fname in glob.glob('papers/*'):

    id = fname[fname.find('\\') + 1:]
    
    with tarfile.open(fname, "r:tar") as f:
        f.extractall(f'extracted_papers/{id}')

    latex_content = latex_reader(f'extracted_papers/{id}')
    paper = latex_extractor.extract(latex_content)
    
    data += [paper['abstract']]
    mapping += [(id, paper['title'], 'abstract')]
    for section in paper['sections']:
        data += paper['sections'][section]
        mapping += [(id, paper['title'], section)] * len(paper['sections'][section])
    
print(len(data))
print(len(mapping))

for i in range(len(data))[::-1]:
    if len(data[i]) < 100:
        data.pop(i)
        mapping.pop(i)

print(len(data))
print(len(mapping))

with open('data.json', 'w') as f:
    json.dump(data, f)
    
with open('mapping.json', 'w') as f:
    json.dump(mapping, f)
    
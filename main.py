import re
import glob
import tarfile

from extractor import LatexReader, LatexExtractor

latex_reader = LatexReader()
latex_extractor = LatexExtractor()

for fname in glob.glob('papers/*'):
    print(fname)
    id = fname[fname.find('\\') + 1:]
    
    with tarfile.open(fname, "r:tar") as f:
        f.extractall(f'extracted_papers/{id}')

    latex_content = latex_reader(f'extracted_papers/{id}')
    data = latex_extractor.extract(latex_content)
    print(data)
    # for section in data['sections']:
    #     print('=' * 50, section, '=' * 50)
    #     text = data['sections'][section]
    #     print(text)
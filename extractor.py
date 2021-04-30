import re
import glob

class LatexReader:
    
    def __call__(self, paper_dir):
        all_latex_files = glob.glob(f'{paper_dir}/*.tex')
        for fname in all_latex_files:
            if self.is_main_tex_file(fname):
                main_filename = re.search(r'.*\\(.*)\.tex', fname).group(1)
                break
        data = self.read_latex(paper_dir, main_filename)
        data = self.replace_newcommand(data)
        return data
    
    def is_main_tex_file(self, fpath):
        with open(fpath) as f:
            data = ''.join(f.readlines())
        if '\\end{document}' in data:
            return True
        return False
    
    def replace_newcommand(self, data):
        newcommands = re.findall(r'^\\newcommand(\{([^\}]*)\}|\\[^\{]*)\s*(\[(.*)\])?\s*\{(.*)\}\s*$', data, flags=re.M)

        for _ in range(3):
            for aa, a, _, b, c in newcommands:
                if a == '':
                    a = aa
                if b == '':
                    c = c.replace('\\', '\\\\')
                    data = re.sub(rf'({re.escape(a)})\b', c, data)
                else:
                    c = c.replace('\\', '\\\\')
                    c = c.replace('#', '\\')
                    data = re.sub(rf'({re.escape(a)}{{([^}}]*)}})\b', rf'{c}', data)        
        return data
        
    def read_latex(self, paper_dir, filename):
        data = ''
        if not filename.endswith('.tex'):
            filename = f'{filename}.tex'
        with open(f'{paper_dir}/{filename}') as f:
            data = ''.join(f.readlines())
            
        all_files = re.findall(r'\\input\{(.+)\}', data)
        
        for fname in all_files:
            section_data = self.read_latex(paper_dir, fname)
            data = data.replace(f'\\input{{{fname}}}', section_data)                
        return data

class LatexExtractor:
    
    def extract(self, content):
        return {
            'title': self.extract_title(content),
            'abstract': self.extract_abstract(content),
            'sections': self.extract_all_sections(content),
        }
    
    def extract_title(self, content):
        title = re.search(r'\\title\{(.*)\}', content).group(1)
        title = self.clean_latex(title)
        title = re.sub(r'\s+', ' ', title)
        return title
    
    def extract_abstract(self, content):
        abstract = re.search(r'\\begin\{abstract\}([\w\W]*)\\end\{abstract\}', content).group(1)
        abstract = self.clean_latex(abstract)
        abstract = re.sub(r'\s+', ' ', abstract)
        return abstract
    
    def extract_all_sections(self, content):
        content = self.exclude_appendix(content)
        sections = re.findall(r'\\section\{([^\}]*\}*)\}', content)
        data = {}
        for section in sections:
            section_content = self.extract_section(content, section)
            section = self.clean_latex(section)
            data[section] = section_content
        return data
    
    def extract_section(self, content, section_name):
        section = re.search(rf'\\section\*?{{{re.escape(section_name)}}}([\w\W]*?)(\\section|$)', content).group(1)
        section = self.clean_latex(section)
        section = re.sub(r'\s*\n\n\s*', '\n\n', section)
        section = section.split('\n\n')
        section = [re.sub(r'\s+', ' ', paragraph) for paragraph in section]
        return section
    
    def exclude_appendix(self, content):
        content = re.sub(r'\\appendix\s[\w\W]*$', '', content)
        return content
    
    @staticmethod
    def clean_latex(text):
        text = re.sub(r'\\begin\{table\*?\}[\w\W]*?\\end\{table\*?\}', '', text)
        text = re.sub(r'\\begin\{figure\*?\}[\w\W]*?\\end\{figure\*?\}', '', text)
        text = re.sub(r'\\begin\{align\*?\}[\w\W]*?\\end\{align\*?\}', '', text)
        text = re.sub(r'\\begin\{equation\*?\}[\w\W]*?\\end\{equation\*?\}', '', text)
        
        text = re.sub(r'^\s*%[^\n]*\n', '', text, flags=re.M)
        text = re.sub(r'\$([^\$]{1,30})\$', r'\1', text)
        text = re.sub(r'\$[^\$]*\$', '', text)
        text = re.sub(r'\~?\\(cite[tp]?|newcite)(\[[^\]]*\])*\{[^\}]*\}', '', text)
        text = re.sub(r'\~?\\ref\{[^\}]*\}', '', text)
        text = re.sub(r'\{\\(em|it|bf) ([^\}]*)\}', r'\2', text)
        text = re.sub(r'\{\\(tt) ([^\}]*)\}', r'\2', text)
        text = re.sub(r'\{\\(scriptsize) ([^\}]*)\}', r'\2', text)
        text = re.sub(r'\{\\(small|large) ([^\}]*)\}', r'\2', text)
        text = re.sub(r'(\`\`|\'\')', '\"', text)
        text = re.sub(r'\`', '\'', text)
        text = re.sub(r'\\(textbf|textsc|textit|texttt)\{([^\}]*)\}', r'\2', text)
        text = re.sub(r'\\(emph|eats)\{([^\}]*)\}', r'\2', text)
        text = re.sub(r'\\(textsubscript)\{([^\}]*)\}', r'\2', text)
        text = re.sub(r'\\url\{([^\}]*)\}', r'\1', text)
        text = re.sub(r'\\paragraph\{([^\}]*)\}', r'\1', text)
        text = re.sub(r'\~?\\footnote\{[^\}]*\}', '', text)
        text = re.sub(r'\\footnotetext(\[\d?\])?\{[^\}]*\}', '', text)
        text = re.sub(r'\\(subsection|label)\{[^\}]+\}', '', text)
        text = re.sub(r'\\(bibliographystyle|bibliography|pagenumbering)\{[^\}]+\}', '', text)
        text = re.sub(r'\\(vspace|hspace)\{[^\}]+\}', '', text)
        text = re.sub(r'\\(xspace)', '', text)
        text = re.sub(r'\\item', '\n', text)
        text = re.sub(r'\\noindenttextbf', '', text)
        text = re.sub(r'\\noindent', '', text)
        text = re.sub(r'\\clearpage', '', text)
        text = re.sub(r'\\renewcommand\*(\{[^\}]+\})+', '', text)
        text = re.sub(r'\\(texttildelow|textasciitilde)', '~', text)
        text = re.sub(r'_\{([^\}]*)\}', r'_\1', text)
        
        text = re.sub(r'\\[a-z]+\{([^\}]+)\}', r'\1', text)
        text = re.sub(r'^\s*\\\w+(\{[^\}]*\})+(\[[^\]]*\])?\s*$', '', text, flags=re.M)
        text = re.sub(r'\{\}', '', text)
        text = re.sub(r'\\([%#&~])', r'\1', text)
        text = re.sub('\\\\\-', '-', text)
        text = re.sub('\\\\', '\n', text)
        
        return text.strip()
    
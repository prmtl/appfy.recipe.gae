import os


BASE = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
GAE = os.path.join(BASE, 'appfy', 'recipe', 'gae')
README = os.path.join(BASE, 'README.rst')
FILES = [
    os.path.join(BASE, 'setup.py'),
    os.path.join(GAE, 'app_lib.py'),
    os.path.join(GAE, 'sdk.py'),
    os.path.join(GAE, 'tools.py'),
]


def get_doc(filename):
    f = open(filename, 'r')
    content = f.read()
    f.close()

    start = content.find('"""')
    end = content.find('"""', start + 1)
    return content[start + 3:end]


def create_readme():
    docs = [get_doc(filename) for filename in FILES]
    readme = '\n\n\n'.join(doc.strip() for doc in docs if doc.strip())
    f = open(README, 'w')
    f.write(readme)
    f.close()


if __name__ == '__main__':
    create_readme()

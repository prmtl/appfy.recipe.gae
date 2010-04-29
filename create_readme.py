import os

join   = os.path.join
BASE   = os.path.abspath(os.path.realpath(os.path.dirname(__file__)))
GAE    = join(BASE, 'appfy', 'recipe', 'gae')
README = join(BASE, 'README.txt')
FILES  = [
    join(BASE, 'setup.py'),
    join(GAE, 'app_lib.py'),
    join(GAE, 'sdk.py'),
    join(GAE, 'tools.py'),
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

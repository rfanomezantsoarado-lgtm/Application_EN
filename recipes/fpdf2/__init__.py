# recipes/fpdf2/__init__.py
from pythonforandroid.recipe import PythonRecipe

class FPDF2Recipe(PythonRecipe):
    version = '2.7.4'
    url = 'https://github.com/py-pdf/fpdf2/archive/refs/tags/{version}.tar.gz'
    depends = ['python3']
    
recipe = FPDF2Recipe()

from setuptools import setup, find_packages

setup(
    name="stylematcher",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'torch',
        'Pillow',
        'transformers',
        'sentence-transformers',
        'pandas',
        'tqdm',
        'flask',
        'streamlit'
    ],
) 
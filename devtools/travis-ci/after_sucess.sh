pip install coveralls
coveralls

echo $TRAVIS_PULL_REQUEST $TRAVIS_BRANCH

if [[ "$TRAVIS_PULL_REQUEST" != "false" ]]; then
    echo "This is a pull request. No deployment will be done."; exit 0
fi


if [[ "$TRAVIS_BRANCH" != "master" ]]; then
    echo "No deployment on BRANCH='$TRAVIS_BRANCH'"; exit 0
fi


if [[ "2.7 3.3 3.4" =~ "$python" ]]; then
    echo $BINSTAR_TOKEN
    echo $BINSTAR_TOKEN > token.txt
    cat token.txt
    binstar -t "$BINSTAR_TOKEN"  upload --force --user iModels --package mbuild $HOME/miniconda/conda-bld/linux-64/mbuild-*
fi

if [[ "$python" != "2.7" ]]; then
    echo "No deploy on PYTHON_VERSION=${python}"; exit 0
fi


# Create the docs and push them to github pages
# ---------------------------------------------
conda install --yes sphinx numpydoc

python setup.py develop

cd docs
make html

source update_gh_pages.sh
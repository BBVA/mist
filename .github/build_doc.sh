#! /bin/bash

GENERATION_ROOT=generated_docs/content
ASSETS_DIR=$GENERATION_ROOT/assets/images
NAV_FILE="$GENERATION_ROOT/_data/navigation.yml"
DOCS_FILE="$GENERATION_ROOT/_includes/docs_incl.md"
LANG_FUNCS_FILE="$GENERATION_ROOT/_includes/funcs_incl.md"
LANG_CATALOG_FILE="$GENERATION_ROOT/_includes/catal_incl.md"
LANG_SYNTAX_FILE="$GENERATION_ROOT/_includes/syntax_incl.md"

# Create the directory tree in which to generate the documentation files
mkdir -vp $GENERATION_ROOT/{_data,_includes,assets/images} 2> /dev/null

# copy assets
cp -vr images/*.png $ASSETS_DIR

# Create main index yaml
echo "Generating main index: $NAV_FILE"
cat <<EOF > $NAV_FILE
# main links
main:
  - title: "Home"
    url: /
  - title: "Quick-Start"
    url: documentation.html#QuickStart
  - title: Documentation
    url: documentation.html
  - title: "Mist Language"
    url: syntax.html

# sidebar links
sidebar:
  - title: Home
    url: /
  - title: Documentation
    url: documentation.html
    children:
      - title: Introduction
        url: documentation.html#Introduction
      - title: Quick Start
        url: documentation.html#QuickStart
  - title: Mist Language
    children:
      - title: Syntax
        url: syntax.html
      - title: Functions
        url: functions.html
      - title: Catalog
        url: catalog.html
EOF

echo -e "Generating doc file: \n$DOCS_FILE"
echo -e "<a id=\"Introduction\"></a>\n\n# Mist Documentation\n\n<a id=\"Documentation\"></a>" > $DOCS_FILE
csplit --prefix=docs --suppress-matched  README.md '/<!--split-->/' '{*}'
grep -v "MIST LOGO" docs00 >> $DOCS_FILE
echo -e "\n\n<a id=\"QuickStart\"></a>" >> $DOCS_FILE
sed -e 's#https://raw.githubusercontent.com/BBVA/mist/master#content/assets#' docs01 >> $DOCS_FILE
echo -e "\n\n" >> $DOCS_FILE
cat docs02 >> $DOCS_FILE

echo "$LANG_SYNTAX_FILE"
cp -v mist/lang/SYNTAX.md $LANG_SYNTAX_FILE

echo "$LANG_FUNCS_FILE"
echo -e "# Mist builtin functions\n\n" > $LANG_FUNCS_FILE
python3 get_function_docs.py | tail -n +2 >> $LANG_FUNCS_FILE

echo "$LANG_CATALOG_FILE"
echo "# Mist Catalog" > $LANG_CATALOG_FILE
for item in mist/catalog/*.md
do
  command=$(basename $item .md)
  echo -e "\n\n<a id=\"$item\"></a>" >> $LANG_CATALOG_FILE
  cat $item >> $LANG_CATALOG_FILE
done

rm docs??

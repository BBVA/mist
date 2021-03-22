#! /bin/bash

# Create the directory tree in which to generate the documentation files
mkdir -vp generated_docs/content/{_data,_includes,assets/images} 2> /dev/null

# copy assets
cp -vr images/*.png generated_docs/content/assets/images


echo -e "Generating doc files: \ngenerated_docs/content/_includes/index_incl.md"
csplit --prefix=docs --suppress-matched  README.md '/<!--split-->/' '{*}'
sed -e 's#https://raw.githubusercontent.com/BBVA/mist/master#content/assets#' docs00 docs02 > generated_docs/content/_includes/index_incl.md

echo "generated_docs/content/_includes/intro_incl.md"
sed -e 's/<!---/---/' -e 's/--->/---/' mist/lang/README.md > generated_docs/content/_includes/intro_incl.md

echo "generated_docs/content/_includes/builtin_incl.md"
copy -v mist/lang/BUILTIN.md generated_docs/content/_includes/builtin_incl.md

echo "generated_docs/content/_includes/quick_incl.md"
sed -e 's#https://raw.githubusercontent.com/BBVA/mist/master#content/assets#' docs01 > generated_docs/content/_includes/quick_incl.md

rm docs??

echo "Generating main index: generated_docs/content/_data/navigation.yml"
# Create main index yaml
cat <<EOF > generated_docs/content/_data/navigation.yml
# main links
main:
  - title: "Home"
    url: /
  - title: "Introduction"
    url: intro.html
  - title: "Quick-Start"
    url: quick.html
  - title: "Builtin commands"
    url: builtin.html

sidebar:
  - title: Home
    url: /
  - title: Introduction
    url: intro.html
  - title: Quick Start (ping)
    url: quick.html
  - title: Builtin commands
    children:
      - title: Data
        url: builtin.html#data
      - title: Put
        url: builtin.html#put
      - title: Print
        url: builtin.html#print
      - title: Check
        url: builtin.html#check
      - title: Iterate
        url: builtin.html#iterate
      - title: Exec
        url: builtin.html#exec
      - title: SearchInText
        url: builtin.html#searchInText
      - title: SearchInXML
        url: builtin.html#searchInXML
      - title: SearchInJSON
        url: builtin.html#searchInJSON
      - title: CSVDump
        url: builtin.html#csvDump
      - title: CSVput
        url: builtin.html#csvPut
  - title: Command catalogs
    children:
      - title: Core catalog
        url: https://cr0hn.github.io/mist-catalog/
      - title: AWS catalog
        url: https://hhurtado.github.io/mist-aws-catalog/
  - title: Playbook catalogs
    url: https://cr0hn.github.io/mist-playbooks/EOF
EOF

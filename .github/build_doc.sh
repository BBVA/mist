#! /bin/bash

# Create the directory tree in which to generate the documentation files
mkdir -vp generated_docs/content/{_data,_includes,assets} 2> /dev/null

# copy assets
cp -vr docs/source/_static/* generated_docs/content/assets/

cp -v README.md generated_docs/content/_includes/index_incl.md

# Split tmp_lang into intro, quick and builtin
#######csplit --prefix=docs --suppress-matched  mist/lang/README.md '/<!--split-->/' '{*}'

echo -e "Generating lang doc files: \n generated_docs/content/_includes/intro_incl.md\n generated_docs/content/_includes/quick_incl.md\n generated_docs/content/_includes/builtin_incl.md"
sed -e 's/<!---/---/' -e 's/--->/---/' mist/lang/README.md > generated_docs/content/_includes/intro_incl.md
sed -e 's/<!---/---/' -e 's/--->/---/' mist/lang/QUICK.md > generated_docs/content/_includes/quick_incl.md
sed -e 's/<!---/---/' -e 's/--->/---/' mist/lang/BUILTIN.md > generated_docs/content/_includes/builtin_incl.md

echo "Generating main index: generated_docs/content/_data/main_menu.yml"
# Create main index yaml
cat <<EOF > generated_docs/content/_data/main_menu.yml
- name: Home
  description: MIST home page
  link: index.html
- name: Introduction
  description: A brief introduction to MIST
  link: intro.html
- name: Quick Start (ping)
  description: Quick overview on how MIST works
  link: quick.html
- name: Builtin commands
  sub:
    - name: Data
      link: builtin.html#data
    - name: Put
      link: builtin.html#put
    - name: Print
      link: builtin.html#print
    - name: Check
      link: builtin.html#check
    - name: Iterate
      link: builtin.html#iterate
    - name: Exec
      link: builtin.html#exec
    - name: SearchInText
      link: builtin.html#searchInText
    - name: SearchInXML
      link: builtin.html#searchInXML
    - name: SearchInJSON
      link: builtin.html#searchInJSON
    - name: CSVDump
      link: builtin.html#csvDump
    - name: CSVput
      link: builtin.html#csvPut
- name: Command catalogs
  sub:
    - name: Core catalog
      link: https://cr0hn.github.io/mist-catalog/
    - name: AWS catalog
      link: https://hhurtado.github.io/mist-aws-catalog/
- name: Playbook catalogs
  sub:
    - name: MIST playbooks
      link: https://cr0hn.github.io/mist-playbooks/
EOF

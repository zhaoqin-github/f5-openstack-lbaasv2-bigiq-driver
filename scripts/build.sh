#!/bin/bash -e

usage() {
  return 0
}

build() {
  m2r README.md
  python setup.py bdist_rpm --release ${BUILD_NUMBER}
}

clean() {
  rm -rf \
    README.rst build dist \
    f5_lbaasv2_bigiq_dirver/__init__.pyc \
    f5_openstack_lbaasv2_bigiq_driver.egg-info
}

BUILD_DIR="."
BUILD_NUMBER="1"

while getopts d:n:h o ; do
  case "$o" in
    d)   BUILD_DIR="$OPTARG";;
    n)   BUILD_NUMBER="$OPTARG";;
    h)   usage
         exit 0;;
    [?]) usage
         exit 1;;
  esac
done
shift $((OPTIND-1))

cd ${BUILD_DIR}

if [[ $1 == "clean" ]] ; then
  clean
else
  build
fi

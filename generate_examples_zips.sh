#!/usr/bin/env bash
set -e
set -x

for path in "examples/google_cloud/bucket_cloud_function"; do
  modeulname=`basename "$path"`
  tmp_zip_location="../${modeulname}_example.zip"
  git archive -o "${tmp_zip_location}" "HEAD:${path}"
  mv "${tmp_zip_location}" "${path}"
done

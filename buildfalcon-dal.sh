#!/bin/bash

export SCRIPT_DIR=$HOME/bin

export MAVEN_OPTS="-Xms3g -Xmx3g -XX:MaxPermSize=512m"

export BUILDVER=$1

if [ -z $BUILDVER ]; then
   BUILDVER=1758
fi

echo "Building with build number $BUILDVER" 

. $SCRIPT_DIR/dal-versions.sh 

$SCRIPT_DIR/falcon-dal.sh

mvn -B -nsu -e\
  -DskipCheck=true \
  -Drepoid=${repo_id} \
  -Drepourl=${nexus_repo_url} \
  -Drepoid=IN_QA \
  -Dreponame=${repo_id} \
  -Phadoop-2 \
  -DskipITs \
  -Ptest-patch \
  clean  \
  install \
  verify  \
  assembly:assembly


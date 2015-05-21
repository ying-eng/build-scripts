#!/bin/bash

export SCRIPT_DIR=$HOME/bin

export MAVEN_OPTS="-Xms3g -Xmx3g -XX:MaxPermSize=512m"

export BUILDVER=$1

if [ -z $BUILDVER ]; then
   BUILDVER=1758
fi

echo "Building with build number $BUILDVER" 

. $SCRIPT_DIR/dal-versions.sh 

$SCRIPT_DIR/oozie-dal.sh

mvn -X -B -e -Dhadoop.version=${hadoop_jar_version} \
-Dhive.version=${hive_jar_version} \
-Dpig.version=${pig_jar_version} \
-Drepoid=${repo_id} \
-Dreponame=${repo_id} \
-Drepourl=${nexus_repo_url} \
-DdistMgmtReleaseUrl=${nexus_repo_url} \
-DmavenReleaseId=${repo_id} \
-DskipTests  \
-Phadoop-2,!hadoop-1\
clean \
install \
assembly:single


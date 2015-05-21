#!/bin/bash


REPLACE="python   ${HOME}/scripts/rewriteXML.py"

$REPLACE  --find pom.xml   -t overwrite  --key+val \
	hbase.version=${hbase_jar_version} \
	hbaselib.version=${hbase_jar_version}.oozie-${oozie_jar_version} \
	hcatalog.version=${hive_jar_version} \
	sqoop.version=${sqoop_jar_version} \
	pig.version=${pig_jar_version} \
	hive.version=${hive_jar_version} \
	tez.version=${tez_jar_version} \
	hadoop.auth.version=${hadoop_jar_version} \
	hadoopTwo.version=${hadoop_jar_version} \
	activeByDefault=false \
	hadoop.version=${hadoop_jar_version}

#
# Omitting for now - the original .sh script doing this, does not do this replace either(!).
#
$REPLACE -C hadooplibs -t overwrite -k version --oldContents hadoop-2-4.2.0 --find pom.xml \
	-v hadoop-2-${oozie_jar_version}


# NO-OP, deactivated by "activeByDefault=false" earlier.

# perl -pi -e 's#\<module\>hadoop.*-1\</module\>#<!-- $& -->#g' ./hadooplibs/pom.xml
# perl -pi -e 's#\<module\>hadoop.*-0.23\</module\>#<!-- $& -->#g' ./hadooplibs/pom.xml
#no-op perl -pi -e 's#\<module\>hcatalog-0.5\</module\>#<!-- $& -->#g' ./hcataloglibs/pom.xml
#no-op perl -pi -e 's#\<module\>hcatalog-0.6\</module\>#<!-- $& -->#g' ./hcataloglibs/pom.xml

echo "Setting new version"

mvn -B -e org.codehaus.mojo:versions-maven-plugin:1.3.1:set -DnewVersion=${oozie_jar_version}

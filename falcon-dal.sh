#!/bin/bash

# Hadoop-2
#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hadoop.profile>[^<]+</<hadoop.profile>${hadoop_profile}</g" {} \;
find . -name 'pom.xml' -type f -exec perl -pi -e "s/<activeByDefault>[^<]+</<activeByDefault>false</g" {} \;
find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hadoop2.version>[^<]+</<hadoop2.version>${hadoop_jar_version}</g" {} \;
find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hadoop.version>[^<]+</<hadoop.version>${hadoop_jar_version}</g" {} \;
find . -name 'pom.xml' -type f -exec perl -pi -e "s/<oozie.version>[^<]+</<oozie.version>${oozie_jar_version}</g" {} \;

find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hive.version>[^<]+</<hive.version>${hive_jar_version}</g" {} \;
find . -name 'pom.xml' -type f -exec perl -pi -e "s/<zookeeper.version>[^<]+</<zookeeper.version>${zookeeper_jar_version}</g" {} \;
find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hcatalog.version>[^<]+</<hcatalog.version>${hcatalog_jar_version}</g" {} \;

#Hadoop-1

#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hadoop.profile>[^<]+</<hadoop.profile>${hadoop_profile}</g" {} \;
#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hadoop1.version>[^<]+</<hadoop1.version>1.2.0.1.3.2.0-111</g" {} \;
#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<oozie.version>[^<]+</<oozie.version>3.3.2.1.3.2.0-111</g" {} \;
#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hive.version>[^<]+</<hive.version>0.11.0.1.3.2.0-111</g" {} \;
#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<zookeeper.version>[^<]+</<zookeeper.version>3.4.5.1.3.2.0-111</g" {} \;
#find . -name 'pom.xml' -type f -exec perl -pi -e "s/<hcatalog.version>[^<]+</<hcatalog.version>0.11.0.1.3.2.0-111</g" {} \;

echo "Setting new version"

mvn -B -e org.codehaus.mojo:versions-maven-plugin:1.3.1:set -DnewVersion=${falcon_jar_version}

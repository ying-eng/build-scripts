build_number=${BUILDVER}

echo "Setting component versions to build $build_number"

export hdp_major_ver=2.3
export hdp_minor_ver=0
export hdp_ebf_ver=0

export hdp_version=${hdp_major_ver}.${hdp_minor_ver}.${hdp_ebf_ver}-${build_number}
export hadoop_jar_version=2.7.1.${hdp_version}
export hadoop_lzo_version=0.6.0.${hdp_version}
export zookeeper_jar_version=3.4.6.${hdp_version}
export hbase_jar_version=1.1.0.${hdp_version}
export #hbase_jar_version=1.1.0.${hdp_version}-hadoop2
export #hbase_jar_version=0.98.4.${hdp_version}-hadoop2
export accumulo_jar_version=1.7.0.${hdp_version}
export tez_jar_version=0.7.0.${hdp_version}
export pig_jar_version=0.15.0.${hdp_version}
export hive_jar_version=1.2.0.${hdp_version}
export hcatalog_jar_version=${hive_jar_version}
export sqoop_jar_version=1.4.6.${hdp_version}
export sqoop2_jar_version=1.99.3.${hdp_version}
export oozie_jar_version=4.2.0.${hdp_version}
export whirr_jar_version=
export mahout_jar_version=0.9.0.${hdp_version}
export flume_jar_version=1.5.2.${hdp_version}
export giraph_jar_version=
export hue_jar_version=2.6.1.${hdp_version}
export datafu_jar_version=
export solr_jar_version=
export crunch_jar_version=
export spark_jar_version=
export phoenix_jar_version=4.0.0.${hdp_version}
export bigtop_utils_jar_version=
export bigtop_jsvc_jar_version=1.0.10
export bigtop_tomcat_jar_version=6.0.37
export falcon_jar_version=0.6.1.${hdp_version}
export knox_jar_version=0.6.0.${hdp_version}
export storm_jar_version=0.9.3.${hdp_version}
export calcite_jar_version=1.0.0.${hdp_version}
export kafka_jar_version=0.8.2.${hdp_version}
export ranger_jar_version=0.8.2.${hdp_version}
export slider_jar_version=0.70.1.${hdp_version}
# Nexus stuff
. ${SCRIPT_DIR}/nexus_info

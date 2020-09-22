-- MariaDB dump 10.17  Distrib 10.5.5-MariaDB, for debian-linux-gnu (x86_64)
--
-- Host: localhost    Database: slurm_acct_db
-- ------------------------------------------------------
-- Server version	10.5.5-MariaDB-1:10.5.5+maria~focal

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `acct_coord_table`
--

DROP TABLE IF EXISTS `acct_coord_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `acct_coord_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `acct` tinytext NOT NULL,
  `user` tinytext NOT NULL,
  PRIMARY KEY (`acct`(42),`user`(42)),
  KEY `user` (`user`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acct_coord_table`
--

LOCK TABLES `acct_coord_table` WRITE;
/*!40000 ALTER TABLE `acct_coord_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `acct_coord_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `acct_table`
--

DROP TABLE IF EXISTS `acct_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `acct_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `name` tinytext NOT NULL,
  `description` text NOT NULL,
  `organization` text NOT NULL,
  PRIMARY KEY (`name`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `acct_table`
--

LOCK TABLES `acct_table` WRITE;
/*!40000 ALTER TABLE `acct_table` DISABLE KEYS */;
INSERT INTO `acct_table` VALUES (1598405566,1598405566,0,'root','default root account','root'),(1598405584,1598405584,0,'test','test','test');
/*!40000 ALTER TABLE `acct_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `clus_res_table`
--

DROP TABLE IF EXISTS `clus_res_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `clus_res_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `cluster` tinytext NOT NULL,
  `res_id` int(11) NOT NULL,
  `percent_allowed` int(10) unsigned DEFAULT 0,
  PRIMARY KEY (`res_id`,`cluster`(42)),
  UNIQUE KEY `udex` (`res_id`,`cluster`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `clus_res_table`
--

LOCK TABLES `clus_res_table` WRITE;
/*!40000 ALTER TABLE `clus_res_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `clus_res_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `cluster_table`
--

DROP TABLE IF EXISTS `cluster_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `cluster_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `name` tinytext NOT NULL,
  `control_host` tinytext NOT NULL DEFAULT '',
  `control_port` int(10) unsigned NOT NULL DEFAULT 0,
  `last_port` int(10) unsigned NOT NULL DEFAULT 0,
  `rpc_version` smallint(5) unsigned NOT NULL DEFAULT 0,
  `classification` smallint(5) unsigned DEFAULT 0,
  `dimensions` smallint(5) unsigned DEFAULT 1,
  `plugin_id_select` smallint(5) unsigned DEFAULT 0,
  `flags` int(10) unsigned DEFAULT 0,
  `federation` tinytext NOT NULL,
  `features` text NOT NULL DEFAULT '',
  `fed_id` int(10) unsigned NOT NULL DEFAULT 0,
  `fed_state` smallint(5) unsigned NOT NULL,
  PRIMARY KEY (`name`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `cluster_table`
--

LOCK TABLES `cluster_table` WRITE;
/*!40000 ALTER TABLE `cluster_table` DISABLE KEYS */;
INSERT INTO `cluster_table` VALUES (1598405578,1598405586,0,'test','192.168.222.4',6817,6817,8704,0,1,101,0,'','',0,0);
/*!40000 ALTER TABLE `cluster_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `convert_version_table`
--

DROP TABLE IF EXISTS `convert_version_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `convert_version_table` (
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `version` int(11) NOT NULL DEFAULT 0,
  PRIMARY KEY (`version`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `convert_version_table`
--

LOCK TABLES `convert_version_table` WRITE;
/*!40000 ALTER TABLE `convert_version_table` DISABLE KEYS */;
INSERT INTO `convert_version_table` VALUES (1598405567,7);
/*!40000 ALTER TABLE `convert_version_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `federation_table`
--

DROP TABLE IF EXISTS `federation_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `federation_table` (
  `creation_time` int(10) unsigned NOT NULL,
  `mod_time` int(10) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `name` tinytext NOT NULL,
  `flags` int(10) unsigned DEFAULT 0,
  PRIMARY KEY (`name`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `federation_table`
--

LOCK TABLES `federation_table` WRITE;
/*!40000 ALTER TABLE `federation_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `federation_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `qos_table`
--

DROP TABLE IF EXISTS `qos_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `qos_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `description` text DEFAULT NULL,
  `flags` int(10) unsigned DEFAULT 0,
  `grace_time` int(10) unsigned DEFAULT NULL,
  `max_jobs_pa` int(11) DEFAULT NULL,
  `max_jobs_per_user` int(11) DEFAULT NULL,
  `max_jobs_accrue_pa` int(11) DEFAULT NULL,
  `max_jobs_accrue_pu` int(11) DEFAULT NULL,
  `min_prio_thresh` int(11) DEFAULT NULL,
  `max_submit_jobs_pa` int(11) DEFAULT NULL,
  `max_submit_jobs_per_user` int(11) DEFAULT NULL,
  `max_tres_pa` text NOT NULL DEFAULT '',
  `max_tres_pj` text NOT NULL DEFAULT '',
  `max_tres_pn` text NOT NULL DEFAULT '',
  `max_tres_pu` text NOT NULL DEFAULT '',
  `max_tres_mins_pj` text NOT NULL DEFAULT '',
  `max_tres_run_mins_pa` text NOT NULL DEFAULT '',
  `max_tres_run_mins_pu` text NOT NULL DEFAULT '',
  `min_tres_pj` text NOT NULL DEFAULT '',
  `max_wall_duration_per_job` int(11) DEFAULT NULL,
  `grp_jobs` int(11) DEFAULT NULL,
  `grp_jobs_accrue` int(11) DEFAULT NULL,
  `grp_submit_jobs` int(11) DEFAULT NULL,
  `grp_tres` text NOT NULL DEFAULT '',
  `grp_tres_mins` text NOT NULL DEFAULT '',
  `grp_tres_run_mins` text NOT NULL DEFAULT '',
  `grp_wall` int(11) DEFAULT NULL,
  `preempt` text NOT NULL DEFAULT '',
  `preempt_mode` int(11) DEFAULT 0,
  `preempt_exempt_time` int(10) unsigned DEFAULT NULL,
  `priority` int(10) unsigned DEFAULT 0,
  `usage_factor` double NOT NULL DEFAULT 1,
  `usage_thres` double DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `udex` (`name`(42))
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `qos_table`
--

LOCK TABLES `qos_table` WRITE;
/*!40000 ALTER TABLE `qos_table` DISABLE KEYS */;
INSERT INTO `qos_table` VALUES (1598405566,1598405566,0,1,'normal','Normal QOS default',0,NULL,NULL,NULL,NULL,NULL,NULL,NULL,NULL,'','','','','','','','',NULL,NULL,NULL,NULL,'','','',NULL,'',0,NULL,0,1,NULL);
/*!40000 ALTER TABLE `qos_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `res_table`
--

DROP TABLE IF EXISTS `res_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `res_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` tinytext NOT NULL,
  `description` text DEFAULT NULL,
  `manager` tinytext NOT NULL,
  `server` tinytext NOT NULL,
  `count` int(10) unsigned DEFAULT 0,
  `type` int(10) unsigned DEFAULT 0,
  `flags` int(10) unsigned DEFAULT 0,
  PRIMARY KEY (`id`),
  UNIQUE KEY `udex` (`name`(42),`server`(42),`type`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `res_table`
--

LOCK TABLES `res_table` WRITE;
/*!40000 ALTER TABLE `res_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `res_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `table_defs_table`
--

DROP TABLE IF EXISTS `table_defs_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `table_defs_table` (
  `creation_time` int(10) unsigned NOT NULL,
  `mod_time` int(10) unsigned NOT NULL DEFAULT 0,
  `table_name` text NOT NULL,
  `definition` text NOT NULL,
  PRIMARY KEY (`table_name`(50))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `table_defs_table`
--

LOCK TABLES `table_defs_table` WRITE;
/*!40000 ALTER TABLE `table_defs_table` DISABLE KEYS */;
INSERT INTO `table_defs_table` VALUES (1598405579,1598405579,'\"test_assoc_table\"','alter table \"test_assoc_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `is_def` tinyint default 0 not null, modify `id_assoc` int unsigned not null auto_increment, modify `user` tinytext not null default \'\', modify `acct` tinytext not null, modify `partition` tinytext not null default \'\', modify `parent_acct` tinytext not null default \'\', modify `lft` int not null, modify `rgt` int not null, modify `shares` int default 1 not null, modify `max_jobs` int default NULL, modify `max_jobs_accrue` int default NULL, modify `min_prio_thresh` int default NULL, modify `max_submit_jobs` int default NULL, modify `max_tres_pj` text not null default \'\', modify `max_tres_pn` text not null default \'\', modify `max_tres_mins_pj` text not null default \'\', modify `max_tres_run_mins` text not null default \'\', modify `max_wall_pj` int default NULL, modify `grp_jobs` int default NULL, modify `grp_jobs_accrue` int default NULL, modify `grp_submit_jobs` int default NULL, modify `grp_tres` text not null default \'\', modify `grp_tres_mins` text not null default \'\', modify `grp_tres_run_mins` text not null default \'\', modify `grp_wall` int default NULL, modify `priority` int unsigned default NULL, modify `def_qos_id` int default NULL, modify `qos` blob not null default \'\', modify `delta_qos` blob not null default \'\', drop primary key, add primary key (id_assoc), drop index udex, add unique index udex (user(42), acct(42), `partition`(42)), drop key lft, add key lft (lft), drop key account, add key account (acct(42));'),(1598405579,1598405579,'\"test_assoc_usage_day_table\"','alter table \"test_assoc_usage_day_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id` int unsigned not null, modify `id_tres` int default 1 not null, modify `time_start` bigint unsigned not null, modify `alloc_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id, id_tres, time_start);'),(1598405579,1598405579,'\"test_assoc_usage_hour_table\"','alter table \"test_assoc_usage_hour_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id` int unsigned not null, modify `id_tres` int default 1 not null, modify `time_start` bigint unsigned not null, modify `alloc_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id, id_tres, time_start);'),(1598405579,1598405579,'\"test_assoc_usage_month_table\"','alter table \"test_assoc_usage_month_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id` int unsigned not null, modify `id_tres` int default 1 not null, modify `time_start` bigint unsigned not null, modify `alloc_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id, id_tres, time_start);'),(1598405579,1598405579,'\"test_event_table\"','alter table \"test_event_table\" modify `time_start` bigint unsigned not null, modify `time_end` bigint unsigned default 0 not null, modify `node_name` tinytext default \'\' not null, modify `cluster_nodes` text not null default \'\', modify `reason` tinytext not null, modify `reason_uid` int unsigned default 0xfffffffe not null, modify `state` int unsigned default 0 not null, modify `tres` text not null default \'\', drop primary key, add primary key (node_name(42), time_start);'),(1598405579,1598405579,'\"test_job_table\"','alter table \"test_job_table\" modify `job_db_inx` bigint unsigned not null auto_increment, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `account` tinytext, modify `admin_comment` text, modify `array_task_str` text, modify `array_max_tasks` int unsigned default 0 not null, modify `array_task_pending` int unsigned default 0 not null, modify `constraints` text default \'\', modify `cpus_req` int unsigned not null, modify `derived_ec` int unsigned default 0 not null, modify `derived_es` text, modify `exit_code` int unsigned default 0 not null, modify `flags` int unsigned default 0 not null, modify `job_name` tinytext not null, modify `id_assoc` int unsigned not null, modify `id_array_job` int unsigned default 0 not null, modify `id_array_task` int unsigned default 0xfffffffe not null, modify `id_block` tinytext, modify `id_job` int unsigned not null, modify `id_qos` int unsigned default 0 not null, modify `id_resv` int unsigned not null, modify `id_wckey` int unsigned not null, modify `id_user` int unsigned not null, modify `id_group` int unsigned not null, modify `pack_job_id` int unsigned not null, modify `pack_job_offset` int unsigned not null, modify `kill_requid` int default -1 not null, modify `state_reason_prev` int unsigned not null, modify `mcs_label` tinytext default \'\', modify `mem_req` bigint unsigned default 0 not null, modify `nodelist` text, modify `nodes_alloc` int unsigned not null, modify `node_inx` text, modify `partition` tinytext not null, modify `priority` int unsigned not null, modify `state` int unsigned not null, modify `timelimit` int unsigned default 0 not null, modify `time_submit` bigint unsigned default 0 not null, modify `time_eligible` bigint unsigned default 0 not null, modify `time_start` bigint unsigned default 0 not null, modify `time_end` bigint unsigned default 0 not null, modify `time_suspended` bigint unsigned default 0 not null, modify `gres_req` text not null default \'\', modify `gres_alloc` text not null default \'\', modify `gres_used` text not null default \'\', modify `wckey` tinytext not null default \'\', modify `work_dir` text not null default \'\', modify `system_comment` text, modify `track_steps` tinyint not null, modify `tres_alloc` text not null default \'\', modify `tres_req` text not null default \'\', drop primary key, add primary key (job_db_inx), drop index id_job, add unique index (id_job, time_submit), drop key old_tuple, add key old_tuple (id_job, id_assoc, time_submit), drop key rollup, add key rollup (time_eligible, time_end), drop key rollup2, add key rollup2 (time_end, time_eligible), drop key nodes_alloc, add key nodes_alloc (nodes_alloc), drop key wckey, add key wckey (id_wckey), drop key qos, add key qos (id_qos), drop key association, add key association (id_assoc), drop key array_job, add key array_job (id_array_job), drop key pack_job, add key pack_job (pack_job_id), drop key reserv, add key reserv (id_resv), drop key sacct_def, add key sacct_def (id_user, time_start, time_end), drop key sacct_def2, add key sacct_def2 (id_user, time_end, time_eligible);'),(1598405579,1598405579,'\"test_last_ran_table\"','alter table \"test_last_ran_table\" modify `hourly_rollup` bigint unsigned default 0 not null, modify `daily_rollup` bigint unsigned default 0 not null, modify `monthly_rollup` bigint unsigned default 0 not null, drop primary key, add primary key (hourly_rollup, daily_rollup, monthly_rollup);'),(1598405579,1598405579,'\"test_resv_table\"','alter table \"test_resv_table\" modify `id_resv` int unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `assoclist` text not null default \'\', modify `flags` bigint unsigned default 0 not null, modify `nodelist` text not null default \'\', modify `node_inx` text not null default \'\', modify `resv_name` text not null, modify `time_start` bigint unsigned default 0 not null, modify `time_end` bigint unsigned default 0 not null, modify `tres` text not null default \'\', modify `unused_wall` double unsigned default 0.0 not null, drop primary key, add primary key (id_resv, time_start);'),(1598405580,1598405580,'\"test_step_table\"','alter table \"test_step_table\" modify `job_db_inx` bigint unsigned not null, modify `deleted` tinyint default 0 not null, modify `exit_code` int default 0 not null, modify `id_step` int not null, modify `kill_requid` int default -1 not null, modify `nodelist` text not null, modify `nodes_alloc` int unsigned not null, modify `node_inx` text, modify `state` smallint unsigned not null, modify `step_name` text not null, modify `task_cnt` int unsigned not null, modify `task_dist` smallint default 0 not null, modify `time_start` bigint unsigned default 0 not null, modify `time_end` bigint unsigned default 0 not null, modify `time_suspended` bigint unsigned default 0 not null, modify `user_sec` int unsigned default 0 not null, modify `user_usec` int unsigned default 0 not null, modify `sys_sec` int unsigned default 0 not null, modify `sys_usec` int unsigned default 0 not null, modify `act_cpufreq` double unsigned default 0.0 not null, modify `consumed_energy` bigint unsigned default 0 not null, modify `req_cpufreq_min` int unsigned default 0 not null, modify `req_cpufreq` int unsigned default 0 not null, modify `req_cpufreq_gov` int unsigned default 0 not null, modify `tres_alloc` text not null default \'\', modify `tres_usage_in_ave` text not null default \'\', modify `tres_usage_in_max` text not null default \'\', modify `tres_usage_in_max_taskid` text not null default \'\', modify `tres_usage_in_max_nodeid` text not null default \'\', modify `tres_usage_in_min` text not null default \'\', modify `tres_usage_in_min_taskid` text not null default \'\', modify `tres_usage_in_min_nodeid` text not null default \'\', modify `tres_usage_in_tot` text not null default \'\', modify `tres_usage_out_ave` text not null default \'\', modify `tres_usage_out_max` text not null default \'\', modify `tres_usage_out_max_taskid` text not null default \'\', modify `tres_usage_out_max_nodeid` text not null default \'\', modify `tres_usage_out_min` text not null default \'\', modify `tres_usage_out_min_taskid` text not null default \'\', modify `tres_usage_out_min_nodeid` text not null default \'\', modify `tres_usage_out_tot` text not null default \'\', drop primary key, add primary key (job_db_inx, id_step);'),(1598405580,1598405580,'\"test_suspend_table\"','alter table \"test_suspend_table\" modify `job_db_inx` bigint unsigned not null, modify `id_assoc` int not null, modify `time_start` bigint unsigned default 0 not null, modify `time_end` bigint unsigned default 0 not null, drop primary key, add primary key (job_db_inx, time_start), drop key job_db_inx_times, add key job_db_inx_times (job_db_inx, time_start, time_end);'),(1598405579,1598405579,'\"test_usage_day_table\"','alter table \"test_usage_day_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id_tres` int not null, modify `time_start` bigint unsigned not null, modify `count` bigint unsigned default 0 not null, modify `alloc_secs` bigint unsigned default 0 not null, modify `down_secs` bigint unsigned default 0 not null, modify `pdown_secs` bigint unsigned default 0 not null, modify `idle_secs` bigint unsigned default 0 not null, modify `resv_secs` bigint unsigned default 0 not null, modify `over_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id_tres, time_start);'),(1598405579,1598405579,'\"test_usage_hour_table\"','alter table \"test_usage_hour_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id_tres` int not null, modify `time_start` bigint unsigned not null, modify `count` bigint unsigned default 0 not null, modify `alloc_secs` bigint unsigned default 0 not null, modify `down_secs` bigint unsigned default 0 not null, modify `pdown_secs` bigint unsigned default 0 not null, modify `idle_secs` bigint unsigned default 0 not null, modify `resv_secs` bigint unsigned default 0 not null, modify `over_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id_tres, time_start);'),(1598405579,1598405579,'\"test_usage_month_table\"','alter table \"test_usage_month_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id_tres` int not null, modify `time_start` bigint unsigned not null, modify `count` bigint unsigned default 0 not null, modify `alloc_secs` bigint unsigned default 0 not null, modify `down_secs` bigint unsigned default 0 not null, modify `pdown_secs` bigint unsigned default 0 not null, modify `idle_secs` bigint unsigned default 0 not null, modify `resv_secs` bigint unsigned default 0 not null, modify `over_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id_tres, time_start);'),(1598405580,1598405580,'\"test_wckey_table\"','alter table \"test_wckey_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `is_def` tinyint default 0 not null, modify `id_wckey` int unsigned not null auto_increment, modify `wckey_name` tinytext not null default \'\', modify `user` tinytext not null, drop primary key, add primary key (id_wckey), drop index udex, add unique index udex (wckey_name(42), user(42));'),(1598405580,1598405580,'\"test_wckey_usage_day_table\"','alter table \"test_wckey_usage_day_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id` int unsigned not null, modify `id_tres` int default 1 not null, modify `time_start` bigint unsigned not null, modify `alloc_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id, id_tres, time_start);'),(1598405580,1598405580,'\"test_wckey_usage_hour_table\"','alter table \"test_wckey_usage_hour_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id` int unsigned not null, modify `id_tres` int default 1 not null, modify `time_start` bigint unsigned not null, modify `alloc_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id, id_tres, time_start);'),(1598405580,1598405580,'\"test_wckey_usage_month_table\"','alter table \"test_wckey_usage_month_table\" modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0 not null, modify `id` int unsigned not null, modify `id_tres` int default 1 not null, modify `time_start` bigint unsigned not null, modify `alloc_secs` bigint unsigned default 0 not null, drop primary key, add primary key (id, id_tres, time_start);'),(1598405567,1598405567,'acct_coord_table','alter table acct_coord_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `acct` tinytext not null, modify `user` tinytext not null, drop primary key, add primary key (acct(42), user(42)), drop key user, add key user (user(42));'),(1598405567,1598405567,'acct_table','alter table acct_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `name` tinytext not null, modify `description` text not null, modify `organization` text not null, drop primary key, add primary key (name(42));'),(1598405567,1598405567,'cluster_table','alter table cluster_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `name` tinytext not null, modify `control_host` tinytext not null default \'\', modify `control_port` int unsigned not null default 0, modify `last_port` int unsigned not null default 0, modify `rpc_version` smallint unsigned not null default 0, modify `classification` smallint unsigned default 0, modify `dimensions` smallint unsigned default 1, modify `plugin_id_select` smallint unsigned default 0, modify `flags` int unsigned default 0, modify `federation` tinytext not null, modify `features` text not null default \'\', modify `fed_id` int unsigned default 0 not null, modify `fed_state` smallint unsigned not null, drop primary key, add primary key (name(42));'),(1598405567,1598405567,'clus_res_table','alter table clus_res_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `cluster` tinytext not null, modify `res_id` int not null, modify `percent_allowed` int unsigned default 0, drop primary key, add primary key (res_id, cluster(42)), drop index udex, add unique index udex (res_id, cluster(42));'),(1598405566,1598405566,'convert_version_table','alter table convert_version_table modify `mod_time` bigint unsigned default 0 not null, modify `version` int default 0, drop primary key, add primary key (version);'),(1598405567,1598405567,'federation_table','alter table federation_table modify `creation_time` int unsigned not null, modify `mod_time` int unsigned default 0 not null, modify `deleted` tinyint default 0, modify `name` tinytext not null, modify `flags` int unsigned default 0, drop primary key, add primary key (name(42));'),(1598405567,1598405567,'qos_table','alter table qos_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `id` int not null auto_increment, modify `name` tinytext not null, modify `description` text, modify `flags` int unsigned default 0, modify `grace_time` int unsigned default NULL, modify `max_jobs_pa` int default NULL, modify `max_jobs_per_user` int default NULL, modify `max_jobs_accrue_pa` int default NULL, modify `max_jobs_accrue_pu` int default NULL, modify `min_prio_thresh` int default NULL, modify `max_submit_jobs_pa` int default NULL, modify `max_submit_jobs_per_user` int default NULL, modify `max_tres_pa` text not null default \'\', modify `max_tres_pj` text not null default \'\', modify `max_tres_pn` text not null default \'\', modify `max_tres_pu` text not null default \'\', modify `max_tres_mins_pj` text not null default \'\', modify `max_tres_run_mins_pa` text not null default \'\', modify `max_tres_run_mins_pu` text not null default \'\', modify `min_tres_pj` text not null default \'\', modify `max_wall_duration_per_job` int default NULL, modify `grp_jobs` int default NULL, modify `grp_jobs_accrue` int default NULL, modify `grp_submit_jobs` int default NULL, modify `grp_tres` text not null default \'\', modify `grp_tres_mins` text not null default \'\', modify `grp_tres_run_mins` text not null default \'\', modify `grp_wall` int default NULL, modify `preempt` text not null default \'\', modify `preempt_mode` int default 0, modify `preempt_exempt_time` int unsigned default NULL, modify `priority` int unsigned default 0, modify `usage_factor` double default 1.0 not null, modify `usage_thres` double default NULL, drop primary key, add primary key (id), drop index udex, add unique index udex (name(42));'),(1598405567,1598405567,'res_table','alter table res_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `id` int not null auto_increment, modify `name` tinytext not null, modify `description` text default null, modify `manager` tinytext not null, modify `server` tinytext not null, modify `count` int unsigned default 0, modify `type` int unsigned default 0, modify `flags` int unsigned default 0, drop primary key, add primary key (id), drop index udex, add unique index udex (name(42), server(42), type);'),(1598405567,1598405567,'tres_table','alter table tres_table modify `creation_time` bigint unsigned not null, modify `deleted` tinyint default 0 not null, modify `id` int not null auto_increment, modify `type` tinytext not null, modify `name` tinytext not null default \'\', drop primary key, add primary key (id), drop index udex, add unique index udex (type(42), name(42));'),(1598405567,1598405567,'txn_table','alter table txn_table modify `id` int not null auto_increment, modify `timestamp` bigint unsigned default 0 not null, modify `action` smallint not null, modify `name` text not null, modify `actor` tinytext not null, modify `cluster` tinytext not null default \'\', modify `info` blob, drop primary key, add primary key (id);'),(1598405567,1598405567,'user_table','alter table user_table modify `creation_time` bigint unsigned not null, modify `mod_time` bigint unsigned default 0 not null, modify `deleted` tinyint default 0, modify `name` tinytext not null, modify `admin_level` smallint default 1 not null, drop primary key, add primary key (name(42));');
/*!40000 ALTER TABLE `table_defs_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_assoc_table`
--

DROP TABLE IF EXISTS `test_assoc_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_assoc_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `is_def` tinyint(4) NOT NULL DEFAULT 0,
  `id_assoc` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `user` tinytext NOT NULL DEFAULT '',
  `acct` tinytext NOT NULL,
  `partition` tinytext NOT NULL DEFAULT '',
  `parent_acct` tinytext NOT NULL DEFAULT '',
  `lft` int(11) NOT NULL,
  `rgt` int(11) NOT NULL,
  `shares` int(11) NOT NULL DEFAULT 1,
  `max_jobs` int(11) DEFAULT NULL,
  `max_jobs_accrue` int(11) DEFAULT NULL,
  `min_prio_thresh` int(11) DEFAULT NULL,
  `max_submit_jobs` int(11) DEFAULT NULL,
  `max_tres_pj` text NOT NULL DEFAULT '',
  `max_tres_pn` text NOT NULL DEFAULT '',
  `max_tres_mins_pj` text NOT NULL DEFAULT '',
  `max_tres_run_mins` text NOT NULL DEFAULT '',
  `max_wall_pj` int(11) DEFAULT NULL,
  `grp_jobs` int(11) DEFAULT NULL,
  `grp_jobs_accrue` int(11) DEFAULT NULL,
  `grp_submit_jobs` int(11) DEFAULT NULL,
  `grp_tres` text NOT NULL DEFAULT '',
  `grp_tres_mins` text NOT NULL DEFAULT '',
  `grp_tres_run_mins` text NOT NULL DEFAULT '',
  `grp_wall` int(11) DEFAULT NULL,
  `priority` int(10) unsigned DEFAULT NULL,
  `def_qos_id` int(11) DEFAULT NULL,
  `qos` blob NOT NULL DEFAULT '',
  `delta_qos` blob NOT NULL DEFAULT '',
  PRIMARY KEY (`id_assoc`),
  UNIQUE KEY `udex` (`user`(42),`acct`(42),`partition`(42)),
  KEY `lft` (`lft`),
  KEY `account` (`acct`(42))
) ENGINE=InnoDB AUTO_INCREMENT=4 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_assoc_table`
--

LOCK TABLES `test_assoc_table` WRITE;
/*!40000 ALTER TABLE `test_assoc_table` DISABLE KEYS */;
INSERT INTO `test_assoc_table` VALUES (1598405578,1598405578,0,0,1,'','root','','',1,6,1,NULL,NULL,NULL,NULL,'','','','',NULL,NULL,NULL,NULL,'','','',NULL,NULL,NULL,',1,',''),(1598405580,1598405580,0,1,2,'root','root','','',4,5,1,NULL,NULL,NULL,NULL,'','','','',NULL,NULL,NULL,NULL,'','','',NULL,NULL,NULL,'',''),(1598405584,1598405584,0,0,3,'','test','','root',2,3,1,NULL,NULL,NULL,NULL,'','','','',NULL,NULL,NULL,NULL,'','','',NULL,NULL,NULL,'','');
/*!40000 ALTER TABLE `test_assoc_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_assoc_usage_day_table`
--

DROP TABLE IF EXISTS `test_assoc_usage_day_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_assoc_usage_day_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(10) unsigned NOT NULL,
  `id_tres` int(11) NOT NULL DEFAULT 1,
  `time_start` bigint(20) unsigned NOT NULL,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_assoc_usage_day_table`
--

LOCK TABLES `test_assoc_usage_day_table` WRITE;
/*!40000 ALTER TABLE `test_assoc_usage_day_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_assoc_usage_day_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_assoc_usage_hour_table`
--

DROP TABLE IF EXISTS `test_assoc_usage_hour_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_assoc_usage_hour_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(10) unsigned NOT NULL,
  `id_tres` int(11) NOT NULL DEFAULT 1,
  `time_start` bigint(20) unsigned NOT NULL,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_assoc_usage_hour_table`
--

LOCK TABLES `test_assoc_usage_hour_table` WRITE;
/*!40000 ALTER TABLE `test_assoc_usage_hour_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_assoc_usage_hour_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_assoc_usage_month_table`
--

DROP TABLE IF EXISTS `test_assoc_usage_month_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_assoc_usage_month_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(10) unsigned NOT NULL,
  `id_tres` int(11) NOT NULL DEFAULT 1,
  `time_start` bigint(20) unsigned NOT NULL,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_assoc_usage_month_table`
--

LOCK TABLES `test_assoc_usage_month_table` WRITE;
/*!40000 ALTER TABLE `test_assoc_usage_month_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_assoc_usage_month_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_event_table`
--

DROP TABLE IF EXISTS `test_event_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_event_table` (
  `time_start` bigint(20) unsigned NOT NULL,
  `time_end` bigint(20) unsigned NOT NULL DEFAULT 0,
  `node_name` tinytext NOT NULL DEFAULT '',
  `cluster_nodes` text NOT NULL DEFAULT '',
  `reason` tinytext NOT NULL,
  `reason_uid` int(10) unsigned NOT NULL DEFAULT 4294967294,
  `state` int(10) unsigned NOT NULL DEFAULT 0,
  `tres` text NOT NULL DEFAULT '',
  PRIMARY KEY (`node_name`(42),`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_event_table`
--

LOCK TABLES `test_event_table` WRITE;
/*!40000 ALTER TABLE `test_event_table` DISABLE KEYS */;
INSERT INTO `test_event_table` VALUES (1598405586,0,'','c[1-2]','Cluster Registered TRES',4294967294,0,'1=2,2=2000,3=0,4=2,5=2,6=0,7=0,8=0');
/*!40000 ALTER TABLE `test_event_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_job_table`
--

DROP TABLE IF EXISTS `test_job_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_job_table` (
  `job_db_inx` bigint(20) unsigned NOT NULL AUTO_INCREMENT,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `account` tinytext DEFAULT NULL,
  `admin_comment` text DEFAULT NULL,
  `array_task_str` text DEFAULT NULL,
  `array_max_tasks` int(10) unsigned NOT NULL DEFAULT 0,
  `array_task_pending` int(10) unsigned NOT NULL DEFAULT 0,
  `constraints` text DEFAULT '',
  `cpus_req` int(10) unsigned NOT NULL,
  `derived_ec` int(10) unsigned NOT NULL DEFAULT 0,
  `derived_es` text DEFAULT NULL,
  `exit_code` int(10) unsigned NOT NULL DEFAULT 0,
  `flags` int(10) unsigned NOT NULL DEFAULT 0,
  `job_name` tinytext NOT NULL,
  `id_assoc` int(10) unsigned NOT NULL,
  `id_array_job` int(10) unsigned NOT NULL DEFAULT 0,
  `id_array_task` int(10) unsigned NOT NULL DEFAULT 4294967294,
  `id_block` tinytext DEFAULT NULL,
  `id_job` int(10) unsigned NOT NULL,
  `id_qos` int(10) unsigned NOT NULL DEFAULT 0,
  `id_resv` int(10) unsigned NOT NULL,
  `id_wckey` int(10) unsigned NOT NULL,
  `id_user` int(10) unsigned NOT NULL,
  `id_group` int(10) unsigned NOT NULL,
  `pack_job_id` int(10) unsigned NOT NULL,
  `pack_job_offset` int(10) unsigned NOT NULL,
  `kill_requid` int(11) NOT NULL DEFAULT -1,
  `state_reason_prev` int(10) unsigned NOT NULL,
  `mcs_label` tinytext DEFAULT '',
  `mem_req` bigint(20) unsigned NOT NULL DEFAULT 0,
  `nodelist` text DEFAULT NULL,
  `nodes_alloc` int(10) unsigned NOT NULL,
  `node_inx` text DEFAULT NULL,
  `partition` tinytext NOT NULL,
  `priority` int(10) unsigned NOT NULL,
  `state` int(10) unsigned NOT NULL,
  `timelimit` int(10) unsigned NOT NULL DEFAULT 0,
  `time_submit` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_eligible` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_start` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_end` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_suspended` bigint(20) unsigned NOT NULL DEFAULT 0,
  `gres_req` text NOT NULL DEFAULT '',
  `gres_alloc` text NOT NULL DEFAULT '',
  `gres_used` text NOT NULL DEFAULT '',
  `wckey` tinytext NOT NULL DEFAULT '',
  `work_dir` text NOT NULL DEFAULT '',
  `system_comment` text DEFAULT NULL,
  `track_steps` tinyint(4) NOT NULL,
  `tres_alloc` text NOT NULL DEFAULT '',
  `tres_req` text NOT NULL DEFAULT '',
  PRIMARY KEY (`job_db_inx`),
  UNIQUE KEY `id_job` (`id_job`,`time_submit`),
  KEY `old_tuple` (`id_job`,`id_assoc`,`time_submit`),
  KEY `rollup` (`time_eligible`,`time_end`),
  KEY `rollup2` (`time_end`,`time_eligible`),
  KEY `nodes_alloc` (`nodes_alloc`),
  KEY `wckey` (`id_wckey`),
  KEY `qos` (`id_qos`),
  KEY `association` (`id_assoc`),
  KEY `array_job` (`id_array_job`),
  KEY `pack_job` (`pack_job_id`),
  KEY `reserv` (`id_resv`),
  KEY `sacct_def` (`id_user`,`time_start`,`time_end`),
  KEY `sacct_def2` (`id_user`,`time_end`,`time_eligible`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_job_table`
--

LOCK TABLES `test_job_table` WRITE;
/*!40000 ALTER TABLE `test_job_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_job_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_last_ran_table`
--

DROP TABLE IF EXISTS `test_last_ran_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_last_ran_table` (
  `hourly_rollup` bigint(20) unsigned NOT NULL DEFAULT 0,
  `daily_rollup` bigint(20) unsigned NOT NULL DEFAULT 0,
  `monthly_rollup` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`hourly_rollup`,`daily_rollup`,`monthly_rollup`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_last_ran_table`
--

LOCK TABLES `test_last_ran_table` WRITE;
/*!40000 ALTER TABLE `test_last_ran_table` DISABLE KEYS */;
INSERT INTO `test_last_ran_table` VALUES (1598405584,1598405584,1598405584);
/*!40000 ALTER TABLE `test_last_ran_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_resv_table`
--

DROP TABLE IF EXISTS `test_resv_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_resv_table` (
  `id_resv` int(10) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `assoclist` text NOT NULL DEFAULT '',
  `flags` bigint(20) unsigned NOT NULL DEFAULT 0,
  `nodelist` text NOT NULL DEFAULT '',
  `node_inx` text NOT NULL DEFAULT '',
  `resv_name` text NOT NULL,
  `time_start` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_end` bigint(20) unsigned NOT NULL DEFAULT 0,
  `tres` text NOT NULL DEFAULT '',
  `unused_wall` double unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_resv`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_resv_table`
--

LOCK TABLES `test_resv_table` WRITE;
/*!40000 ALTER TABLE `test_resv_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_resv_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_step_table`
--

DROP TABLE IF EXISTS `test_step_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_step_table` (
  `job_db_inx` bigint(20) unsigned NOT NULL,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `exit_code` int(11) NOT NULL DEFAULT 0,
  `id_step` int(11) NOT NULL,
  `kill_requid` int(11) NOT NULL DEFAULT -1,
  `nodelist` text NOT NULL,
  `nodes_alloc` int(10) unsigned NOT NULL,
  `node_inx` text DEFAULT NULL,
  `state` smallint(5) unsigned NOT NULL,
  `step_name` text NOT NULL,
  `task_cnt` int(10) unsigned NOT NULL,
  `task_dist` smallint(6) NOT NULL DEFAULT 0,
  `time_start` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_end` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_suspended` bigint(20) unsigned NOT NULL DEFAULT 0,
  `user_sec` int(10) unsigned NOT NULL DEFAULT 0,
  `user_usec` int(10) unsigned NOT NULL DEFAULT 0,
  `sys_sec` int(10) unsigned NOT NULL DEFAULT 0,
  `sys_usec` int(10) unsigned NOT NULL DEFAULT 0,
  `act_cpufreq` double unsigned NOT NULL DEFAULT 0,
  `consumed_energy` bigint(20) unsigned NOT NULL DEFAULT 0,
  `req_cpufreq_min` int(10) unsigned NOT NULL DEFAULT 0,
  `req_cpufreq` int(10) unsigned NOT NULL DEFAULT 0,
  `req_cpufreq_gov` int(10) unsigned NOT NULL DEFAULT 0,
  `tres_alloc` text NOT NULL DEFAULT '',
  `tres_usage_in_ave` text NOT NULL DEFAULT '',
  `tres_usage_in_max` text NOT NULL DEFAULT '',
  `tres_usage_in_max_taskid` text NOT NULL DEFAULT '',
  `tres_usage_in_max_nodeid` text NOT NULL DEFAULT '',
  `tres_usage_in_min` text NOT NULL DEFAULT '',
  `tres_usage_in_min_taskid` text NOT NULL DEFAULT '',
  `tres_usage_in_min_nodeid` text NOT NULL DEFAULT '',
  `tres_usage_in_tot` text NOT NULL DEFAULT '',
  `tres_usage_out_ave` text NOT NULL DEFAULT '',
  `tres_usage_out_max` text NOT NULL DEFAULT '',
  `tres_usage_out_max_taskid` text NOT NULL DEFAULT '',
  `tres_usage_out_max_nodeid` text NOT NULL DEFAULT '',
  `tres_usage_out_min` text NOT NULL DEFAULT '',
  `tres_usage_out_min_taskid` text NOT NULL DEFAULT '',
  `tres_usage_out_min_nodeid` text NOT NULL DEFAULT '',
  `tres_usage_out_tot` text NOT NULL DEFAULT '',
  PRIMARY KEY (`job_db_inx`,`id_step`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_step_table`
--

LOCK TABLES `test_step_table` WRITE;
/*!40000 ALTER TABLE `test_step_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_step_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_suspend_table`
--

DROP TABLE IF EXISTS `test_suspend_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_suspend_table` (
  `job_db_inx` bigint(20) unsigned NOT NULL,
  `id_assoc` int(11) NOT NULL,
  `time_start` bigint(20) unsigned NOT NULL DEFAULT 0,
  `time_end` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`job_db_inx`,`time_start`),
  KEY `job_db_inx_times` (`job_db_inx`,`time_start`,`time_end`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_suspend_table`
--

LOCK TABLES `test_suspend_table` WRITE;
/*!40000 ALTER TABLE `test_suspend_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_suspend_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_usage_day_table`
--

DROP TABLE IF EXISTS `test_usage_day_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_usage_day_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id_tres` int(11) NOT NULL,
  `time_start` bigint(20) unsigned NOT NULL,
  `count` bigint(20) unsigned NOT NULL DEFAULT 0,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `down_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `pdown_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `idle_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `resv_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `over_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_usage_day_table`
--

LOCK TABLES `test_usage_day_table` WRITE;
/*!40000 ALTER TABLE `test_usage_day_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_usage_day_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_usage_hour_table`
--

DROP TABLE IF EXISTS `test_usage_hour_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_usage_hour_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id_tres` int(11) NOT NULL,
  `time_start` bigint(20) unsigned NOT NULL,
  `count` bigint(20) unsigned NOT NULL DEFAULT 0,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `down_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `pdown_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `idle_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `resv_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `over_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_usage_hour_table`
--

LOCK TABLES `test_usage_hour_table` WRITE;
/*!40000 ALTER TABLE `test_usage_hour_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_usage_hour_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_usage_month_table`
--

DROP TABLE IF EXISTS `test_usage_month_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_usage_month_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id_tres` int(11) NOT NULL,
  `time_start` bigint(20) unsigned NOT NULL,
  `count` bigint(20) unsigned NOT NULL DEFAULT 0,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `down_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `pdown_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `idle_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `resv_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  `over_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_usage_month_table`
--

LOCK TABLES `test_usage_month_table` WRITE;
/*!40000 ALTER TABLE `test_usage_month_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_usage_month_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_wckey_table`
--

DROP TABLE IF EXISTS `test_wckey_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_wckey_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `is_def` tinyint(4) NOT NULL DEFAULT 0,
  `id_wckey` int(10) unsigned NOT NULL AUTO_INCREMENT,
  `wckey_name` tinytext NOT NULL DEFAULT '',
  `user` tinytext NOT NULL,
  PRIMARY KEY (`id_wckey`),
  UNIQUE KEY `udex` (`wckey_name`(42),`user`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_wckey_table`
--

LOCK TABLES `test_wckey_table` WRITE;
/*!40000 ALTER TABLE `test_wckey_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_wckey_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_wckey_usage_day_table`
--

DROP TABLE IF EXISTS `test_wckey_usage_day_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_wckey_usage_day_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(10) unsigned NOT NULL,
  `id_tres` int(11) NOT NULL DEFAULT 1,
  `time_start` bigint(20) unsigned NOT NULL,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_wckey_usage_day_table`
--

LOCK TABLES `test_wckey_usage_day_table` WRITE;
/*!40000 ALTER TABLE `test_wckey_usage_day_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_wckey_usage_day_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_wckey_usage_hour_table`
--

DROP TABLE IF EXISTS `test_wckey_usage_hour_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_wckey_usage_hour_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(10) unsigned NOT NULL,
  `id_tres` int(11) NOT NULL DEFAULT 1,
  `time_start` bigint(20) unsigned NOT NULL,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_wckey_usage_hour_table`
--

LOCK TABLES `test_wckey_usage_hour_table` WRITE;
/*!40000 ALTER TABLE `test_wckey_usage_hour_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_wckey_usage_hour_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `test_wckey_usage_month_table`
--

DROP TABLE IF EXISTS `test_wckey_usage_month_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `test_wckey_usage_month_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(10) unsigned NOT NULL,
  `id_tres` int(11) NOT NULL DEFAULT 1,
  `time_start` bigint(20) unsigned NOT NULL,
  `alloc_secs` bigint(20) unsigned NOT NULL DEFAULT 0,
  PRIMARY KEY (`id`,`id_tres`,`time_start`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `test_wckey_usage_month_table`
--

LOCK TABLES `test_wckey_usage_month_table` WRITE;
/*!40000 ALTER TABLE `test_wckey_usage_month_table` DISABLE KEYS */;
/*!40000 ALTER TABLE `test_wckey_usage_month_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `tres_table`
--

DROP TABLE IF EXISTS `tres_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `tres_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `deleted` tinyint(4) NOT NULL DEFAULT 0,
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `type` tinytext NOT NULL,
  `name` tinytext NOT NULL DEFAULT '',
  PRIMARY KEY (`id`),
  UNIQUE KEY `udex` (`type`(42),`name`(42))
) ENGINE=InnoDB AUTO_INCREMENT=1001 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `tres_table`
--

LOCK TABLES `tres_table` WRITE;
/*!40000 ALTER TABLE `tres_table` DISABLE KEYS */;
INSERT INTO `tres_table` VALUES (1598405566,0,1,'cpu',''),(1598405566,0,2,'mem',''),(1598405566,0,3,'energy',''),(1598405566,0,4,'node',''),(1598405566,0,5,'billing',''),(1598405566,0,6,'fs','disk'),(1598405566,0,7,'vmem',''),(1598405566,0,8,'pages',''),(1598405566,1,1000,'dynamic_offset','');
/*!40000 ALTER TABLE `tres_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `txn_table`
--

DROP TABLE IF EXISTS `txn_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `txn_table` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `timestamp` bigint(20) unsigned NOT NULL DEFAULT 0,
  `action` smallint(6) NOT NULL,
  `name` text NOT NULL,
  `actor` tinytext NOT NULL,
  `cluster` tinytext NOT NULL DEFAULT '',
  `info` blob DEFAULT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=6 DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `txn_table`
--

LOCK TABLES `txn_table` WRITE;
/*!40000 ALTER TABLE `txn_table` DISABLE KEYS */;
INSERT INTO `txn_table` VALUES (1,1598405578,1405,'test','root','','mod_time=1598405578, shares=1, grp_jobs=NULL, grp_jobs_accrue=NULL, grp_submit_jobs=NULL, grp_wall=NULL, max_jobs=NULL, max_jobs_accrue=NULL, min_prio_thresh=NULL, max_submit_jobs=NULL, max_wall_pj=NULL, priority=NULL, def_qos_id=NULL, qos=\',1,\', federation=\'\', fed_id=0, fed_state=0, features=\'\''),(2,1598405580,1404,'id_assoc=2','root','test','mod_time=1598405580, acct=\'root\', user=\'root\', `partition`=\'\', shares=1, grp_jobs=NULL, grp_jobs_accrue=NULL, grp_submit_jobs=NULL, grp_wall=NULL, is_def=1, max_jobs=NULL, max_jobs_accrue=NULL, min_prio_thresh=NULL, max_submit_jobs=NULL, max_wall_pj=NULL, priority=NULL, def_qos_id=NULL, qos=\'\', delta_qos=\'\''),(3,1598405584,1402,'test','root','','description=\'test\', organization=\'test\''),(4,1598405584,1404,'id_assoc=3','root','test','mod_time=1598405584, acct=\'test\', parent_acct=\'root\', user=\'\', shares=1, grp_jobs=NULL, grp_jobs_accrue=NULL, grp_submit_jobs=NULL, grp_wall=NULL, max_jobs=NULL, max_jobs_accrue=NULL, min_prio_thresh=NULL, max_submit_jobs=NULL, max_wall_pj=NULL, priority=NULL, def_qos_id=NULL, qos=\'\', delta_qos=\'\''),(5,1598405586,1430,'name=\'test\'','slurm','','control_host=\'192.168.222.4\', control_port=6817, last_port=6817, rpc_version=8704, dimensions=1, plugin_id_select=101, flags=0');
/*!40000 ALTER TABLE `txn_table` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `user_table`
--

DROP TABLE IF EXISTS `user_table`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `user_table` (
  `creation_time` bigint(20) unsigned NOT NULL,
  `mod_time` bigint(20) unsigned NOT NULL DEFAULT 0,
  `deleted` tinyint(4) DEFAULT 0,
  `name` tinytext NOT NULL,
  `admin_level` smallint(6) NOT NULL DEFAULT 1,
  PRIMARY KEY (`name`(42))
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `user_table`
--

LOCK TABLES `user_table` WRITE;
/*!40000 ALTER TABLE `user_table` DISABLE KEYS */;
INSERT INTO `user_table` VALUES (1598405566,1598405566,0,'root',3);
/*!40000 ALTER TABLE `user_table` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2020-08-26  1:33:24

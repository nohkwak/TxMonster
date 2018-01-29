DROP DATABASE IF EXISTS TxMonDB;
CREATE DATABASE TxMonDB;
use TxMonDB;

CREATE TABLE dpr_lists (
    ID                    int NOT NULL AUTO_INCREMENT,
    addr                   varchar(256)  NOT NULL ,
    depth                  varchar(32)   NOT NULL ,
    CONSTRAINT pk_dpr_lists PRIMARY KEY ( ID, addr )
) engine=InnoDB;

CREATE TABLE dpr_user_lists (
    ID                    int NOT NULL AUTO_INCREMENT,
    addr                   varchar(256)  NOT NULL ,
    depth                  varchar(32)   NOT NULL ,
/*    ntx_range              varchar(32)   NOT NULL ,
    origin                 varchar(256)  NOT NULL , */
    CONSTRAINT pk_dpr_user_lists PRIMARY KEY ( ID, addr )
) engine=InnoDB;

CREATE TABLE dpr_user_txs (
    ID                    int NOT NULL AUTO_INCREMENT,
    sender                   varchar(256)  NOT NULL ,
    receiver                 varchar(256)  NOT NULL ,
    tx_time                 DATETIME NOT NULL ,
    tx_month                varchar(12)   NOT NULL ,
    BTC                     FLOAT(64,8) NOT NULL,
    typo                    varchar(10) NOT NULL,
    CONSTRAINT pk_dpr_user_txs PRIMARY KEY ( ID, sender, receiver, tx_time, typo )
) engine=InnoDB;




CREATE TABLE white_lists (
    ID                    int NOT NULL AUTO_INCREMENT,
    addr                   varchar(256)  NOT NULL ,
    depth                  varchar(32)   NOT NULL ,
    CONSTRAINT pk_white_lists PRIMARY KEY ( ID, addr )
) engine=InnoDB;


CREATE TABLE black_lists (
    ID                    int NOT NULL AUTO_INCREMENT,
    addr                   varchar(256)  NOT NULL ,
    depth                  varchar(32)   NOT NULL ,
/*    ntx_range              varchar(32)   NOT NULL ,
    origin                 varchar(256)  NOT NULL , */
    CONSTRAINT pk_black_lists PRIMARY KEY ( ID, addr )
) engine=InnoDB;

CREATE TABLE alarm_lists (
    ID                    int NOT NULL AUTO_INCREMENT,
    input              varchar(256)  NOT NULL ,
    output             varchar(256)  NOT NULL ,
    CONSTRAINT pk_alarm_lists PRIMARY KEY ( ID, input )
) engine=InnoDB;

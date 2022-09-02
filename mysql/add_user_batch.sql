DELIMITER $$

USE `test`$$

DROP PROCEDURE IF EXISTS `add_user_batch`$$

CREATE DEFINER=`root`@`%` PROCEDURE `add_user_batch`(IN COUNT INT)
BEGIN
    DECLARE i INT;
    DECLARE t_name VARCHAR(8);
    DECLARE t_tag VARCHAR(20);
    DECLARE t_age INT(2);
    DECLARE t_sql_template VARCHAR(100);
    DECLARE t_sql TEXT;   
    DECLARE t_tag_mod_val INT DEFAULT(25);
    DECLARE t_commit_mod_val INT DEFAULT(100);
    
    DECLARE t_start_time DATETIME;
    DECLARE t_end_time DATETIME;    
    
    TRUNCATE TABLE `system_user`;
    
    SET t_start_time=NOW();
    SET t_sql_template = "INSERT INTO `system_user`(NAME, age, tag) VALUES";
    SET t_sql = t_sql_template;
    SET i = 1;
    WHILE i <= COUNT
        DO
            SET t_age = FLOOR(1 + RAND() * 60);
            SET t_name = LEFT(UUID(), 8);
            -- 给tag随机制造空值
            IF MOD(i, t_tag_mod_val) = 0 THEN
                SET t_tag = "NULL";
            ELSE
                SET t_tag = CONCAT("'",LEFT(UUID(), 8),"'");
            END IF;
 
            SET t_sql = CONCAT(t_sql,"('",t_name,"',",t_age,",",t_tag,")");
            
            IF MOD(i,t_commit_mod_val) != 0 THEN
              SET t_sql = CONCAT(t_sql,",");
            ELSE
              SET t_sql = CONCAT(t_sql,";");
                   -- 只要达到t_commit_mod_val要求的次数，就执行并提交
                   SET @insert_sql = t_sql;
                   PREPARE stmt FROM @insert_sql;
                   EXECUTE stmt;
                   DEALLOCATE PREPARE stmt;
                   COMMIT;
              SET t_sql=t_sql_template;
            END IF;
            SET i = i + 1;
        END WHILE;
        
        -- 不能被t_commit_mod_val整除时，余下的数据处理
        IF LENGTH(t_sql) > LENGTH(t_sql_template) THEN
                   SET t_sql=CONCAT(SUBSTRING(t_sql,1,LENGTH(t_sql)-1),';');
                   SET @insert_sql = t_sql;
                   PREPARE stmt FROM @insert_sql;
                   EXECUTE stmt;
                   DEALLOCATE PREPARE stmt;
                   COMMIT;
        END IF;
        SET t_end_time=NOW();
        SELECT CONCAT('insert data success,time cost ',TIMEDIFF(t_end_time,t_start_time)) AS finishedTag;
END$$

DELIMITER ;